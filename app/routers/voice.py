# from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, Depends
# from fastapi.responses import StreamingResponse, FileResponse
# from pydantic import BaseModel
# from typing import Optional
# from sqlalchemy.orm import Session
# import io
# import json
# import asyncio
# import traceback
# import uuid
# import base64

# from ..services.voice_service import voice_service
# from ..services.voice_engine import create_voice_engine
# from ..services.llm_agent import get_agricultural_advice
# from ..crud.sensor import get_latest_reading
# from ..database import get_db

# router = APIRouter(prefix="/voice", tags=["Voice Services"])


# @router.websocket("/ws/voice-advisor")
# async def voice_advisor_websocket(websocket: WebSocket):
#     """
#     Real-time Voice-to-Voice AI Advisor WebSocket

#     Protocol:
#     1. Client sends: Raw audio chunks (16kHz, 16-bit, mono PCM)
#     2. Client sends: JSON { type: "audio_playback_ended" } when TTS audio finishes playing
#     3. Server sends: JSON status messages + Audio response chunks
#     4. Server sends: { type: "mute_mic" } before TTS, waits for client to unmute after playback
#     """

#     await websocket.accept()

#     voice_engine = create_voice_engine()

#     from ..database import SessionLocal
#     db = SessionLocal()

#     session_id = None
#     land_size = 1.0
#     is_connected = True

#     loop = asyncio.get_running_loop()

#     print("🔌 WebSocket connected: voice-advisor")

#     try:
#         await websocket.send_json({
#             "type": "status",
#             "message": "Connected to AI Voice Advisor. Start speaking..."
#         })

#         # ============================================================
#         # Async handler that runs ON the event loop
#         # ============================================================
#         async def handle_recognized_speech(text: str, language: str):
#             nonlocal session_id

#             if not is_connected:
#                 return

#             try:
#                 # Send transcription to client
#                 await websocket.send_json({
#                     "type": "transcription",
#                     "text": text,
#                     "language": language
#                 })

#                 # Get latest sensor data
#                 latest_reading = get_latest_reading(db)

#                 if latest_reading:
#                     sensor_data = {
#                         "nitrogen": latest_reading.nitrogen,
#                         "phosphorus": latest_reading.phosphorus,
#                         "potassium": latest_reading.potassium,
#                         "ph": latest_reading.ph,
#                         "temperature": latest_reading.temperature,
#                         "humidity": latest_reading.humidity,
#                         "ec": latest_reading.ec
#                     }
#                     print(f"📊 Using sensor data: N={latest_reading.nitrogen}, P={latest_reading.phosphorus}, K={latest_reading.potassium}")
#                 else:
#                     sensor_data = {
#                         "nitrogen": 200, "phosphorus": 20, "potassium": 150,
#                         "ph": 6.5, "temperature": 25, "humidity": 50, "ec": 1000
#                     }
#                     print("⚠️ Using default sensor values")

#                 if not session_id:
#                     session_id = str(uuid.uuid4())

#                 ai_result = get_agricultural_advice(
#                     user_message=text,
#                     sensor_data=sensor_data,
#                     land_size=land_size,
#                     session_id=session_id
#                 )

#                 ai_response = ai_result["response"]

#                 # Send AI text response
#                 await websocket.send_json({
#                     "type": "ai_response",
#                     "text": ai_response
#                 })

#                 print(f"🤖 AI Response ({language}): {ai_response[:100]}...")

#                 # MUTE mic on server side before TTS
#                 voice_engine.mute()

#                 # Tell client to mute mic
#                 if is_connected:
#                     await websocket.send_json({"type": "mute_mic"})

#                 # Convert AI response to speech and stream
#                 async for audio_chunk in voice_engine.text_to_speech_stream(ai_response, language):
#                     if not is_connected:
#                         break

#                     audio_b64 = base64.b64encode(audio_chunk).decode('utf-8')
#                     await websocket.send_json({
#                         "type": "audio_chunk",
#                         "data": audio_b64
#                     })

#                 # Tell client all audio chunks sent — client will play and then send "audio_playback_ended"
#                 if is_connected:
#                     await websocket.send_json({"type": "completed"})

#                 print("✅ Audio chunks streamed, waiting for client playback to finish")

#             except WebSocketDisconnect:
#                 print("🔌 Client disconnected during response")
#             except Exception as e:
#                 error_str = str(e)
#                 if "disconnect" in error_str.lower() or "closed" in error_str.lower():
#                     print("🔌 Client disconnected during response")
#                     return

#                 print(f"❌ Error handling speech: {error_str}")
#                 print(traceback.format_exc())

#                 # Unmute on error so mic doesn't stay stuck
#                 voice_engine.unmute()

#                 if is_connected:
#                     try:
#                         await websocket.send_json({
#                             "type": "error",
#                             "message": f"Error processing request: {error_str}"
#                         })
#                         await websocket.send_json({"type": "unmute_mic"})
#                     except:
#                         pass

