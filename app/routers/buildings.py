from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.dependencies import verify_api_key

router = APIRouter(prefix="/buildings", tags=["buildings"], dependencies=[Depends(verify_api_key)])

# Список зданий в прямоугольной области (bbox)
@router.get("/in_bbox/", response_model=List[schemas.Building])
def get_buildings_in_bbox(
    min_lat: float = Query(..., ge=-90, le=90),
    min_lon: float = Query(..., ge=-180, le=180),
    max_lat: float = Query(..., ge=-90, le=90),
    max_lon: float = Query(..., ge=-180, le=180),
    db: Session = Depends(get_db)
):
    if min_lat > max_lat or min_lon > max_lon:
        raise HTTPException(status_code=400, detail="Invalid bbox coordinates")
    buildings = db.query(models.Building).filter(
        models.Building.latitude.between(min_lat, max_lat),
        models.Building.longitude.between(min_lon, max_lon)
    ).all()
    return buildings

# Организации в конкретном здании
@router.get("/{building_id}/organizations/", response_model=List[schemas.OrganizationShort])
def get_organizations_in_building(building_id: int, db: Session = Depends(get_db)):
    building = db.query(models.Building).filter(models.Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    orgs = building.organizations
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