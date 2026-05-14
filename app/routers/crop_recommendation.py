# # """
# # AgriCheck – Crop Recommendation Endpoint  (v2 – Live Sensor Integration)
# # File: app/routers/crop_recommendation.py

# # Flow:
# #   ESP32  →  POST /readings/  →  DB  →  GET /api/v1/recommend-crops  →  Top-3 Crops
  
# # No query parameters needed. Data is pulled automatically from the latest DB reading.
# # """

# # from __future__ import annotations

# # import os
# # import json
# # import logging
# # from typing import List

# # import httpx
# # from fastapi import APIRouter, Depends, HTTPException
# # from sqlalchemy.orm import Session
# # from pydantic import BaseModel

# # from ..database import get_db
# # from ..crud import sensor as crud

# # logger = logging.getLogger(__name__)


# # # ─────────────────────────────────────────────────────────────────────────────
# # # Pydantic response schemas
# # # ─────────────────────────────────────────────────────────────────────────────

# # class SensorSnapshot(BaseModel):
# #     """The live sensor values that were used for this recommendation."""
# #     nitrogen: float
# #     phosphorus: float
# #     potassium: float
# #     ph: float
# #     temperature: float
# #     humidity: float
# #     ec: float
# #     reading_id: int
# #     timestamp: str


# # class CropRecommendation(BaseModel):
# #     rank: int
# #     name: str
# #     reason: str


# # class RecommendationResponse(BaseModel):
# #     status: str
# #     sensor_data: SensorSnapshot        # ← shows which reading was used
# #     recommendations: List[CropRecommendation]
# #     summary: str                       # ← single combined message


# # # ─────────────────────────────────────────────────────────────────────────────
# # # Agronomic knowledge base  (Pakistani context)
# # # ─────────────────────────────────────────────────────────────────────────────

# # CROP_PROFILES: dict[str, dict] = {

# #     # ── Major Kharif Crops (Summer) ───────────────────────────────────────────
# #     "Rice": {
# #         "n":           (80,  120),
# #         "p":           (30,   60),
# #         "k":           (30,   60),
# #         "ph":          (5.5,  6.5),
# #         "humidity":    (70,   90),
# #         "temperature": (20,   35),
# #         "ec":          (0.3,  1.5),
# #     },
# #     "Cotton": {
# #         "n":           (60,  120),
# #         "p":           (30,   60),
# #         "k":           (40,   80),
# #         "ph":          (6.0,  8.0),
# #         "humidity":    (40,   70),
# #         "temperature": (25,   38),
# #         "ec":          (0.5,  3.0),
# #     },
# #     "Maize": {
# #         "n":           (100, 150),
# #         "p":           (40,   70),
# #         "k":           (40,   70),
# #         "ph":          (5.8,  7.0),
# #         "humidity":    (50,   80),
# #         "temperature": (18,   32),
# #         "ec":          (0.5,  2.5),
# #     },
# #     "Sugarcane": {
# #         "n":           (100, 180),
# #         "p":           (40,   80),
# #         "k":           (80,  150),
# #         "ph":          (6.0,  7.5),
# #         "humidity":    (65,   90),
# #         "temperature": (25,   38),
# #         "ec":          (0.5,  2.5),
# #     },
# #     "Sorghum (Jowar)": {
# #         "n":           (60,  100),
# #         "p":           (30,   50),
# #         "k":           (30,   50),
# #         "ph":          (5.5,  7.5),
# #         "humidity":    (30,   70),
# #         "temperature": (25,   38),
# #         "ec":          (0.5,  4.0),   # drought & salt tolerant
# #     },
# #     "Millet (Bajra)": {
# #         "n":           (40,   80),
# #         "p":           (20,   40),
# #         "k":           (20,   40),
# #         "ph":          (5.5,  7.0),
# #         "humidity":    (25,   60),
# #         "temperature": (25,   38),
# #         "ec":          (0.5,  3.5),
# #     },
# #     "Sesame (Til)": {
# #         "n":           (40,   70),
# #         "p":           (25,   45),
# #         "k":           (25,   45),
# #         "ph":          (5.5,  7.5),
# #         "humidity":    (30,   60),
# #         "temperature": (25,   35),
# #         "ec":          (0.5,  2.5),
# #     },
# #     "Mung Bean (Moong)": {
# #         "n":           (20,   40),   # fixes its own N
# #         "p":           (40,   60),
# #         "k":           (30,   50),
# #         "ph":          (6.0,  7.5),
# #         "humidity":    (50,   80),
# #         "temperature": (25,   35),
# #         "ec":          (0.3,  2.0),
# #     },
# #     "Moth Bean (Mash)": {
# #         "n":           (20,   40),
# #         "p":           (35,   55),
# #         "k":           (30,   50),
# #         "ph":          (6.0,  7.5),
# #         "humidity":    (40,   70),
# #         "temperature": (25,   35),
# #         "ec":          (0.3,  2.5),
# #     },

# #     # ── Major Rabi Crops (Winter) ─────────────────────────────────────────────
# #     "Wheat": {
# #         "n":           (80,  120),
# #         "p":           (40,   60),
# #         "k":           (40,   60),
# #         "ph":          (6.0,  7.5),
# #         "humidity":    (50,   70),
# #         "temperature": (10,   25),
# #         "ec":          (0.5,  2.0),
# #     },
# #     "Mustard (Sarson)": {
# #         "n":           (60,  100),
# #         "p":           (30,   50),
# #         "k":           (30,   50),
# #         "ph":          (5.8,  7.0),
# #         "humidity":    (40,   65),
# #         "temperature": (10,   25),
# #         "ec":          (0.5,  2.5),
# #     },
# #     "Chickpea (Chanay)": {
# #         "n":           (20,   40),   # fixes its own N
# #         "p":           (40,   60),
# #         "k":           (30,   50),
# #         "ph":          (6.0,  8.0),
# #         "humidity":    (30,   60),
# #         "temperature": (10,   25),
# #         "ec":          (0.3,  3.0),
# #     },
# #     "Lentil (Masoor)": {
# #         "n":           (20,   40),
# #         "p":           (35,   55),
# #         "k":           (25,   45),
# #         "ph":          (6.0,  8.0),
# #         "humidity":    (35,   65),
# #         "temperature": (10,   25),
# #         "ec":          (0.3,  2.5),
# #     },
# #     "Barley (Jau)": {
# #         "n":           (60,  100),
# #         "p":           (30,   50),
# #         "k":           (30,   50),
# #         "ph":          (6.0,  8.5),
# #         "humidity":    (40,   65),
# #         "temperature": (8,    22),
# #         "ec":          (0.5,  5.0),   # very salt tolerant
# #     },