#         # ============================================================
#         # Async error sender
#         # ============================================================
#         async def send_error_message(error: str):
#             try:
#                 if is_connected:
#                     await websocket.send_json({
#                         "type": "error",
#                         "message": f"Speech recognition error: {error}. Please check your microphone."
#                     })
#             except:
#                 pass

#         # ============================================================
#         # Thread-safe callbacks (called from Azure SDK threads)
#         # ============================================================
#         def on_speech_recognized(text: str, language: str):
#             if is_connected:
#                 asyncio.run_coroutine_threadsafe(
#                     handle_recognized_speech(text, language), loop
#                 )

#         def on_recognition_error(error_details: str):
#             print(f"❌ Recognition error: {error_details}")
#             if is_connected:
#                 asyncio.run_coroutine_threadsafe(
#                     send_error_message(error_details), loop
#                 )

#         # Start continuous recognition
#         voice_engine.start_continuous_recognition(
#             on_recognized_callback=on_speech_recognized,
#             on_error_callback=on_recognition_error
#         )

#         # Main loop - receive audio chunks from client
#         while is_connected:
#             try:
#                 message = await asyncio.wait_for(websocket.receive(), timeout=30.0)

#                 if "bytes" in message:
#                     audio_chunk = message["bytes"]
#                     voice_engine.write_audio_chunk(audio_chunk)

#                 elif "text" in message:
#                     data = json.loads(message["text"])

#                     if data.get("type") == "config":
#                         land_size = data.get("land_size_acres", 1.0)
#                         print(f"⚙️ Updated land size: {land_size} acres")

#                     elif data.get("type") == "reset":
#                         session_id = None
#                         print("🔄 Session reset")

#                         if is_connected:
#                             await websocket.send_json({
#                                 "type": "status",
#                                 "message": "Session reset. Start speaking..."
#                             })

#                     elif data.get("type") == "ping":
#                         if is_connected:
#                             await websocket.send_json({"type": "pong"})

#                     elif data.get("type") == "audio_playback_ended":
#                         # Client finished playing TTS audio — unmute mic
#                         voice_engine.unmute()
#                         print("🎤 Client playback ended — mic unmuted")

#                         if is_connected:
#                             await websocket.send_json({"type": "unmute_mic"})

#             except asyncio.TimeoutError:
#                 if is_connected:
#                     try:
#                         await websocket.send_json({"type": "keep_alive"})
#                     except:
#                         break

#             except WebSocketDisconnect:
#                 print("🔌 WebSocket disconnected by client")
#                 is_connected = False
#                 break

#             except RuntimeError as e:
#                 if "disconnect" in str(e).lower():
#                     print("🔌 WebSocket disconnect detected")
#                     is_connected = False
#                     break
#                 else:
#                     raise

#             except Exception as e:
#                 print(f"❌ WebSocket error: {str(e)}")
#                 is_connected = False
#                 break

#     except WebSocketDisconnect:
#         print("🔌 WebSocket disconnected during setup")

#     except Exception as e:
#         print(f"❌ WebSocket fatal error: {str(e)}")
#         print(traceback.format_exc())

#     finally:
#         is_connected = False
#         voice_engine.cleanup()
#         db.close()
#         print("🧹 WebSocket cleanup completed")






























from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import io
import json
import asyncio
import traceback
import uuid
import base64

from services.voice_service import voice_service
from services.voice_engine import create_voice_engine
from services.voice_llm_agent import get_voice_agricultural_advice, clear_voice_session
from crud.sensor import get_latest_reading
from database import get_db

router = APIRouter(prefix="/voice", tags=["Voice Services"])


