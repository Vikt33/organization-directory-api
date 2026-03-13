from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from math import radians, sin, cos, sqrt, atan2

from app import models, schemas
from app.database import get_db
from app.dependencies import verify_api_key

router = APIRouter(prefix="/organizations", tags=["organizations"], dependencies=[Depends(verify_api_key)])

# Вспомогательная функция для получения организации с полными данными
def get_organization_with_details(db: Session, org_id: int):
    return db.query(models.Organization).options(
        joinedload(models.Organization.phone_numbers),
        joinedload(models.Organization.activities),
        joinedload(models.Organization.building)
    ).filter(models.Organization.id == org_id).first()

# Получение организации по ID
@router.get("/{org_id}", response_model=schemas.Organization)
def get_organization(org_id: int, db: Session = Depends(get_db)):
    org = get_organization_with_details(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

# Поиск по названию (частичное совпадение, регистронезависимое)
@router.get("/search/", response_model=List[schemas.OrganizationShort])
def search_organizations(name: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    orgs = db.query(models.Organization).filter(
        models.Organization.name.ilike(f"%{name}%")
    ).options(
        joinedload(models.Organization.phone_numbers),
        joinedload(models.Organization.activities)
    ).all()
    result = []
    for org in orgs:
        result.append(schemas.OrganizationShort(
            id=org.id,
            name=org.name,
            building_id=org.building_id,
            phone_numbers=[pn.number for pn in org.phone_numbers],
            activity_names=[act.name for act in org.activities]
        ))
    return result

# Организации в радиусе от точки (в километрах)
@router.get("/nearby/", response_model=List[schemas.OrganizationShort])
def get_organizations_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius: float = Query(..., gt=0, description="Radius in km"),
    db: Session = Depends(get_db)
):
    # Получаем все здания в радиусе (приближённо через ограничение по координатам)
    # Для упрощения используем эвристику: 1 градус широты ~ 111 км, долготы ~ 111 * cos(lat)
    lat_deg_km = 111.0
    lon_deg_km = 111.0 * abs(cos(radians(lat)))
    lat_diff = radius / lat_deg_km
    lon_diff = radius / lon_deg_km

    buildings = db.query(models.Building).filter(
        models.Building.latitude.between(lat - lat_diff, lat + lat_diff),
        models.Building.longitude.between(lon - lon_diff, lon + lon_diff)
    ).all()

    # Точная фильтрация по формуле гаверсинуса
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # радиус Земли в км
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    orgs = []
    for b in buildings:
        if haversine(lat, lon, b.latitude, b.longitude) <= radius:
            for org in b.organizations:
                orgs.append(org)

    # Подгружаем телефоны и деятельности
    db.query(models.Organization).filter(models.Organization.id.in_([o.id for o in orgs])).options(
        joinedload(models.Organization.phone_numbers),
        joinedload(models.Organization.activities)
    ).all()

    result = []
    for org in orgs:
        result.append(schemas.OrganizationShort(
            id=org.id,
            name=org.name,
            building_id=org.building_id,
            phone_numbers=[pn.number for pn in org.phone_numbers],
            activity_names=[act.name for act in org.activities]
        ))
    return result

# Организации по виду деятельности с учётом поддеятельностей (до 3 уровня)
@router.get("/by_activity_tree/{activity_id}", response_model=List[schemas.OrganizationShort])
def get_organizations_by_activity_tree(activity_id: int, db: Session = Depends(get_db)):
    # Получаем все дочерние ID до глубины 3
    activity_ids = {activity_id}
    current_level = db.query(models.Activity).filter(models.Activity.parent_id == activity_id).all()
    for _ in range(2):  # ещё два уровня
        if not current_level:
            break
        next_level = []
        for act in current_level:
            activity_ids.add(act.id)
            children = db.query(models.Activity).filter(models.Activity.parent_id == act.id).all()
            next_level.extend(children)
        current_level = next_level
    # Добавляем конечный уровень
    for act in current_level:
        activity_ids.add(act.id)

    # Ищем организации, у которых есть хотя бы одна деятельность из списка
    orgs = db.query(models.Organization).join(models.organization_activity).filter(
        models.organization_activity.c.activity_id.in_(activity_ids)
    ).distinct().options(
        joinedload(models.Organization.phone_numbers),
        joinedload(models.Organization.activities)
    ).all()

    result = []
    for org in orgs:
        result.append(schemas.OrganizationShort(
            id=org.id,
            name=org.name,
            building_id=org.building_id,
            phone_numbers=[pn.number for pn in org.phone_numbers],
            activity_names=[act.name for act in org.activities]
        ))
    return result