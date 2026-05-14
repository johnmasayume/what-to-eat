from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


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
    notes: Optional[str] = None
    country: Optional[str] = None
    shop_images: list[str] = []
    menu_images: list[str] = []


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
    notes: Optional[str] = None
    country: Optional[str] = None
    shop_images: list[str] = []
    menu_images: list[str] = []

    model_config = {"from_attributes": True}

    @field_validator("shop_images", "menu_images", mode="before")
    @classmethod
    def ensure_list(cls, v):
        return v if isinstance(v, list) else []


class PlaceUpdate(BaseModel):
    name: Optional[str] = None
    maps_url: Optional[str] = None
    address: Optional[str] = None
    parking_difficulty: Optional[str] = None
    days_closed: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    has_epp: Optional[bool] = None
    submitted_by: Optional[str] = None
    notes: Optional[str] = None
    country: Optional[str] = None
    shop_images: Optional[list[str]] = None
    menu_images: Optional[list[str]] = None


class LookupOut(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    is_duplicate: bool = False