# #     # ── Vegetables ────────────────────────────────────────────────────────────
# #     "Potato": {
# #         "n":           (100, 150),
# #         "p":           (60,  100),
# #         "k":           (80,  130),
# #         "ph":          (5.0,  6.5),
# #         "humidity":    (60,   80),
# #         "temperature": (15,   25),
# #         "ec":          (0.5,  2.0),
# #     },
# #     "Tomato": {
# #         "n":           (80,  120),
# #         "p":           (50,   80),
# #         "k":           (60,  100),
# #         "ph":          (5.5,  7.0),
# #         "humidity":    (50,   75),
# #         "temperature": (18,   30),
# #         "ec":          (0.5,  2.5),
# #     },
# #     "Onion (Pyaaz)": {
# #         "n":           (60,  100),
# #         "p":           (40,   60),
# #         "k":           (50,   80),
# #         "ph":          (6.0,  7.0),
# #         "humidity":    (50,   70),
# #         "temperature": (13,   24),
# #         "ec":          (0.5,  1.5),
# #     },
# #     "Chilli": {
# #         "n":           (80,  120),
# #         "p":           (40,   70),
# #         "k":           (50,   90),
# #         "ph":          (5.5,  7.0),
# #         "humidity":    (50,   75),
# #         "temperature": (20,   32),
# #         "ec":          (0.5,  2.0),
# #     },
# #     "Garlic (Lehsan)": {
# #         "n":           (60,  100),
# #         "p":           (40,   60),
# #         "k":           (50,   80),
# #         "ph":          (6.0,  7.5),
# #         "humidity":    (50,   70),
# #         "temperature": (12,   24),
# #         "ec":          (0.5,  2.0),
# #     },
# #     "Spinach (Palak)": {
# #         "n":           (80,  120),
# #         "p":           (30,   50),
# #         "k":           (40,   70),
# #         "ph":          (6.0,  7.5),
# #         "humidity":    (50,   80),
# #         "temperature": (10,   20),
# #         "ec":          (0.5,  2.0),
# #     },

# #     # ── Oilseeds & Cash Crops ─────────────────────────────────────────────────
# #     "Sunflower": {
# #         "n":           (60,  100),
# #         "p":           (40,   60),
# #         "k":           (40,   60),
# #         "ph":          (6.0,  7.5),
# #         "humidity":    (40,   65),
# #         "temperature": (20,   30),
# #         "ec":          (0.5,  2.5),
# #     },
# #     "Canola (Toria)": {
# #         "n":           (70,  110),
# #         "p":           (30,   50),
# #         "k":           (30,   50),
# #         "ph":          (5.5,  7.0),
# #         "humidity":    (40,   65),
# #         "temperature": (10,   20),
# #         "ec":          (0.5,  2.5),
# #     },
# #     "Groundnut (Mungphali)": {
# #         "n":           (20,   40),
# #         "p":           (40,   70),
# #         "k":           (50,   90),
# #         "ph":          (5.5,  7.0),
# #         "humidity":    (50,   75),
# #         "temperature": (22,   35),
# #         "ec":          (0.3,  2.0),
# #     },
# # }

# # PARAM_WEIGHTS = {
# #     "ph":          3.0,   # most critical – wrong pH locks out all nutrients
# #     "temperature": 2.5,
# #     "humidity":    2.0,
# #     "n":           1.5,
# #     "ec":          1.5,
# #     "p":           1.0,
# #     "k":           1.0,
# # }


# # # ─────────────────────────────────────────────────────────────────────────────
# # # Scoring helpers
# # # ─────────────────────────────────────────────────────────────────────────────

# # def _param_score(value: float, low: float, high: float) -> float:
# #     """1.0 inside range, linear decay to 0.0 outside."""
# #     if low <= value <= high:
# #         return 1.0
# #     margin = (high - low) * 0.5 or 1.0
# #     if value < low:
# #         return max(0.0, 1.0 - (low - value) / margin)
# #     return max(0.0, 1.0 - (value - high) / margin)


# # def _build_reason(crop: str, sensor: dict[str, float]) -> str:
# #     """Short human-readable reason string."""
# #     profile = CROP_PROFILES[crop]
# #     label_map = {
# #         "ph": "pH", "n": "Nitrogen", "p": "Phosphorus",
# #         "k": "Potassium", "humidity": "Humidity",
# #         "temperature": "Temperature", "ec": "EC",
# #     }
# #     positives, negatives = [], []
# #     for param, (lo, hi) in profile.items():
# #         (positives if lo <= sensor[param] <= hi else negatives).append(label_map[param])

# #     parts = []
# #     if positives:
# #         parts.append(f"{', '.join(positives[:3])} within optimal range")
# #     if negatives:
# #         parts.append(f"{', '.join(negatives[:2])} slightly outside ideal range")
# #     return "; ".join(parts) if parts else "Conditions are broadly suitable."


# # def score_crops_locally(sensor: dict[str, float]) -> list[dict]:
# #     """Weighted scoring → top-3 ranked list."""
# #     scores = []
# #     for crop, profile in CROP_PROFILES.items():
# #         total_w = weighted_s = 0.0
# #         for param, (lo, hi) in profile.items():
# #             w = PARAM_WEIGHTS.get(param, 1.0)
# #             weighted_s += w * _param_score(sensor[param], lo, hi)
# #             total_w += w
# #         scores.append((crop, (weighted_s / total_w) * 100))

# #     scores.sort(key=lambda x: x[1], reverse=True)
# #     return [
# #         {"rank": i + 1, "name": name, "reason": _build_reason(name, sensor)}
# #         for i, (name, _) in enumerate(scores[:3])
# #     ]


# # # ─────────────────────────────────────────────────────────────────────────────
# # # Optional LLM enrichment via Anthropic API
# # # Set ANTHROPIC_API_KEY in your .env — silently skipped if absent
# # # ─────────────────────────────────────────────────────────────────────────────

# # ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
# # ANTHROPIC_URL     = "https://api.anthropic.com/v1/messages"
# # LLM_MODEL         = "claude-sonnet-4-20250514"


