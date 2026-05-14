# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from datetime import datetime
# import uuid
# from ..database import get_db
# from ..schemas.sensor import ChatRequest, ChatResponse
# from ..crud import sensor as crud
# from ..services.llm_agent import get_agricultural_advice

# router = APIRouter(prefix="/chat", tags=["AI Agricultural Advisor"])

# @router.post("/", response_model=ChatResponse)
# def chat_with_advisor(request: ChatRequest, db: Session = Depends(get_db)):
#     """
#     Chat with Dr. AgriBot - AI Agricultural Advisor
    
#     The AI analyzes your soil sensor data and provides expert recommendations on:
#     - Fertilizer types and dosages
#     - Irrigation schedules
#     - Soil pH management
#     - Crop-specific nutrient advice
#     """
    
#     # Generate session ID if not provided
#     session_id = request.session_id or str(uuid.uuid4())
    
#     # Get latest sensor data if requested
#     sensor_data = {}
#     if request.include_sensor_data:
#         latest_reading = crud.get_latest_reading(db)
#         if latest_reading:
#             sensor_data = {
#                 "nitrogen": latest_reading.nitrogen,
#                 "phosphorus": latest_reading.phosphorus,
#                 "potassium": latest_reading.potassium,
#                 "ph": latest_reading.ph,
#                 "temperature": latest_reading.temperature,
#                 "humidity": latest_reading.humidity,
#                 "ec": latest_reading.ec
#             }
#         else:
#             raise HTTPException(
#                 status_code=404,
#                 detail="No sensor data available. Please ensure ESP32 is sending data."
#             )
    
#     # Get land size or default to 1 acre
#     land_size = request.land_size_acres or 1.0
    
#     # Get AI advice
#     result = get_agricultural_advice(
#         user_message=request.message,
#         sensor_data=sensor_data,
#         land_size=land_size,
#         session_id=session_id
#     )
    
#     return ChatResponse(
#         response=result["response"],
#         session_id=result["session_id"],
#         sensor_data_used=result.get("sensor_data_used"),
#         timestamp=datetime.utcnow()
#     )

# @router.delete("/session/{session_id}")
# def clear_chat_history(session_id: str):
#     """Clear chat history for a specific session"""
#     # LangGraph's SqliteSaver handles this automatically
#     return {"message": f"Session {session_id} history will be managed by checkpointer"}





from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from schemas.sensor import ChatRequest, ChatResponse
from services.llm_agent import get_agricultural_advice
from crud.sensor import get_latest_reading
import uuid

router = APIRouter(prefix="/chat", tags=["AI Agricultural Advisor"])


@router.post("/", response_model=ChatResponse)
def chat_with_advisor(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Chat with AI Agricultural Advisor
    
    **Smart Defaults:**
    - Only `message` is required
    - `session_id` → auto-generated if not provided
    - `land_size_acres` → defaults to 1.0 acre
    - `include_sensor_data` → defaults to True (uses latest sensor readings)
    
    **Examples:**
    
    Minimal request (just message):
    ```json
    {
      "message": "What fertilizer do I need?"
    }
    ```
    
    With custom land size:
    ```json
    {
      "message": "کس کھاد کی ضرورت ہے؟",
      "land_size_acres": 3.5
    }
    ```
    
    Without sensor data:
    ```json
    {
      "message": "What is Urea fertilizer?",
      "include_sensor_data": false
    }
    ```
    """
    
    # Auto-generate session_id if not provided
    if not request.session_id:
        request.session_id = str(uuid.uuid4())
    
    # Get sensor data
    sensor_data = None
    
    if request.include_sensor_data:
        latest_reading = get_latest_reading(db)
        
        if latest_reading:
            sensor_data = {
                "nitrogen": latest_reading.nitrogen,
                "phosphorus": latest_reading.phosphorus,
                "potassium": latest_reading.potassium,
                "ph": latest_reading.ph,
                "temperature": latest_reading.temperature,
                "humidity": latest_reading.humidity,
                "ec": latest_reading.ec
            }
            print(f"📊 Using sensor data for chat: N={latest_reading.nitrogen}, P={latest_reading.phosphorus}, K={latest_reading.potassium}")
        else:
            # Use default values if no sensor data available
            sensor_data = {
                "nitrogen": 200,
                "phosphorus": 20,
                "potassium": 150,
                "ph": 6.5,
                "temperature": 25,
                "humidity": 50,
                "ec": 1000
            }
            print("⚠️ No sensor data found, using default values")
    
    # Call AI service
    try:
        result = get_agricultural_advice(
            user_message=request.message,
            sensor_data=sensor_data,
            land_size=request.land_size_acres,
            session_id=request.session_id
        )
        
        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            sensor_data_used=sensor_data,
            timestamp=datetime.now().isoformat(),  # ✅ Convert to string with .isoformat()
            recommendations=result.get("recommendations")
        )
    
    except Exception as e:
        print(f"❌ AI Service Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )
