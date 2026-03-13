from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app import models, schemas
from app.database import get_db
from app.dependencies import verify_api_key

router = APIRouter(prefix="/activities", tags=["activities"], dependencies=[Depends(verify_api_key)])

# Получить дерево деятельности (опционально)
@router.get("/tree/", response_model=List[schemas.Activity])
def get_activity_tree(db: Session = Depends(get_db)):
    # Загружаем все деятельности с parent_id
    activities = db.query(models.Activity).options(joinedload(models.Activity.children)).all()
    # Строим дерево: корневые элементы (parent_id is None)
    activity_map = {act.id: act for act in activities}
    roots = []
    for act in activities:
        if act.parent_id is None:
            roots.append(act)
        else:
            parent = activity_map.get(act.parent_id)
            if parent:
                if not hasattr(parent, 'children_list'):
                    parent.children_list = []
                parent.children_list.append(act)
    # Преобразуем в схему с детьми (рекурсивно)
    def build_tree(act):
        act_schema = schemas.Activity.model_validate(act)
        if hasattr(act, 'children_list'):
            act_schema.children = [build_tree(child) for child in act.children_list]
        return act_schema
    return [build_tree(root) for root in roots]

# Организации по конкретному виду деятельности (без поддеятельностей)
@router.get("/{activity_id}/organizations/", response_model=List[schemas.OrganizationShort])
def get_organizations_by_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    orgs = activity.organizations
    # Подгружаем телефоны
    db.query(models.Organization).filter(models.Organization.id.in_([o.id for o in orgs])).options(
        joinedload(models.Organization.phone_numbers)
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