# # async def _enrich_with_llm(sensor: dict[str, float], local_top3: list[dict]) -> list[dict]:
# #     """Replace generic reasons with AI-generated agronomic reasons. Falls back silently."""
# #     if not ANTHROPIC_API_KEY:
# #         return local_top3

# #     prompt = (
# #         "You are an expert agronomist for Pakistani farming conditions.\n"
# #         "Live 7-in-1 soil sensor readings:\n"
# #         f"  Nitrogen (N): {sensor['n']} kg/ha\n"
# #         f"  Phosphorus (P): {sensor['p']} kg/ha\n"
# #         f"  Potassium (K): {sensor['k']} kg/ha\n"
# #         f"  pH: {sensor['ph']}\n"
# #         f"  Humidity: {sensor['humidity']} %\n"
# #         f"  Temperature: {sensor['temperature']} °C\n"
# #         f"  EC: {sensor['ec']} dS/m\n\n"
# #         "Scoring model ranked these top-3 crops:\n"
# #         + "\n".join(f"  {c['rank']}. {c['name']}" for c in local_top3)
# #         + "\n\nFor each crop write ONE concise sentence (max 20 words) explaining WHY "
# #         "it suits these exact sensor values. "
# #         "Reply ONLY with a JSON array, no markdown:\n"
# #         '[{"rank":1,"name":"...","reason":"..."},{"rank":2,...},{"rank":3,...}]'
# #     )

# #     try:
# #         async with httpx.AsyncClient(timeout=12) as client:
# #             resp = await client.post(
# #                 ANTHROPIC_URL,
# #                 headers={
# #                     "x-api-key": ANTHROPIC_API_KEY,
# #                     "anthropic-version": "2023-06-01",
# #                     "content-type": "application/json",
# #                 },
# #                 json={
# #                     "model": LLM_MODEL,
# #                     "max_tokens": 300,
# #                     "messages": [{"role": "user", "content": prompt}],
# #                 },
# #             )
# #         resp.raise_for_status()
# #         enriched = json.loads(resp.json()["content"][0]["text"].strip())
# #         if (
# #             isinstance(enriched, list) and len(enriched) == 3
# #             and all({"rank", "name", "reason"} <= set(c) for c in enriched)
# #         ):
# #             return enriched
# #     except Exception as exc:
# #         logger.warning("LLM enrichment failed (%s) — using local reasons.", exc)

# #     return local_top3


# # # ─────────────────────────────────────────────────────────────────────────────
# # # Router
# # # ─────────────────────────────────────────────────────────────────────────────

# # router = APIRouter(prefix="/api/v1", tags=["Crop Recommendation"])


# # @router.get(
# #     "/recommend-crops",
# #     response_model=RecommendationResponse,
# #     summary="Top-3 crop recommendations from latest live sensor reading",
# #     description=(
# #         "No parameters needed. Automatically fetches the most recent ESP32 sensor "
# #         "reading from the database and returns the top-3 suitable crops ranked by "
# #         "agronomic fit."
# #     ),
# # )
# # async def recommend_crops(db: Session = Depends(get_db)):
# #     # ── Step 1: Fetch latest reading from DB (same function your sensor router uses)
# #     reading = crud.get_latest_reading(db=db)
# #     if not reading:
# #         raise HTTPException(
# #             status_code=404,
# #             detail="No sensor readings found. Make sure the ESP32 is sending data."
# #         )

# #     # ── Step 2: Map DB model fields → internal sensor dict
# #     sensor = {
# #         "n":           reading.nitrogen,
# #         "p":           reading.phosphorus,
# #         "k":           reading.potassium,
# #         "ph":          reading.ph,
# #         "humidity":    reading.humidity,
# #         "temperature": reading.temperature,
# #         "ec":          reading.ec,
# #     }

# #     # ── Step 3: Score crops locally (fast, no I/O)
# #     local_top3 = score_crops_locally(sensor)

# #     # ── Step 4: Optionally enrich reasons with LLM (skipped if no API key)
# #     final_top3 = await _enrich_with_llm(sensor, local_top3)

# #     # Step 5: Build summary string
# #     medals = ["🥇", "🥈", "🥉"]
# #     summary = "\n".join(
# #         f"{medals[i]} {c['name']} — {c['reason']}"
# #         for i, c in enumerate(final_top3)
# #     )

# #     # Step 6: Return response with summary
# #     return RecommendationResponse(
# #         status="success",
# #         summary=summary,
# #         sensor_data=SensorSnapshot(
# #             nitrogen=reading.nitrogen,
# #             phosphorus=reading.phosphorus,
# #             potassium=reading.potassium,
# #             ph=reading.ph,
# #             temperature=reading.temperature,
# #             humidity=reading.humidity,
# #             ec=reading.ec,
# #             reading_id=reading.id,
# #             timestamp=str(reading.timestamp),
# #         ),
# #         recommendations=[CropRecommendation(**c) for c in final_top3],
# #     )





























# """
# AgriCheck – Crop Recommendation Endpoint  (v3 – Units Fixed)
# File: app/routers/crop_recommendation.py

# KEY FIX: All N/P/K ranges are now in mg/kg (matching real ESP32 sensor output).
#          EC is in mS/cm (matching sensor output, NOT dS/m).
#          This ensures llm_agent.py and this endpoint always agree.
# """

# from __future__ import annotations

# import os
# import json
# import logging
# from typing import List

# import httpx
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from pydantic import BaseModel

# from ..database import get_db
# from ..crud import sensor as crud

# logger = logging.getLogger(__name__)


# # ─────────────────────────────────────────────────────────────────────────────
# # Pydantic response schemas
# # ─────────────────────────────────────────────────────────────────────────────

# class SensorSnapshot(BaseModel):
#     nitrogen: float
#     phosphorus: float
#     potassium: float
#     ph: float
#     temperature: float
#     humidity: float
#     ec: float
#     reading_id: int
#     timestamp: str


# class CropRecommendation(BaseModel):
#     rank: int
#     name: str
#     reason: str


# class RecommendationResponse(BaseModel):
#     status: str
#     sensor_data: SensorSnapshot
#     recommendations: List[CropRecommendation]
#     summary: str


# # ─────────────────────────────────────────────────────────────────────────────
# # Agronomic knowledge base
# # ⚠️  ALL units match real ESP32 7-in-1 sensor output:
# #     N / P / K  → mg/kg
# #     pH         → 0–14
# #     Temperature→ °C
# #     Humidity   → %
# #     EC         → mS/cm  (sensor sends mS/cm, NOT dS/m)
# # ─────────────────────────────────────────────────────────────────────────────

