from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import SensorReading  # ✅ Fixed import
from schemas.sensor import SensorReadingCreate


def create_sensor_reading(db: Session, reading: SensorReadingCreate):
    """Create a new sensor reading"""
    db_reading = SensorReading(**reading.model_dump())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    print(f"✅ New reading saved: ID={db_reading.id}, N={db_reading.nitrogen}, P={db_reading.phosphorus}, K={db_reading.potassium}")
    return db_reading


def get_latest_reading(db: Session):
    """Get the most recent sensor reading"""
    reading = db.query(SensorReading).order_by(desc(SensorReading.timestamp)).first()
    if reading:
        print(f"📊 Latest reading: ID={reading.id}, Time={reading.timestamp}, N={reading.nitrogen}")
    return reading


def get_reading_history(db: Session, limit: int = 20):
    """Get recent sensor readings for historical analysis"""
    return db.query(SensorReading).order_by(desc(SensorReading.timestamp)).limit(limit).all()
