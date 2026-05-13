import random
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Place
from schemas import LookupOut, PlaceCreate, PlaceOut, PlaceUpdate
from services.place_lookup import lookup_place

router = APIRouter(prefix="/api/places", tags=["places"])


def today_name() -> str:
    return datetime.now().strftime("%A")


def is_open(place: Place) -> bool:
    if not place.days_closed:
        return True
    return today_name() not in [d.strip() for d in place.days_closed.split(",")]


@router.get("/", response_model=list[PlaceOut])
def list_places(db: Session = Depends(get_db)):
    return db.query(Place).order_by(Place.created_at.desc()).all()


@router.get("/today", response_model=list[PlaceOut])
def list_today(db: Session = Depends(get_db)):
    return [p for p in db.query(Place).all() if is_open(p)]


@router.get("/recommend", response_model=Optional[PlaceOut])
def recommend(db: Session = Depends(get_db)):
    open_places = [p for p in db.query(Place).all() if is_open(p)]
    return random.choice(open_places) if open_places else None


@router.get("/lookup", response_model=LookupOut)
async def lookup(maps_url: str = Query(...), db: Session = Depends(get_db)):
    if db.query(Place).filter(Place.maps_url == maps_url).first():
        return LookupOut(is_duplicate=True)
    info = await lookup_place(maps_url)
    return LookupOut(**info)


@router.post("/", response_model=PlaceOut, status_code=201)
def create_place(body: PlaceCreate, db: Session = Depends(get_db)):
    if db.query(Place).filter(Place.maps_url == body.maps_url).first():
        raise HTTPException(status_code=409, detail="Place already exists")
    place = Place(**body.model_dump())
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


@router.put("/{place_id}", response_model=PlaceOut)
def update_place(place_id: int, body: PlaceUpdate, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Not found")
    if body.maps_url and body.maps_url != place.maps_url:
        conflict = db.query(Place).filter(Place.maps_url == body.maps_url, Place.id != place_id).first()
        if conflict:
            raise HTTPException(status_code=409, detail="Another place with this Maps URL already exists")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(place, field, value)
    db.commit()
    db.refresh(place)
    return place


@router.delete("/{place_id}", status_code=204)
def delete_place(place_id: int, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(place)
    db.commit()