# CROP_PROFILES: dict[str, dict] = {

#     # ── Kharif (Summer) ───────────────────────────────────────────────────────
#     "Rice": {
#         "n":           (150,  250),   # mg/kg
#         "p":           (80,   150),
#         "k":           (100,  200),
#         "ph":          (5.5,  6.5),
#         "humidity":    (70,   90),    # %
#         "temperature": (20,   35),    # °C
#         "ec":          (300,  800),   # mS/cm
#     },
#     "Cotton": {
#         "n":           (150,  280),
#         "p":           (80,   160),
#         "k":           (120,  220),
#         "ph":          (6.0,  8.0),
#         "humidity":    (40,   70),
#         "temperature": (25,   38),
#         "ec":          (500,  1500),
#     },
#     "Maize": {
#         "n":           (200,  350),
#         "p":           (100,  200),
#         "k":           (150,  280),
#         "ph":          (5.8,  7.0),
#         "humidity":    (50,   80),
#         "temperature": (18,   32),
#         "ec":          (500,  1500),
#     },
#     "Sugarcane": {
#         "n":           (200,  400),
#         "p":           (100,  200),
#         "k":           (200,  400),
#         "ph":          (6.0,  7.5),
#         "humidity":    (65,   90),
#         "temperature": (25,   38),
#         "ec":          (500,  1500),
#     },
#     "Sorghum (Jowar)": {
#         "n":           (120,  250),
#         "p":           (80,   160),
#         "k":           (100,  200),
#         "ph":          (5.5,  7.5),
#         "humidity":    (30,   70),
#         "temperature": (25,   38),
#         "ec":          (500,  2000),  # drought & salt tolerant
#     },
#     "Millet (Bajra)": {
#         "n":           (100,  200),
#         "p":           (60,   130),
#         "k":           (80,   180),
#         "ph":          (5.5,  7.0),
#         "humidity":    (25,   60),
#         "temperature": (25,   38),
#         "ec":          (500,  1800),
#     },
#     "Sesame (Til)": {
#         "n":           (100,  180),
#         "p":           (60,   130),
#         "k":           (80,   160),
#         "ph":          (5.5,  7.5),
#         "humidity":    (30,   60),
#         "temperature": (25,   35),
#         "ec":          (500,  1500),
#     },
#     "Mung Bean (Moong)": {
#         "n":           (60,   130),   # fixes its own N — needs less
#         "p":           (100,  180),
#         "k":           (100,  200),
#         "ph":          (6.0,  7.5),
#         "humidity":    (50,   80),
#         "temperature": (25,   35),
#         "ec":          (300,  1200),
#     },
#     "Moth Bean (Mash)": {
#         "n":           (60,   130),
#         "p":           (90,   170),
#         "k":           (100,  200),
#         "ph":          (6.0,  7.5),
#         "humidity":    (40,   70),
#         "temperature": (25,   35),
#         "ec":          (300,  1500),
#     },

#     # ── Rabi (Winter) ─────────────────────────────────────────────────────────
#     "Wheat": {
#         "n":           (150,  280),
#         "p":           (100,  200),
#         "k":           (120,  240),
#         "ph":          (6.0,  7.5),
#         "humidity":    (50,   70),
#         "temperature": (10,   25),
#         "ec":          (500,  1200),
#     },
#     "Mustard (Sarson)": {
#         "n":           (120,  250),
#         "p":           (80,   160),
#         "k":           (100,  200),
#         "ph":          (5.8,  7.0),
#         "humidity":    (40,   65),
#         "temperature": (10,   25),
#         "ec":          (500,  1500),
#     },
#     "Chickpea (Chanay)": {
#         "n":           (50,   130),   # fixes its own N
#         "p":           (100,  200),
#         "k":           (100,  200),
#         "ph":          (6.0,  8.0),
#         "humidity":    (30,   60),
#         "temperature": (10,   25),
#         "ec":          (300,  1500),
#     },
#     "Lentil (Masoor)": {
#         "n":           (50,   130),
#         "p":           (90,   170),
#         "k":           (80,   180),
#         "ph":          (6.0,  8.0),
#         "humidity":    (35,   65),
#         "temperature": (10,   25),
#         "ec":          (300,  1200),
#     },
#     "Barley (Jau)": {
#         "n":           (120,  250),
#         "p":           (80,   160),
#         "k":           (100,  200),
#         "ph":          (6.0,  8.5),
#         "humidity":    (40,   65),
#         "temperature": (8,    22),
#         "ec":          (500,  2500),  # very salt tolerant
#     },

#     # ── Vegetables ────────────────────────────────────────────────────────────
#     "Potato": {
#         "n":           (200,  350),
#         "p":           (150,  280),
#         "k":           (250,  400),
#         "ph":          (5.0,  6.5),
#         "humidity":    (60,   80),
#         "temperature": (15,   25),
#         "ec":          (500,  1200),
#     },
#     "Tomato": {
#         "n":           (180,  300),
#         "p":           (120,  220),
#         "k":           (180,  320),
#         "ph":          (5.5,  7.0),
#         "humidity":    (50,   75),
#         "temperature": (18,   30),
#         "ec":          (500,  1500),
#     },
#     "Onion (Pyaaz)": {
#         "n":           (130,  230),
#         "p":           (100,  180),
#         "k":           (150,  260),
#         "ph":          (6.0,  7.0),
#         "humidity":    (50,   70),
#         "temperature": (13,   24),
#         "ec":          (500,  1000),
#     },
#     "Chilli": {
#         "n":           (180,  300),
#         "p":           (100,  200),
#         "k":           (150,  280),
#         "ph":          (5.5,  7.0),
#         "humidity":    (50,   75),
#         "temperature": (20,   32),
#         "ec":          (500,  1200),
#     },
#     "Garlic (Lehsan)": {
#         "n":           (130,  230),
#         "p":           (100,  180),
#         "k":           (150,  260),
#         "ph":          (6.0,  7.5),
#         "humidity":    (50,   70),
#         "temperature": (12,   24),
#         "ec":          (500,  1200),
#     },
#     "Spinach (Palak)": {
#         "n":           (180,  300),
#         "p":           (80,   160),
#         "k":           (120,  240),
#         "ph":          (6.0,  7.5),
#         "humidity":    (50,   80),
#         "temperature": (10,   20),
#         "ec":          (500,  1200),
#     },

