from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, crud, schemas, weather, models
import asyncio


router = APIRouter(tags=["temperatures"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.Temperature])
def list(city_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_temperatures(db, city_id)

@router.post("/update")
async def update_temperatures(db: Session = Depends(get_db)):
    cities = crud.get_cities(db)
    results = []

    async def process_city(city):
        temp = await weather.get_weather_data(city.name)
        return crud.create_temperature(db, schemas.TemperatureCreate(
            city_id=city.id,
            temperature=temp
        ))

    results = await asyncio.gather(*[process_city(city) for city in cities])
    return results