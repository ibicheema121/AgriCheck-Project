import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import sensor, chat, voice 
from routers.public_chat import router as public_chat_router
from routers.crop_recommendation import router as crop_recommendation_router
from config import CORS_ORIGINS


# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="AgriCheck IoT Backend",
    description="API for ESP32 7-in-1 Soil Sensor Data with AI Agricultural Advisor",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include existing routers
app.include_router(sensor.router)
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(crop_recommendation_router)

# Include public chat router (Dashboard LLM Button)
app.include_router(public_chat_router)


# Health check endpoint
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "healthy",
        "message": "AgriCheck IoT Backend API with AI Advisor",
        "version": "2.0.0",
        "features": [
            "Real-time soil monitoring",
            "AI agricultural recommendations",
            "Persistent chat memory",
            "Fertilizer dosage calculator",
            "Voice-to-Voice AI Advisor (WebSocket)"  # ✅ NEW
        ]
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