#     # ── Oilseeds ──────────────────────────────────────────────────────────────
#     "Sunflower": {
#         "n":           (130,  250),
#         "p":           (100,  180),
#         "k":           (120,  220),
#         "ph":          (6.0,  7.5),
#         "humidity":    (40,   65),
#         "temperature": (20,   30),
#         "ec":          (500,  1500),
#     },
#     "Canola (Toria)": {
#         "n":           (150,  270),
#         "p":           (80,   160),
#         "k":           (100,  200),
#         "ph":          (5.5,  7.0),
#         "humidity":    (40,   65),
#         "temperature": (10,   20),
#         "ec":          (500,  1500),
#     },
#     "Groundnut (Mungphali)": {
#         "n":           (60,   130),
#         "p":           (100,  200),
#         "k":           (150,  270),
#         "ph":          (5.5,  7.0),
#         "humidity":    (50,   75),
#         "temperature": (22,   35),
#         "ec":          (300,  1200),
#     },
# }

# PARAM_WEIGHTS = {
#     "ph":          3.0,
#     "temperature": 2.5,
#     "humidity":    2.0,
#     "n":           1.5,
#     "ec":          1.5,
#     "p":           1.0,
#     "k":           1.0,
# }


# # ─────────────────────────────────────────────────────────────────────────────
# # Scoring helpers
# # ─────────────────────────────────────────────────────────────────────────────

# def _param_score(value: float, low: float, high: float) -> float:
#     """1.0 inside range, linear decay to 0.0 outside."""
#     if low <= value <= high:
#         return 1.0
#     margin = (high - low) * 0.5 or 1.0
#     if value < low:
#         return max(0.0, 1.0 - (low - value) / margin)
#     return max(0.0, 1.0 - (value - high) / margin)


# def _build_reason(crop: str, sensor: dict[str, float]) -> str:
#     """Short human-readable reason string."""
#     profile = CROP_PROFILES[crop]
#     label_map = {
#         "ph": "pH", "n": "Nitrogen", "p": "Phosphorus",
#         "k": "Potassium", "humidity": "Humidity",
#         "temperature": "Temperature", "ec": "EC",
#     }
#     positives, negatives = [], []
#     for param, (lo, hi) in profile.items():
#         (positives if lo <= sensor[param] <= hi else negatives).append(label_map[param])

#     parts = []
#     if positives:
#         parts.append(f"{', '.join(positives[:3])} within optimal range")
#     if negatives:
#         parts.append(f"{', '.join(negatives[:2])} slightly outside ideal range")
#     return "; ".join(parts) if parts else "Conditions are broadly suitable."


# def score_crops_locally(sensor: dict[str, float]) -> list[dict]:
#     """Weighted scoring → top-3 ranked list.
    
#     sensor dict keys: n, p, k, ph, humidity, temperature, ec
#     All values must be in the SAME units as CROP_PROFILES above:
#         n/p/k → mg/kg,  ec → mS/cm,  temp → °C,  humidity → %
#     """
#     scores = []
#     for crop, profile in CROP_PROFILES.items():
#         total_w = weighted_s = 0.0
#         for param, (lo, hi) in profile.items():
#             w = PARAM_WEIGHTS.get(param, 1.0)
#             weighted_s += w * _param_score(sensor[param], lo, hi)
#             total_w += w
#         scores.append((crop, (weighted_s / total_w) * 100))

#     scores.sort(key=lambda x: x[1], reverse=True)
#     return [
#         {"rank": i + 1, "name": name, "reason": _build_reason(name, sensor)}
#         for i, (name, _) in enumerate(scores[:3])
#     ]


# # ─────────────────────────────────────────────────────────────────────────────
# # Optional LLM enrichment via Anthropic API
# # ─────────────────────────────────────────────────────────────────────────────

# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
# ANTHROPIC_URL     = "https://api.anthropic.com/v1/messages"
# LLM_MODEL         = "claude-sonnet-4-20250514"


# async def _enrich_with_llm(sensor: dict[str, float], local_top3: list[dict]) -> list[dict]:
#     """Replace generic reasons with AI-generated agronomic reasons."""
#     if not ANTHROPIC_API_KEY:
#         return local_top3

#     prompt = (
#         "You are an expert agronomist for Pakistani farming conditions.\n"
#         "Live 7-in-1 soil sensor readings:\n"
#         f"  Nitrogen (N): {sensor['n']} mg/kg\n"
#         f"  Phosphorus (P): {sensor['p']} mg/kg\n"
#         f"  Potassium (K): {sensor['k']} mg/kg\n"
#         f"  pH: {sensor['ph']}\n"
#         f"  Humidity: {sensor['humidity']} %\n"
#         f"  Temperature: {sensor['temperature']} °C\n"
#         f"  EC: {sensor['ec']} mS/cm\n\n"
#         "Scoring model ranked these top-3 crops:\n"
#         + "\n".join(f"  {c['rank']}. {c['name']}" for c in local_top3)
#         + "\n\nFor each crop write ONE concise sentence (max 20 words) explaining WHY "
#         "it suits these exact sensor values. "
#         "Reply ONLY with a JSON array, no markdown:\n"
#         '[{"rank":1,"name":"...","reason":"..."},{"rank":2,...},{"rank":3,...}]'
#     )

#     try:
#         async with httpx.AsyncClient(timeout=12) as client:
#             resp = await client.post(
#                 ANTHROPIC_URL,
#                 headers={
#                     "x-api-key": ANTHROPIC_API_KEY,
#                     "anthropic-version": "2023-06-01",
#                     "content-type": "application/json",
#                 },
#                 json={
#                     "model": LLM_MODEL,
#                     "max_tokens": 300,
#                     "messages": [{"role": "user", "content": prompt}],
#                 },
#             )
#         resp.raise_for_status()
#         enriched = json.loads(resp.json()["content"][0]["text"].strip())
#         if (
#             isinstance(enriched, list) and len(enriched) == 3
#             and all({"rank", "name", "reason"} <= set(c) for c in enriched)
#         ):
#             return enriched
#     except Exception as exc:
#         logger.warning("LLM enrichment failed (%s) — using local reasons.", exc)

#     return local_top3


# # ─────────────────────────────────────────────────────────────────────────────
# # Router
# # ─────────────────────────────────────────────────────────────────────────────

# router = APIRouter(prefix="/api/v1", tags=["Crop Recommendation"])


