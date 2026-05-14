from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String

from database import Base


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    maps_url = Column(String, unique=True, nullable=False, index=True)
    address = Column(String, nullable=True)
    parking_difficulty = Column(String, nullable=False)  # "easy" | "hard"
    days_closed = Column(String, default="")  # comma-separated: "Saturday,Sunday"
    budget_min = Column(Integer, nullable=False)
    budget_max = Column(Integer, nullable=False)
    has_epp = Column(Boolean, default=False)
    submitted_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    country = Column(String, nullable=True)
    shop_images = Column(JSON, default=list, nullable=True)
    menu_images = Column(JSON, default=list, nullable=True)
