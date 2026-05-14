from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Sensor Reading Schemas (NO CHANGES - KEEP AS IS)
class SensorReadingCreate(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    temperature: float
    humidity: float
    ec: float


class SensorReadingResponse(BaseModel):
    id: int
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    temperature: float
    humidity: float
    ec: float
    timestamp: datetime

    class Config:
        from_attributes = True


# ✅ CHANGE THIS SECTION ONLY - Chat Schemas
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Your farming question (REQUIRED)")
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID (auto-generated if not provided)"
    )
    land_size_acres: Optional[float] = Field(
        default=1.0,
        ge=0.1,
        le=1000,
        description="Farm size in acres (default: 1.0)"
    )
    include_sensor_data: Optional[bool] = Field(
        default=True,
        description="Include latest sensor readings (default: true)"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "message": "What fertilizer should I use?"
                },
                {
                    "message": "کس کھاد کی ضرورت ہے؟",
                    "land_size_acres": 2.5
                },
                {
                    "message": "Is my soil good?",
                    "include_sensor_data": True
                }
            ]
        }


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sensor_data_used: Optional[dict] = None
    timestamp: str
    recommendations: Optional[dict] = None