# @router.get(
#     "/recommend-crops",
#     response_model=RecommendationResponse,
#     summary="Top-3 crop recommendations from latest live sensor reading",
# )
# async def recommend_crops(db: Session = Depends(get_db)):
#     reading = crud.get_latest_reading(db=db)
#     if not reading:
#         raise HTTPException(
#             status_code=404,
#             detail="No sensor readings found. Make sure the ESP32 is sending data."
#         )

#     # DB fields map directly — units are whatever the sensor sends (mg/kg, mS/cm)
#     sensor = {
#         "n":           reading.nitrogen,
#         "p":           reading.phosphorus,
#         "k":           reading.potassium,
#         "ph":          reading.ph,
#         "humidity":    reading.humidity,
#         "temperature": reading.temperature,
#         "ec":          reading.ec,
#     }

#     local_top3 = score_crops_locally(sensor)
#     final_top3 = await _enrich_with_llm(sensor, local_top3)

#     medals = ["\U0001f947", "\U0001f948", "\U0001f949"]
#     summary = "\n".join(
#         f"{medals[i]} {c['name']} — {c['reason']}"
#         for i, c in enumerate(final_top3)
#     )

#     return RecommendationResponse(
#         status="success",
#         summary=summary,
#         sensor_data=SensorSnapshot(
#             nitrogen=reading.nitrogen,
#             phosphorus=reading.phosphorus,
#             potassium=reading.potassium,
#             ph=reading.ph,
#             temperature=reading.temperature,
#             humidity=reading.humidity,
#             ec=reading.ec,
#             reading_id=reading.id,
#             timestamp=str(reading.timestamp),
#         ),
#         recommendations=[CropRecommendation(**c) for c in final_top3],
#     )




































































































































"""
AgriCheck – Crop Recommendation Endpoint  (v4 – Production Ready)
File: app/routers/crop_recommendation.py

Changes from v3:
  1. Season selector  — ?season=kharif / rabi / auto (default: auto)
  2. Confidence %     — each crop shows match percentage
  3. Balanced weights — NPK now matters more, temperature less dominant
"""

from __future__ import annotations

import os
import json
import logging
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..crud import sensor as crud

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic schemas
# ─────────────────────────────────────────────────────────────────────────────