@router.websocket("/ws/voice-advisor")
async def voice_advisor_websocket(websocket: WebSocket):
    """
    Real-time Voice-to-Voice AI Advisor WebSocket

    Protocol:
    1. Client sends: Raw audio chunks (16kHz, 16-bit, mono PCM)
    2. Client sends: JSON { type: "audio_playback_ended" } when TTS audio finishes playing
    3. Server sends: JSON status messages + Audio response chunks
    4. Server sends: { type: "mute_mic" } before TTS, waits for client to unmute after playback
    """

    await websocket.accept()

    voice_engine = create_voice_engine()

    from ..database import SessionLocal
    db = SessionLocal()

    session_id = None
    land_size = 1.0
    is_connected = True

    loop = asyncio.get_running_loop()

    print("🔌 WebSocket connected: voice-advisor")

    try:
        await websocket.send_json({
            "type": "status",
            "message": "Connected to AI Voice Advisor. Start speaking..."
        })

        async def handle_recognized_speech(text: str, language: str):
            nonlocal session_id

            if not is_connected:
                return

            try:
                # Send transcription to client
                await websocket.send_json({
                    "type": "transcription",
                    "text": text,
                    "language": language
                })

                # Get latest sensor data
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
                    print(f"📊 Latest reading: ID={latest_reading.id}, N={latest_reading.nitrogen}")
                    print(f"📊 Using sensor data: N={latest_reading.nitrogen}, P={latest_reading.phosphorus}, K={latest_reading.potassium}")
                else:
                    sensor_data = {
                        "nitrogen": 200, "phosphorus": 20, "potassium": 150,
                        "ph": 6.5, "temperature": 25, "humidity": 50, "ec": 1000
                    }
                    print("⚠️ Using default sensor values")

                if not session_id:
                    session_id = str(uuid.uuid4())

                # Use voice-specific LLM agent (separate from chat endpoint)
                ai_result = get_voice_agricultural_advice(
                    user_message=text,
                    sensor_data=sensor_data,
                    land_size=land_size,
                    session_id=session_id
                )

                ai_response = ai_result["response"]
                response_language = ai_result.get("language", language)

                # Send AI text response
                await websocket.send_json({
                    "type": "ai_response",
                    "text": ai_response
                })

                print(f"🤖 AI Response ({response_language}): {ai_response[:100]}...")

                # MUTE mic on server side before TTS
                voice_engine.mute()

                # Tell client to mute mic
                if is_connected:
                    await websocket.send_json({"type": "mute_mic"})

                # Convert AI response to speech using detected language for TTS voice
                async for audio_chunk in voice_engine.text_to_speech_stream(ai_response, response_language):
                    if not is_connected:
                        break

                    audio_b64 = base64.b64encode(audio_chunk).decode('utf-8')
                    await websocket.send_json({
                        "type": "audio_chunk",
                        "data": audio_b64
                    })

                # Tell client all audio chunks sent
                if is_connected:
                    await websocket.send_json({"type": "completed"})

                print("✅ Audio chunks streamed, waiting for client playback to finish")

            except WebSocketDisconnect:
                print("🔌 Client disconnected during response")
            except Exception as e:
                error_str = str(e)
                if "disconnect" in error_str.lower() or "closed" in error_str.lower():
                    print("🔌 Client disconnected during response")
                    return

                print(f"❌ Error handling speech: {error_str}")
                print(traceback.format_exc())

                # Unmute on error so mic doesn't stay stuck
                voice_engine.unmute()

                if is_connected:
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Error processing request: {error_str}"
                        })
                        await websocket.send_json({"type": "unmute_mic"})
                    except:
                        pass

        async def send_error_message(error: str):
            try:
                if is_connected:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Speech recognition error: {error}. Please check your microphone."
                    })
            except:
                pass

        def on_speech_recognized(text: str, language: str):
            if is_connected:
                asyncio.run_coroutine_threadsafe(
                    handle_recognized_speech(text, language), loop
                )

        def on_recognition_error(error_details: str):
            print(f"❌ Recognition error: {error_details}")
            if is_connected:
                asyncio.run_coroutine_threadsafe(
                    send_error_message(error_details), loop
                )

        # Start continuous recognition
        voice_engine.start_continuous_recognition(
            on_recognized_callback=on_speech_recognized,
            on_error_callback=on_recognition_error
        )

        # Main loop - receive audio chunks from client
        while is_connected:
            try:
                message = await asyncio.wait_for(websocket.receive(), timeout=30.0)

                if "bytes" in message:
                    audio_chunk = message["bytes"]
                    voice_engine.write_audio_chunk(audio_chunk)

                elif "text" in message:
                    data = json.loads(message["text"])

                    if data.get("type") == "config":
                        land_size = data.get("land_size_acres", 1.0)
                        print(f"⚙️ Updated land size: {land_size} acres")

                    elif data.get("type") == "reset":
                        if session_id:
                            clear_voice_session(session_id)
                        session_id = None
                        print("🔄 Session reset")

                        if is_connected:
                            await websocket.send_json({
                                "type": "status",
                                "message": "Session reset. Start speaking..."
                            })

                    elif data.get("type") == "ping":
                        if is_connected:
                            await websocket.send_json({"type": "pong"})

                    elif data.get("type") == "audio_playback_ended":
                        # Client finished playing TTS audio — unmute mic
                        voice_engine.unmute()
                        print("🎤 Client playback ended — mic unmuted")

                        if is_connected:
                            await websocket.send_json({"type": "unmute_mic"})

            except asyncio.TimeoutError:
                if is_connected:
                    try:
                        await websocket.send_json({"type": "keep_alive"})
                    except:
                        break

            except WebSocketDisconnect:
                print("🔌 WebSocket disconnected by client")
                is_connected = False
                break

            except RuntimeError as e:
                if "disconnect" in str(e).lower():
                    print("🔌 WebSocket disconnect detected")
                    is_connected = False
                    break
                else:
                    raise

            except Exception as e:
                print(f"❌ WebSocket error: {str(e)}")
                is_connected = False
                break

    except WebSocketDisconnect:
        print("🔌 WebSocket disconnected during setup")

    except Exception as e:
        print(f"❌ WebSocket fatal error: {str(e)}")
        print(traceback.format_exc())

    finally:
        is_connected = False
        voice_engine.cleanup()
        db.close()
        print("🧹 WebSocket cleanup completed")
