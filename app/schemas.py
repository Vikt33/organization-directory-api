from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# Building
class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float

class BuildingCreate(BuildingBase):
    pass

class Building(BuildingBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Activity
class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int
    children: List['Activity'] = []
    model_config = ConfigDict(from_attributes=True)

# PhoneNumber
class PhoneNumberBase(BaseModel):
    number: str

class PhoneNumberCreate(PhoneNumberBase):
    pass

class PhoneNumber(PhoneNumberBase):
    id: int
    organization_id: int
    model_config = ConfigDict(from_attributes=True)

# Organization
class OrganizationBase(BaseModel):
    name: str
    building_id: int

class OrganizationCreate(OrganizationBase):
    phone_numbers: List[str]
    activity_ids: List[int]

class Organization(OrganizationBase):
    id: int
    phone_numbers: List[PhoneNumber] = []
    activities: List[Activity] = []
    building: Building
    model_config = ConfigDict(from_attributes=True)

# Для ответов с краткой информацией (без вложенных объектов)
class OrganizationShort(BaseModel):
    id: int
    name: str
    building_id: int
    phone_numbers: List[str]
    activity_names: List[str]
    model_config = ConfigDict(from_attributes=True)