from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PlaceCreate(BaseModel):
    name: str
    maps_url: str
    address: Optional[str] = None
    parking_difficulty: str
    days_closed: str = ""
    budget_min: int
    budget_max: int
    has_epp: bool = False
    submitted_by: str


class PlaceOut(BaseModel):
    id: int
    name: str
    maps_url: str
    address: Optional[str]
    parking_difficulty: str
    days_closed: str
    budget_min: int
    budget_max: int
    has_epp: bool
    submitted_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LookupOut(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    is_duplicate: bool = False
