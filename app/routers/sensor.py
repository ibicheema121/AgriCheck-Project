from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.sensor import SensorReadingCreate, SensorReadingResponse
from crud import sensor as crud

router = APIRouter(prefix="/readings", tags=["Sensor Readings"])

@router.post("/", response_model=SensorReadingResponse, status_code=201)
def create_reading(reading: SensorReadingCreate, db: Session = Depends(get_db)):
    """
    Create a new sensor reading from ESP32
    """
    return crud.create_sensor_reading(db=db, reading=reading)

@router.get("/latest", response_model=SensorReadingResponse)
def get_latest(db: Session = Depends(get_db)):
    """
    Get the most recent sensor reading
    """
    reading = crud.get_latest_reading(db=db)
    if not reading:
        raise HTTPException(status_code=404, detail="No readings found")
    return reading

@router.get("/history", response_model=List[SensorReadingResponse])
def get_history(limit: int = 20, db: Session = Depends(get_db)):
    """
    Get historical sensor readings (default: last 20)
    """
    return crud.get_reading_history(db=db, limit=limit)