class SensorSnapshot(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    temperature: float
    humidity: float
    ec: float
    reading_id: int
    timestamp: str


class CropRecommendation(BaseModel):
    rank: int
    name: str
    confidence: str          # e.g. "84%"
    season: str              # e.g. "Kharif" or "Rabi"
    reason: str


class RecommendationResponse(BaseModel):
    status: str
    season_used: str         # which season filter was applied
    sensor_data: SensorSnapshot
    recommendations: List[CropRecommendation]
    summary: str


# ─────────────────────────────────────────────────────────────────────────────
# Season classification
# ─────────────────────────────────────────────────────────────────────────────

KHARIF_CROPS = {
    "Rice", "Cotton", "Maize", "Sugarcane",
    "Sorghum (Jowar)", "Millet (Bajra)", "Sesame (Til)",
    "Mung Bean (Moong)", "Moth Bean (Mash)",
    "Groundnut (Mungphali)",
}

RABI_CROPS = {
    "Wheat", "Mustard (Sarson)", "Chickpea (Chanay)",
    "Lentil (Masoor)", "Barley (Jau)",
    "Potato", "Onion (Pyaaz)", "Garlic (Lehsan)",
    "Spinach (Palak)", "Canola (Toria)",
}

# Crops that can grow in both seasons
BOTH_SEASONS = {
    "Tomato", "Chilli", "Sunflower",
}

ALL_CROPS_SEASON = {
    **{c: "Kharif" for c in KHARIF_CROPS},
    **{c: "Rabi"   for c in RABI_CROPS},
    **{c: "Both"   for c in BOTH_SEASONS},
}


# ─────────────────────────────────────────────────────────────────────────────
# Agronomic profiles
# Units: N/P/K → mg/kg | EC → mS/cm | Temp → °C | Humidity → %
# ─────────────────────────────────────────────────────────────────────────────

CROP_PROFILES: dict[str, dict] = {

    # ── Kharif ───────────────────────────────────────────────────────────────
    "Rice": {
        "n":           (150, 250),
        "p":           (80,  150),
        "k":           (100, 200),
        "ph":          (5.5, 6.5),
        "humidity":    (70,  90),
        "temperature": (20,  35),
        "ec":          (300, 800),
    },
    "Cotton": {
        "n":           (150, 280),
        "p":           (80,  160),
        "k":           (120, 220),
        "ph":          (6.0, 8.0),
        "humidity":    (40,  70),
        "temperature": (25,  38),
        "ec":          (500, 1500),
    },
    "Maize": {
        "n":           (200, 350),
        "p":           (100, 200),
        "k":           (150, 280),
        "ph":          (5.8, 7.0),
        "humidity":    (50,  80),
        "temperature": (18,  32),
        "ec":          (500, 1500),
    },
    "Sugarcane": {
        "n":           (200, 400),
        "p":           (100, 200),
        "k":           (200, 400),
        "ph":          (6.0, 7.5),
        "humidity":    (65,  90),
        "temperature": (25,  38),
        "ec":          (500, 1500),
    },
    "Sorghum (Jowar)": {
        "n":           (120, 250),
        "p":           (80,  160),
        "k":           (100, 200),
        "ph":          (5.5, 7.5),
        "humidity":    (30,  70),
        "temperature": (25,  38),
        "ec":          (500, 2000),
    },
    "Millet (Bajra)": {
        "n":           (100, 200),
        "p":           (60,  130),
        "k":           (80,  180),
        "ph":          (5.5, 7.0),
        "humidity":    (25,  60),
        "temperature": (25,  38),
        "ec":          (500, 1800),
    },
    "Sesame (Til)": {
        "n":           (100, 180),
        "p":           (60,  130),
        "k":           (80,  160),
        "ph":          (5.5, 7.5),
        "humidity":    (30,  60),
        "temperature": (25,  35),
        "ec":          (500, 1500),
    },
    "Mung Bean (Moong)": {
        "n":           (60,  130),
        "p":           (100, 180),
        "k":           (100, 200),
        "ph":          (6.0, 7.5),
        "humidity":    (50,  80),
        "temperature": (25,  35),
        "ec":          (300, 1200),
    },
    "Moth Bean (Mash)": {
        "n":           (60,  130),
        "p":           (90,  170),
        "k":           (100, 200),
        "ph":          (6.0, 7.5),
        "humidity":    (40,  70),
        "temperature": (25,  35),
        "ec":          (300, 1500),
    },
    "Groundnut (Mungphali)": {
        "n":           (60,  130),
        "p":           (100, 200),
        "k":           (150, 270),
        "ph":          (5.5, 7.0),
        "humidity":    (50,  75),
        "temperature": (22,  35),
        "ec":          (300, 1200),
    },

    # ── Rabi ─────────────────────────────────────────────────────────────────
    "Wheat": {
        "n":           (150, 280),
        "p":           (100, 200),
        "k":           (120, 240),
        "ph":          (6.0, 7.5),
        "humidity":    (50,  70),
        "temperature": (10,  25),
        "ec":          (500, 1200),
    },
    "Mustard (Sarson)": {
        "n":           (120, 250),
        "p":           (80,  160),
        "k":           (100, 200),
        "ph":          (5.8, 7.0),
        "humidity":    (40,  65),
        "temperature": (10,  25),
        "ec":          (500, 1500),
    },
    "Chickpea (Chanay)": {
        "n":           (50,  130),
        "p":           (100, 200),
        "k":           (100, 200),
        "ph":          (6.0, 8.0),
        "humidity":    (30,  60),
        "temperature": (10,  25),
        "ec":          (300, 1500),
    },
    "Lentil (Masoor)": {
        "n":           (50,  130),
        "p":           (90,  170),
        "k":           (80,  180),
        "ph":          (6.0, 8.0),
        "humidity":    (35,  65),
        "temperature": (10,  25),
        "ec":          (300, 1200),
    },
    "Barley (Jau)": {
        "n":           (120, 250),
        "p":           (80,  160),
        "k":           (100, 200),
        "ph":          (6.0, 8.5),
        "humidity":    (40,  65),
        "temperature": (8,   22),
        "ec":          (500, 2500),
    },
    "Potato": {
        "n":           (200, 350),
        "p":           (150, 280),
        "k":           (250, 400),
        "ph":          (5.0, 6.5),
        "humidity":    (60,  80),
        "temperature": (15,  25),
        "ec":          (500, 1200),
    },
    "Onion (Pyaaz)": {
        "n":           (130, 230),
        "p":           (100, 180),
        "k":           (150, 260),
        "ph":          (6.0, 7.0),
        "humidity":    (50,  70),
        "temperature": (13,  24),
        "ec":          (500, 1000),
    },
    "Garlic (Lehsan)": {
        "n":           (130, 230),
        "p":           (100, 180),
        "k":           (150, 260),
        "ph":          (6.0, 7.5),
        "humidity":    (50,  70),
        "temperature": (12,  24),
        "ec":          (500, 1200),
    },
    "Spinach (Palak)": {
        "n":           (180, 300),
        "p":           (80,  160),
        "k":           (120, 240),
        "ph":          (6.0, 7.5),
        "humidity":    (50,  80),
        "temperature": (10,  20),
        "ec":          (500, 1200),
    },
    "Canola (Toria)": {
        "n":           (150, 270),
        "p":           (80,  160),
        "k":           (100, 200),
        "ph":          (5.5, 7.0),
        "humidity":    (40,  65),
        "temperature": (10,  20),
        "ec":          (500, 1500),
    },

    # ── Both Seasons ──────────────────────────────────────────────────────────
    "Tomato": {
        "n":           (180, 300),
        "p":           (120, 220),
        "k":           (180, 320),
        "ph":          (5.5, 7.0),
        "humidity":    (50,  75),
        "temperature": (18,  30),
        "ec":          (500, 1500),
    },
    "Chilli": {
        "n":           (180, 300),
        "p":           (100, 200),
        "k":           (150, 280),
        "ph":          (5.5, 7.0),
        "humidity":    (50,  75),
        "temperature": (20,  32),
        "ec":          (500, 1200),
    },
    "Sunflower": {
        "n":           (130, 250),
        "p":           (100, 180),
        "k":           (120, 220),
        "ph":          (6.0, 7.5),
        "humidity":    (40,  65),
        "temperature": (20,  30),
        "ec":          (500, 1500),
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Balanced weights — NPK matters more now
# ─────────────────────────────────────────────────────────────────────────────
PARAM_WEIGHTS = {
    "ph":          3.0,   # still most critical
    "n":           2.5,   # ← raised from 1.5
    "p":           2.0,   # ← raised from 1.0
    "k":           2.0,   # ← raised from 1.0
    "temperature": 1.8,   # ← lowered from 2.5
    "humidity":    1.5,   # ← lowered from 2.0
    "ec":          1.2,   # ← lowered from 1.5
}


# ─────────────────────────────────────────────────────────────────────────────
# Auto season detection from temperature
# ─────────────────────────────────────────────────────────────────────────────

def _detect_season(temperature: float) -> str:
    """
    Auto-detect season from soil temperature:
      >= 25°C  → Kharif  (summer crops)
      < 25°C   → Rabi    (winter crops)
    """
    return "kharif" if temperature >= 25 else "rabi"


# ─────────────────────────────────────────────────────────────────────────────
# Scoring helpers
# ─────────────────────────────────────────────────────────────────────────────

def _param_score(value: float, low: float, high: float) -> float:
    """1.0 inside range, linear decay to 0.0 outside."""
    if low <= value <= high:
        return 1.0
    margin = (high - low) * 0.5 or 1.0
    if value < low:
        return max(0.0, 1.0 - (low - value) / margin)
    return max(0.0, 1.0 - (value - high) / margin)


def _build_reason(crop: str, sensor: dict[str, float]) -> str:
    """Short human-readable reason string."""
    profile = CROP_PROFILES[crop]
    label_map = {
        "ph": "pH", "n": "Nitrogen", "p": "Phosphorus",
        "k": "Potassium", "humidity": "Humidity",
        "temperature": "Temperature", "ec": "EC",
    }
    positives, negatives = [], []
    for param, (lo, hi) in profile.items():
        (positives if lo <= sensor[param] <= hi else negatives).append(label_map[param])

    parts = []
    if positives:
        parts.append(f"{', '.join(positives[:3])} within optimal range")
    if negatives:
        parts.append(f"{', '.join(negatives[:2])} slightly outside ideal range")
    return "; ".join(parts) if parts else "Conditions are broadly suitable."


def score_crops_locally(
    sensor: dict[str, float],
    season: str = "auto",
) -> list[dict]:
    """
    Weighted scoring → top-3 ranked list.

    Args:
        sensor : dict with keys n, p, k, ph, humidity, temperature, ec
        season : "kharif" | "rabi" | "auto" (default)
                 auto = detect from temperature

    Returns:
        list of 3 dicts: {rank, name, confidence, season, reason}
    """
    # Resolve season
    if season == "auto":
        resolved = _detect_season(sensor["temperature"])
    else:
        resolved = season.lower()

    # Filter crops by season
    eligible = {
        crop for crop, s in ALL_CROPS_SEASON.items()
        if s.lower() == resolved or s.lower() == "both"
    }

    scores = []
    for crop, profile in CROP_PROFILES.items():
        if crop not in eligible:
            continue
        total_w = weighted_s = 0.0
        for param, (lo, hi) in profile.items():
            w = PARAM_WEIGHTS.get(param, 1.0)
            weighted_s += w * _param_score(sensor[param], lo, hi)
            total_w += w
        pct = (weighted_s / total_w) * 100
        scores.append((crop, pct))

    scores.sort(key=lambda x: x[1], reverse=True)

    return [
        {
            "rank":       i + 1,
            "name":       name,
            "confidence": f"{score:.0f}%",
            "season":     ALL_CROPS_SEASON.get(name, "Both"),
            "reason":     _build_reason(name, sensor),
        }
        for i, (name, score) in enumerate(scores[:3])
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Optional LLM enrichment via Anthropic API
# ─────────────────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_URL     = "https://api.anthropic.com/v1/messages"
LLM_MODEL         = "claude-sonnet-4-20250514"


async def _enrich_with_llm(sensor: dict[str, float], local_top3: list[dict]) -> list[dict]:
    """Replace generic reasons with AI-generated agronomic reasons."""
    if not ANTHROPIC_API_KEY:
        return local_top3

    prompt = (
        "You are an expert agronomist for Pakistani farming conditions.\n"
        "Live 7-in-1 soil sensor readings:\n"
        f"  Nitrogen (N): {sensor['n']} mg/kg\n"
        f"  Phosphorus (P): {sensor['p']} mg/kg\n"
        f"  Potassium (K): {sensor['k']} mg/kg\n"
        f"  pH: {sensor['ph']}\n"
        f"  Humidity: {sensor['humidity']} %\n"
        f"  Temperature: {sensor['temperature']} °C\n"
        f"  EC: {sensor['ec']} mS/cm\n\n"
        "Scoring model ranked these top-3 crops:\n"
        + "\n".join(f"  {c['rank']}. {c['name']} ({c['confidence']} match)" for c in local_top3)
        + "\n\nFor each crop write ONE concise sentence (max 20 words) explaining WHY "
        "it suits these exact sensor values. "
        "Reply ONLY with a JSON array, no markdown:\n"
        '[{"rank":1,"name":"...","reason":"..."},{"rank":2,...},{"rank":3,...}]'
    )

    try:
        async with httpx.AsyncClient(timeout=12) as client:
            resp = await client.post(
                ANTHROPIC_URL,
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": LLM_MODEL,
                    "max_tokens": 300,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
        resp.raise_for_status()
        enriched = json.loads(resp.json()["content"][0]["text"].strip())
        if (
            isinstance(enriched, list) and len(enriched) == 3
            and all({"rank", "name", "reason"} <= set(c) for c in enriched)
        ):
            # Merge enriched reasons back, keep confidence & season from local
            enriched_map = {c["name"]: c["reason"] for c in enriched}
            for crop in local_top3:
                if crop["name"] in enriched_map:
                    crop["reason"] = enriched_map[crop["name"]]
            return local_top3
    except Exception as exc:
        logger.warning("LLM enrichment failed (%s) — using local reasons.", exc)

    return local_top3


# ─────────────────────────────────────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/v1", tags=["Crop Recommendation"])


@router.get(
    "/recommend-crops",
    response_model=RecommendationResponse,
    summary="Top-3 crop recommendations from latest live sensor reading",
    description=(
        "Fetches latest ESP32 sensor reading from DB and returns the top-3 "
        "suitable crops with confidence %, season tag, and agronomic reasons.\n\n"
        "**season** parameter:\n"
        "- `auto` (default) — detects from soil temperature (≥25°C = Kharif)\n"
        "- `kharif` — only summer crops (Rice, Cotton, Maize, Sugarcane…)\n"
        "- `rabi` — only winter crops (Wheat, Mustard, Chickpea, Potato…)"
    ),
)
async def recommend_crops(
    db: Session = Depends(get_db),
    season: Optional[str] = Query(
        default="auto",
        description="Season filter: 'auto', 'kharif', or 'rabi'",
        regex="^(auto|kharif|rabi)$",
    ),
):
    reading = crud.get_latest_reading(db=db)
    if not reading:
        raise HTTPException(
            status_code=404,
            detail="No sensor readings found. Make sure the ESP32 is sending data."
        )

    sensor = {
        "n":           reading.nitrogen,
        "p":           reading.phosphorus,
        "k":           reading.potassium,
        "ph":          reading.ph,
        "humidity":    reading.humidity,
        "temperature": reading.temperature,
        "ec":          reading.ec,
    }

    # Score with season filter
    local_top3 = score_crops_locally(sensor, season=season or "auto")

    # Optionally enrich reasons with LLM
    final_top3 = await _enrich_with_llm(sensor, local_top3)

    # Resolve which season was actually used
    if season == "auto" or not season:
        season_used = f"Auto → {_detect_season(sensor['temperature']).capitalize()}"
    else:
        season_used = season.capitalize()

    # Build summary string
    medals = ["\U0001f947", "\U0001f948", "\U0001f949"]
    summary = "\n".join(
        f"{medals[i]} {c['name']} ({c['confidence']}) — {c['reason']}"
        for i, c in enumerate(final_top3)
    )

    return RecommendationResponse(
        status="success",
        season_used=season_used,
        summary=summary,
        sensor_data=SensorSnapshot(
            nitrogen=reading.nitrogen,
            phosphorus=reading.phosphorus,
            potassium=reading.potassium,
            ph=reading.ph,
            temperature=reading.temperature,
            humidity=reading.humidity,
            ec=reading.ec,
            reading_id=reading.id,
            timestamp=str(reading.timestamp),
        ),
        recommendations=[CropRecommendation(**c) for c in final_top3],
    )