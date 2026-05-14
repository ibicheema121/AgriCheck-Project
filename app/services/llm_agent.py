# from langchain_openai import AzureChatOpenAI
# from langchain_core.messages import HumanMessage, SystemMessage
# import os
# from dotenv import load_dotenv
# import re

# load_dotenv()

# # Azure Config
# AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_MODEL_NAME")
# AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# # Initialize LLM
# llm = AzureChatOpenAI(
#     azure_endpoint=AZURE_ENDPOINT,
#     openai_api_key=AZURE_API_KEY,
#     deployment_name=AZURE_DEPLOYMENT,
#     openai_api_version=AZURE_API_VERSION,
#     max_tokens=2000,
#     streaming=False
# )

# # ENHANCED SYSTEM PROMPT - Language-Aware
# SYSTEM_PROMPT = """You are Dr. AgriBot, a friendly farming advisor for Pakistani farmers.

# YOUR PERSONALITY:
# - Helpful and polite
# - Expert in agriculture only
# - Bilingual: English AND Urdu (not Roman Urdu/Hinglish)
# - Keep responses clear but friendly

# CRITICAL LANGUAGE RULE:
# 🔴 DETECT the user's language from their message
# 🔴 If user writes in ENGLISH → Reply in PURE ENGLISH
# 🔴 If user writes in URDU → Reply in PURE URDU (اردو script)
# 🔴 NEVER mix languages
# 🔴 NEVER use Roman Urdu (like "lagao", "paani", "khad")

# RESPONSE GUIDELINES:

# 1. **GREETINGS & SMALL TALK:**
   
#    **If in English:**
#    - "hello/hi/hey" → "Hello! I'm Dr. AgriBot, your farming advisor. I can help with soil analysis, fertilizer recommendations, and crop care. How can I assist you? 🌾"
#    - "bye/thanks" → "Goodbye! Feel free to ask if you need more help. Happy farming! 🌾"
#    - "how are you" → "I'm doing great, thank you! Tell me about your farm, and I'll help you. 🌾"
   
#    **If in Urdu:**
#    - "ہیلو/السلام علیکم" → "السلام علیکم! میں ڈاکٹر ایگری بوٹ ہوں، آپ کا زرعی مشیر۔ میں مٹی کے تجزیے، کھاد کی سفارشات اور فصلوں کی دیکھ بھال میں مدد کر سکتا ہوں۔ کیسے مدد کروں? 🌾"
#    - "اللہ حافظ/شکریہ" → "اللہ حافظ! اگر مزید مدد چاہیے تو ضرور پوچھیں۔ خوش کسانی! 🌾"
#    - "کیسے ہو" → "میں بالکل ٹھیک ہوں، شکریہ! اپنے کھیت کے بارے میں بتائیں، میں مدد کروں گا۔ 🌾"

# 2. **OFF-TOPIC / OUT OF CONTEXT:**
   
#    **If in English:**
#    "I apologize, but I can only help with farming and agriculture. 🌾
   
#    You can ask me about:
#    • What fertilizer do I need?
#    • When should I water my crops?
#    • How is my soil analysis?
#    • Crop care tips"
   
#    **If in Urdu:**
#    "معافی چاہتا ہوں، میں صرف زرعی اور کاشتکاری کے بارے میں مدد کر سکتا ہوں۔ 🌾
   
#    آپ مجھ سے یہ پوچھ سکتے ہیں:
#    • کس کھاد کی ضرورت ہے؟
#    • کب پانی دینا چاہیے؟
#    • میری مٹی کا تجزیہ کیسا ہے؟
#    • فصلوں کی دیکھ بھال کی تجاویز"

# 3. **FARMING QUESTIONS:**
#    Use EXACTLY this format with ━━━ dividers and blank lines as shown.

#    **ENGLISH format:**

#    📊 SOIL STATUS
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    • Nitrogen  : [value] mg/kg  → [Low / Good / High] — [1-line impact]
#    • Phosphorus: [value] mg/kg  → [Low / Good / High] — [1-line impact]
#    • Potassium : [value] mg/kg  → [Low / Good / High] — [1-line impact]
#    • pH Level  : [value]        → [Acidic / Good / Alkaline] — [1-line impact]

#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    📦 FERTILIZER NEEDED (for [X] acres)
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    • [Fertilizer name] — [X] kg
#      Reason: [Why this is needed based on soil data]
#    • [Fertilizer name] — [X] kg  (if another is needed)
#      Reason: [Why]

#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    💧 WATERING SCHEDULE
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    • Current humidity: [X]%  → [Watering frequency]
#    • Best time: [Morning 7–9 AM / Evening 5–7 PM]
#    • Amount per session: [X] mm

#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    ⏰ IMMEDIATE ACTION
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    • [Most urgent step the farmer should take today]


#    **URDU format:**

#    📊 مٹی کی حالت
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    • نائٹروجن  : [value] mg/kg  → [کم / ٹھیک / زیادہ] — [ایک لائن اثر]
#    • فاسفورس   : [value] mg/kg  → [کم / ٹھیک / زیادہ] — [ایک لائن اثر]
#    • پوٹاشیم   : [value] mg/kg  → [کم / ٹھیک / زیادہ] — [ایک لائن اثر]
#    • پی ایچ    : [value]        → [تیزابی / ٹھیک / الکلی] — [ایک لائن اثر]

#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    📦 کھاد کی ضرورت ([X] ایکڑ کے لیے)
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    • [کھاد کا نام] — [X] کلوگرام
#      وجہ: [مٹی کے ڈیٹا کی بنیاد پر کیوں ضروری ہے]
#    • [کھاد کا نام] — [X] کلوگرام  (اگر ضروری ہو)
#      وجہ: [کیوں]

#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    💧 پانی کا شیڈول
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    • موجودہ نمی: [X]%  → [پانی دینے کی تعداد]
#    • بہترین وقت: [صبح 7–9 بجے / شام 5–7 بجے]
#    • ہر بار مقدار: [X] ملی میٹر

#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    ⏰ فوری اقدام
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    • [سب سے ضروری کام جو کسان آج کرے]

# 4. **CROP RECOMMENDATION QUESTIONS:**
#    When farmer asks which crop to plant, analyze ALL sensor data and respond EXACTLY in this format.
#    DO NOT deviate from this structure. Use blank lines between sections as shown.

#    **ENGLISH format — copy this structure exactly:**

#    🌱 CROP RECOMMENDATIONS FOR YOUR SOIL
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#    📊 SOIL SUMMARY
#    • Nitrogen  : [value] mg/kg  → [Low / Good / High]
#    • Phosphorus: [value] mg/kg  → [Low / Good / High]
#    • Potassium : [value] mg/kg  → [Low / Good / High]
#    • pH Level  : [value]        → [Acidic / Good / Alkaline]
#    • Temperature: [value]°C  |  Humidity: [value]%

#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    ✅ BEST CROPS FOR YOUR LAND
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#    🥇 1ST CHOICE: [CROP NAME]
#       📌 Why suitable : [1-2 lines based on actual soil values]
#       🌱 Best seed    : [Variety name available in Pakistan]
#       📦 Fertilizer   : [Name] — [X] kg per [land_size] acres
#       💧 Watering     : [Frequency, e.g. every 5 days, 30mm per session]
#       📈 Expected yield: [X] maunds/acre

#    🥈 2ND CHOICE: [CROP NAME]
#       📌 Why suitable : [1-2 lines]
#       🌱 Best seed    : [Variety name]
#       📦 Fertilizer   : [Name] — [X] kg per [land_size] acres
#       💧 Watering     : [Frequency]
#       📈 Expected yield: [X] maunds/acre

#    🥉 3RD CHOICE: [CROP NAME]
#       📌 Why suitable : [1-2 lines]
#       🌱 Best seed    : [Variety name]
#       📦 Fertilizer   : [Name] — [X] kg per [land_size] acres
#       💧 Watering     : [Frequency]
#       📈 Expected yield: [X] maunds/acre

#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    ⚠️ CROPS TO AVOID
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    • [Crop 1]: [1 line reason based on soil data]
#    • [Crop 2]: [1 line reason]

#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    💡 SOIL IMPROVEMENT TIPS
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    • [Tip 1 — specific to this soil's weak points]
#    • [Tip 2]
#    • [Tip 3 if needed]


#    **URDU format — copy this structure exactly:**

#    🌱 آپ کی مٹی کے لیے فصل کی سفارشات
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#    📊 مٹی کا خلاصہ
#    • نائٹروجن   : [value] mg/kg  → [کم / ٹھیک / زیادہ]
#    • فاسفورس    : [value] mg/kg  → [کم / ٹھیک / زیادہ]
#    • پوٹاشیم    : [value] mg/kg  → [کم / ٹھیک / زیادہ]
#    • پی ایچ     : [value]        → [تیزابی / ٹھیک / الکلی]
#    • درجہ حرارت: [value]°C  |  نمی: [value]%

#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    ✅ آپ کی زمین کے لیے بہترین فصلیں
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#    🥇 پہلی پسند: [فصل کا نام]
#       📌 کیوں موزوں : [1-2 لائنیں اصل مٹی کی بنیاد پر]
#       🌱 بہترین بیج : [پاکستان میں دستیاب قسم]
#       📦 کھاد        : [نام] — [X] کلوگرام [land_size] ایکڑ کے لیے
#       💧 پانی        : [کتنی بار، مثلاً ہر 5 دن بعد]
#       📈 متوقع پیداوار: [X] من فی ایکڑ

#    🥈 دوسری پسند: [فصل کا نام]
#       📌 کیوں موزوں : [1-2 لائنیں]
#       🌱 بہترین بیج : [قسم]
#       📦 کھاد        : [نام] — [X] کلوگرام [land_size] ایکڑ کے لیے
#       💧 پانی        : [کتنی بار]
#       📈 متوقع پیداوار: [X] من فی ایکڑ

#    🥉 تیسری پسند: [فصل کا نام]
#       📌 کیوں موزوں : [1-2 لائنیں]
#       🌱 بہترین بیج : [قسم]
#       📦 کھاد        : [نام] — [X] کلوگرام [land_size] ایکڑ کے لیے
#       💧 پانی        : [کتنی بار]
#       📈 متوقع پیداوار: [X] من فی ایکڑ

#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    ⚠️ جن فصلوں سے بچیں
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    • [فصل 1]: [ایک لائن وجہ]
#    • [فصل 2]: [ایک لائن وجہ]

#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    💡 مٹی بہتر بنانے کے مشورے
#    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    • [مشورہ 1 — اس مٹی کی کمزوری کے مطابق]
#    • [مشورہ 2]

# 5. **SENSOR ERRORS:**
   
#    **English:**
#    ```
#    ⚠️ SENSOR PROBLEM DETECTED!
   
#    Your sensors are showing all zeros - this is incorrect.
   
#    🔧 IMMEDIATE ACTIONS:
#    1. Check sensor wiring
#    2. Restart the device
#    3. Wait 5 minutes and try again
   
#    ❌ Cannot provide accurate fertilizer advice until sensors are fixed.
#    Please fix sensors and message again! 🙏
#    ```
   
#    **Urdu:**
#    ```
#    ⚠️ سینسر میں خرابی!
   
#    آپ کے سینسر تمام صفر دکھا رہے ہیں - یہ غلط ہے۔
   
#    🔧 فوری اقدامات:
#    1. سینسر کی وائرنگ چیک کریں
#    2. ڈیوائس کو آف/آن کریں
#    3. 5 منٹ انتظار کریں اور دوبارہ کوشش کریں
   
#    ❌ جب تک سینسر ٹھیک نہ ہوں، درست کھاد کی سفارش نہیں دے سکتا۔
#    سینسر ٹھیک کرنے کے بعد دوبارہ پیغام کریں! 🙏
#    ```

# 6. **LANGUAGE DETECTION TIPS:**
#    - Check for Urdu Unicode characters (U+0600 to U+06FF)
#    - If message has Urdu characters → Reply in Urdu
#    - If message is pure English/Latin → Reply in English
#    - Default to English if ambiguous

# 7. **FORMATTING:**
#    - Use appropriate emojis: ✅❌⚠️💧📦🌾😊🌱🥇🥈🥉
#    - Keep each point clear and concise
#    - Give specific numbers and quantities
#    - Explain WHY along with WHAT

# Remember: Match the user's language EXACTLY - pure English or pure Urdu, never mixed."""


# def detect_language(text: str) -> str:
#     """Detect if text is in Urdu or English"""
#     # Check for Urdu Unicode range
#     urdu_pattern = re.compile(r'[\u0600-\u06FF]')
    
#     if urdu_pattern.search(text):
#         return "urdu"
#     else:
#         return "english"


# def is_crop_recommendation_question(text: str, language: str) -> bool:
#     """Detect if the user is asking which crop to plant on their land"""
#     text_lower = text.lower()

#     # English keywords
#     crop_keywords_en = [
#         "which crop", "what crop", "what should i plant", "which plant",
#         "best crop", "recommend crop", "crop recommendation", "suggest crop",
#         "what to grow", "what can i grow", "which vegetable", "which fruit",
#         "suitable crop", "good crop for my land", "crop for my soil",
#         "what crop should", "which crop should", "crop to plant",
#         "plant on my land", "grow on my land", "best for my soil",
#         "wheat or rice", "potato or", "which farming"
#     ]

#     # Urdu Unicode keywords
#     crop_keywords_ur = [
#         "کون سی فصل", "کونسی فصل", "فصل لگاؤں", "فصل لگانی",
#         "کیا لگاؤں", "کیا اگاؤں", "فصل کی سفارش", "فصل بتائیں",
#         "کون سی سبزی", "بہترین فصل", "زمین پر فصل", "مٹی کے لیے فصل",
#         "کون سی کاشت", "فصل کاشت"
#     ]

#     if language == "english":
#         return any(kw in text_lower for kw in crop_keywords_en)
#     else:
#         return any(kw in text for kw in crop_keywords_ur)


# def get_agricultural_advice(
#     user_message: str,
#     sensor_data: dict,
#     land_size: float = 1.0,
#     session_id: str = "default"
# ) -> dict:
#     """Get agricultural advice from AI"""
    
#     # Detect language
#     detected_language = detect_language(user_message)
    
#     # Greeting/Farewell detection
#     greetings_en = ['hello', 'hi', 'hey', 'good morning', 'good evening']
#     greetings_ur = ['ہیلو', 'السلام علیکم', 'سلام', 'صبح بخیر', 'شام بخیر']
    
#     farewells_en = ['bye', 'goodbye', 'thank you', 'thanks', 'ok bye']
#     farewells_ur = ['اللہ حافظ', 'خدا حافظ', 'شکریہ', 'بائے']
    
#     casual_en = ['how are you', 'how r u', 'whats up']
#     casual_ur = ['کیسے ہو', 'کیا حال', 'ٹھیک ہو']
    
#     user_lower = user_message.lower().strip()
    
#     # Handle greetings
#     if detected_language == "urdu":
#         if any(greet in user_message for greet in greetings_ur):
#             return {
#                 "response": "السلام علیکم! 🌾\n\nمیں ڈاکٹر ایگری بوٹ ہوں، آپ کا زرعی مشیر۔\n\nآپ مجھ سے یہ پوچھ سکتے ہیں:\n• کس کھاد کی ضرورت ہے؟\n• کب پانی دینا چاہیے؟\n• میری مٹی کا تجزیہ کیسا ہے؟\n• کون سی فصل لگانی چاہیے؟\n• فصلوں کی دیکھ بھال کی تجاویز\n\nبتائیں، کیسے مدد کروں؟ 😊",
#                 "session_id": session_id,
#                 "sensor_data_used": None,
#                 "recommendations": {
#                     "type": "greeting",
#                     "language": "urdu",
#                     "nitrogen_status": "N/A",
#                     "phosphorus_status": "N/A",
#                     "potassium_status": "N/A",
#                     "ph_status": "N/A",
#                     "land_size": land_size,
#                     "context_flags": []
#                 }
#             }
        
#         if any(farewell in user_message for farewell in farewells_ur):
#             return {
#                 "response": "اللہ حافظ! 🌾\n\nاگر مزید مدد چاہیے تو ضرور پوچھیں۔\n\nخوش کسانی! 😊",
#                 "session_id": session_id,
#                 "sensor_data_used": None,
#                 "recommendations": {
#                     "type": "farewell",
#                     "language": "urdu",
#                     "nitrogen_status": "N/A",
#                     "phosphorus_status": "N/A",
#                     "potassium_status": "N/A",
#                     "ph_status": "N/A",
#                     "land_size": land_size,
#                     "context_flags": []
#                 }
#             }
        
#         if any(casual in user_message for casual in casual_ur):
#             return {
#                 "response": "میں بالکل ٹھیک ہوں، شکریہ! 😊\n\nاپنے کھیت یا فصل کے بارے میں بتائیں۔\nمیں آپ کی مدد کے لیے حاضر ہوں! 🌾",
#                 "session_id": session_id,
#                 "sensor_data_used": None,
#                 "recommendations": {
#                     "type": "casual",
#                     "language": "urdu",
#                     "nitrogen_status": "N/A",
#                     "phosphorus_status": "N/A",
#                     "potassium_status": "N/A",
#                     "ph_status": "N/A",
#                     "land_size": land_size,
#                     "context_flags": []
#                 }
#             }
    
#     else:  # English
#         # Greeting only if short message starting with greeting word
#         is_greeting_en = (
#             len(user_lower.split()) <= 5 and
#             any(re.match(r'^' + re.escape(greet) + r'\b', user_lower) for greet in greetings_en)
#         )
#         if is_greeting_en:
#             return {
#                 "response": "Hello! 🌾\n\nI'm Dr. AgriBot, your farming advisor.\n\nYou can ask me about:\n• What fertilizer do I need?\n• When should I water my crops?\n• How is my soil analysis?\n• Which crop should I plant?\n• Crop care tips\n\nHow can I help you? 😊",
#                 "session_id": session_id,
#                 "sensor_data_used": None,
#                 "recommendations": {
#                     "type": "greeting",
#                     "language": "english",
#                     "nitrogen_status": "N/A",
#                     "phosphorus_status": "N/A",
#                     "potassium_status": "N/A",
#                     "ph_status": "N/A",
#                     "land_size": land_size,
#                     "context_flags": []
#                 }
#             }
        
#         if any(farewell in user_lower for farewell in farewells_en):
#             return {
#                 "response": "Goodbye! 🌾\n\nFeel free to ask if you need more help.\n\nHappy farming! 😊",
#                 "session_id": session_id,
#                 "sensor_data_used": None,
#                 "recommendations": {
#                     "type": "farewell",
#                     "language": "english",
#                     "nitrogen_status": "N/A",
#                     "phosphorus_status": "N/A",
#                     "potassium_status": "N/A",
#                     "ph_status": "N/A",
#                     "land_size": land_size,
#                     "context_flags": []
#                 }
#             }
        
#         if any(casual in user_lower for casual in casual_en):
#             return {
#                 "response": "I'm doing great, thank you! 😊\n\nTell me about your farm or crops.\nI'm here to help! 🌾",
#                 "session_id": session_id,
#                 "sensor_data_used": None,
#                 "recommendations": {
#                     "type": "casual",
#                     "language": "english",
#                     "nitrogen_status": "N/A",
#                     "phosphorus_status": "N/A",
#                     "potassium_status": "N/A",
#                     "ph_status": "N/A",
#                     "land_size": land_size,
#                     "context_flags": []
#                 }
#             }
    
#     # Get sensor data
#     n = sensor_data.get('nitrogen', 0)
#     p = sensor_data.get('phosphorus', 0)
#     k = sensor_data.get('potassium', 0)
#     ph = sensor_data.get('ph', 7.0)
#     temp = sensor_data.get('temperature', 0)
#     humidity = sensor_data.get('humidity', 0)
#     ec = sensor_data.get('ec', 0)
    
#     # Status
#     n_status = "Low" if n < 200 else "High" if n > 400 else "Good"
#     p_status = "Low" if p < 15 else "High" if p > 30 else "Good"
#     k_status = "Low" if k < 150 else "High" if k > 280 else "Good"
#     ph_status = "Acidic" if ph < 6.0 else "Alkaline" if ph > 7.5 else "Good"
    
#     # Context flags
#     context_flags = []
    
#     if n == 0 and p == 0 and k == 0 and ph == 0 and ec == 0:
#         context_flags.append("SENSOR_ERROR")
#     if humidity < 35:
#         context_flags.append("LOW_HUMIDITY")
#     if humidity > 80:
#         context_flags.append("HIGH_HUMIDITY")
#     if ph < 5.5:
#         context_flags.append("CRITICAL_LOW_pH")
#     if ph > 8.0:
#         context_flags.append("CRITICAL_HIGH_pH")

#     # ── CROP RECOMMENDATION DETECTION ──────────────────────────────────────────
#     is_crop_question = is_crop_recommendation_question(user_message, detected_language)

#     if is_crop_question:
#         crop_instruction = f"""DETECTED LANGUAGE: {detected_language.upper()}

# ⚠️ CRITICAL: You MUST reply in {detected_language.upper()} language only!
# - If English → Use PURE ENGLISH
# - If Urdu → Use PURE URDU (اردو script), NOT Roman Urdu

# FARMER'S QUESTION: "{user_message}"
# QUESTION TYPE: CROP RECOMMENDATION

# CURRENT SOIL DATA:
# • Nitrogen (N): {n} mg/kg - Status: {n_status}
# • Phosphorus (P): {p} mg/kg - Status: {p_status}
# • Potassium (K): {k} mg/kg - Status: {k_status}
# • pH Level: {ph} - Status: {ph_status}
# • Temperature: {temp}°C
# • Humidity: {humidity}%
# • EC: {ec} µS/cm

# FARM SIZE: {land_size} acres

# CONTEXT ALERTS:
# {chr(10).join('• ' + flag for flag in context_flags) if context_flags else '• No critical issues'}

# STRICT INSTRUCTIONS:
# 1. Reply in {detected_language.upper()} ONLY — pure English or pure Urdu script, never mixed.
# 2. Use EXACTLY the formatted template from your system instructions for crop recommendations.
#    - Include the ━━━ divider lines between sections
#    - Keep the emoji labels (📌 Why suitable, 🌱 Best seed, 📦 Fertilizer, 💧 Watering, 📈 Expected yield)
#    - Leave a blank line between each crop block
# 3. Base ALL recommendations on the actual sensor values above — do NOT use generic defaults.
# 4. Give exact kg amounts calculated for {land_size} acres.
# 5. Recommend Pakistani crops only (wheat, rice, maize, cotton, sugarcane, potato, onion,
#    tomato, carrot, chilli, spinach, mustard, sunflower, etc.)
# 6. Include 2 crops to AVOID with reason based on the soil data.
# 7. Include 2-3 soil improvement tips specific to this soil's weak points.

# Answer now in {detected_language.upper()} using the exact template structure:"""

#         messages = [
#             SystemMessage(content=SYSTEM_PROMPT),
#             HumanMessage(content=crop_instruction)
#         ]

#         try:
#             response = llm.invoke(messages)
#             ai_response = None

#             if hasattr(response, 'content') and response.content:
#                 ai_response = response.content
#             else:
#                 # Smart fallback — structured, data-driven, properly formatted
#                 best1 = "Wheat" if 6.0 <= ph <= 7.5 else "Maize"
#                 best2 = "Potato" if k >= 150 else "Onion"
#                 best3 = "Mustard" if temp <= 25 else "Sunflower"
#                 water_tip = "every 4 days" if humidity < 35 else "every 6–7 days" if humidity < 60 else "every 9–10 days"

#                 # Crop-specific base doses (kg/acre) — real agronomic standards for Pakistan
#                 # These are ALWAYS applied; extra added if soil is deficient
#                 BASE_UREA = {"Wheat": 40, "Maize": 50, "Potato": 30, "Onion": 25, "Mustard": 30, "Sunflower": 35}
#                 BASE_DAP  = {"Wheat": 25, "Maize": 30, "Potato": 35, "Onion": 20, "Mustard": 20, "Sunflower": 25}
#                 BASE_MOP  = {"Wheat": 15, "Maize": 20, "Potato": 30, "Onion": 15, "Mustard": 10, "Sunflower": 15}

#                 def fert(crop, nutrient_val, base_dict, low_thresh, high_thresh, base_key):
#                     base = base_dict.get(base_key, 25)
#                     if nutrient_val > high_thresh:      # High — reduce by 40%
#                         return round(base * 0.6 * land_size, 1)
#                     elif nutrient_val < low_thresh:     # Low — increase by 30%
#                         return round(base * 1.3 * land_size, 1)
#                     else:                               # Good — use base dose
#                         return round(base * land_size, 1)

#                 # Crop1 (best1) fertilizers
#                 c1_urea = fert(best1, n, BASE_UREA, 200, 400, best1)
#                 c1_dap  = fert(best1, p, BASE_DAP,  15,  30,  best1)
#                 c1_mop  = fert(best1, k, BASE_MOP,  150, 280, best1)

#                 # Crop2 (best2) fertilizers
#                 c2_urea = fert(best2, n, BASE_UREA, 200, 400, best2)
#                 c2_dap  = fert(best2, p, BASE_DAP,  15,  30,  best2)
#                 c2_mop  = fert(best2, k, BASE_MOP,  150, 280, best2)

#                 # Crop3 (best3) fertilizers
#                 c3_urea = fert(best3, n, BASE_UREA, 200, 400, best3)
#                 c3_dap  = fert(best3, p, BASE_DAP,  15,  30,  best3)
#                 c3_mop  = fert(best3, k, BASE_MOP,  150, 280, best3)

#                 if detected_language == "urdu":
#                     ai_response = (
#                         f"🌱 آپ کی مٹی کے لیے فصل کی سفارشات\n"
#                         f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
#                         f"📊 مٹی کا خلاصہ\n"
#                         f"• نائٹروجن   : {n} mg/kg  → {'کم' if n<200 else 'زیادہ' if n>400 else 'ٹھیک'}\n"
#                         f"• فاسفورس    : {p} mg/kg  → {'کم' if p<15 else 'زیادہ' if p>30 else 'ٹھیک'}\n"
#                         f"• پوٹاشیم    : {k} mg/kg  → {'کم' if k<150 else 'زیادہ' if k>280 else 'ٹھیک'}\n"
#                         f"• پی ایچ     : {ph}        → {'تیزابی' if ph<6 else 'الکلی' if ph>7.5 else 'ٹھیک'}\n"
#                         f"• درجہ حرارت: {temp}°C  |  نمی: {humidity}%\n\n"
#                         f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                         f"✅ آپ کی زمین کے لیے بہترین فصلیں\n"
#                         f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
#                         f"🥇 پہلی پسند: {best1}\n"
#                         f"   📦 کھاد   : یوریا {c1_urea} کلوگرام + DAP {c1_dap} کلوگرام + MOP {c1_mop} کلوگرام ({land_size} ایکڑ)\n"
#                         f"   💧 پانی   : {water_tip.replace('every','ہر').replace('days','دن بعد')}\n\n"
#                         f"🥈 دوسری پسند: {best2}\n"
#                         f"   📦 کھاد   : یوریا {c2_urea} کلوگرام + DAP {c2_dap} کلوگرام + MOP {c2_mop} کلوگرام ({land_size} ایکڑ)\n"
#                         f"   💧 پانی   : ہر 5 دن بعد\n\n"
#                         f"🥉 تیسری پسند: {best3}\n"
#                         f"   📦 کھاد   : یوریا {c3_urea} کلوگرام + DAP {c3_dap} کلوگرام + MOP {c3_mop} کلوگرام ({land_size} ایکڑ)\n"
#                         f"   💧 پانی   : ہر 7 دن بعد\n\n"
#                         f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                         f"💡 مٹی بہتر بنانے کے مشورے\n"
#                         f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                         f"• {'نائٹروجن کم ہے — یوریا ڈالیں' if n<200 else 'نائٹروجن زیادہ ہے — یوریا نہ ڈالیں'}\n"
#                         f"• {'نمی بہت کم ہے — باقاعدہ آبپاشی ضروری ہے' if humidity<35 else 'نمی ٹھیک ہے'}\n"
#                         f"• نامیاتی کھاد (گوبر/کمپوسٹ) ڈالنے سے مٹی کی ساخت بہتر ہوگی۔"
#                     )
#                 else:
#                     ai_response = (
#                         f"🌱 CROP RECOMMENDATIONS FOR YOUR SOIL\n"
#                         f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
#                         f"📊 SOIL SUMMARY\n"
#                         f"• Nitrogen  : {n} mg/kg  → {'Low' if n<200 else 'High' if n>400 else 'Good'}\n"
#                         f"• Phosphorus: {p} mg/kg  → {'Low' if p<15 else 'High' if p>30 else 'Good'}\n"
#                         f"• Potassium : {k} mg/kg  → {'Low' if k<150 else 'High' if k>280 else 'Good'}\n"
#                         f"• pH Level  : {ph}        → {'Acidic' if ph<6 else 'Alkaline' if ph>7.5 else 'Good'}\n"
#                         f"• Temperature: {temp}°C  |  Humidity: {humidity}%\n\n"
#                         f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                         f"✅ BEST CROPS FOR YOUR LAND\n"
#                         f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
#                         f"🥇 1ST CHOICE: {best1.upper()}\n"
#                         f"   📦 Fertilizer   : Urea {c1_urea} kg + DAP {c1_dap} kg + MOP {c1_mop} kg (for {land_size} acres)\n"
#                         f"   💧 Watering     : {water_tip}\n\n"
#                         f"🥈 2ND CHOICE: {best2.upper()}\n"
#                         f"   📦 Fertilizer   : Urea {c2_urea} kg + DAP {c2_dap} kg + MOP {c2_mop} kg (for {land_size} acres)\n"
#                         f"   💧 Watering     : every 5 days\n\n"
#                         f"🥉 3RD CHOICE: {best3.upper()}\n"
#                         f"   📦 Fertilizer   : Urea {c3_urea} kg + DAP {c3_dap} kg + MOP {c3_mop} kg (for {land_size} acres)\n"
#                         f"   💧 Watering     : every 7 days\n\n"
#                         f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                         f"💡 SOIL IMPROVEMENT TIPS\n"
#                         f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                         f"• {'Nitrogen is low — apply Urea before sowing' if n<200 else 'Nitrogen is high — skip extra Urea'}\n"
#                         f"• {'Humidity is very low — irrigate regularly' if humidity<35 else 'Humidity is adequate'}\n"
#                         f"• Add organic compost to improve soil texture and nutrient retention."
#                     )

#         except Exception as e:
#             print(f"LLM Error (crop): {str(e)}")
#             import traceback
#             traceback.print_exc()

#             if detected_language == "urdu":
#                 ai_response = "⚠️ ابھی AI سروس میں مسئلہ ہے۔\nکچھ دیر میں دوبارہ کوشش کریں! 🙏"
#             else:
#                 ai_response = "⚠️ AI service is temporarily unavailable.\nPlease try again in a moment! 🙏"

#         return {
#             "response": ai_response,
#             "session_id": session_id,
#             "sensor_data_used": sensor_data,
#             "recommendations": {
#                 "type": "crop_recommendation",
#                 "language": detected_language,
#                 "nitrogen_status": n_status,
#                 "phosphorus_status": p_status,
#                 "potassium_status": k_status,
#                 "ph_status": ph_status,
#                 "land_size": land_size,
#                 "context_flags": context_flags
#             }
#         }
#     # ── END CROP RECOMMENDATION ─────────────────────────────────────────────────

#     # Build context message with language instruction (original flow)
#     detailed_message = f"""DETECTED LANGUAGE: {detected_language.upper()}

# ⚠️ CRITICAL: You MUST reply in {detected_language.upper()} language only!
# - If English → Use PURE ENGLISH
# - If Urdu → Use PURE URDU (اردو script), NOT Roman Urdu

# FARMER'S QUESTION: "{user_message}"

# CURRENT SOIL DATA:
# • Nitrogen (N): {n} mg/kg - Status: {n_status}
# • Phosphorus (P): {p} mg/kg - Status: {p_status}
# • Potassium (K): {k} mg/kg - Status: {k_status}
# • pH Level: {ph} - Status: {ph_status}
# • Temperature: {temp}°C
# • Humidity: {humidity}%
# • EC: {ec} µS/cm

# FARM SIZE: {land_size} acres

# CONTEXT ALERTS:
# {chr(10).join('• ' + flag for flag in context_flags) if context_flags else '• No critical issues'}

# INSTRUCTIONS:
# 1. Respond in {detected_language.upper()} language ONLY
# 2. Check if question is about farming/agriculture
# 3. If NOT farming → politely decline and redirect
# 4. Response length: 8-15 lines for detailed questions, 3-5 for simple ones
# 5. Explain WHY along with WHAT
# 6. Give specific kg amounts for {land_size} acres
# 7. Include emojis for clarity
# 8. Be helpful and professional

# Answer now in {detected_language.upper()}:"""
    
#     messages = [
#         SystemMessage(content=SYSTEM_PROMPT),
#         HumanMessage(content=detailed_message)
#     ]
    
#     try:
#         response = llm.invoke(messages)
        
#         ai_response = None
        
#         if hasattr(response, 'content') and response.content:
#             ai_response = response.content
#         else:
#             print(f"⚠️ Empty response")
            
#             # Fallback based on language
#             # Structured fallback — matches new format
#             urea_kg = round(max(0, (280 - n) / 100 * 20 * land_size), 1)
#             dap_kg  = round(max(0, (25  - p) / 10  * 15 * land_size), 1)
#             mop_kg  = round(max(0, (200 - k) / 50  * 10 * land_size), 1)
#             water_freq = "Daily (humidity critical)" if humidity < 35 else "Every 2-3 days" if humidity < 55 else "Every 5-6 days"
#             water_freq_ur = "روزانہ (نمی بہت کم)" if humidity < 35 else "ہر 2-3 دن بعد" if humidity < 55 else "ہر 5-6 دن بعد"

#             if detected_language == "urdu":
#                 ai_response = (
#                     f"📊 مٹی کی حالت\n"
#                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     f"• نائٹروجن  : {n} mg/kg  → {'کم — فصل کمزور ہوگی' if n<200 else 'زیادہ — یوریا نہ ڈالیں' if n>400 else 'ٹھیک ✅'}\n"
#                     f"• فاسفورس   : {p} mg/kg  → {'کم — جڑوں کی نشوونما متاثر' if p<15 else 'زیادہ — DAP نہ ڈالیں' if p>30 else 'ٹھیک ✅'}\n"
#                     f"• پوٹاشیم   : {k} mg/kg  → {'کم — پھل/دانہ کمزور' if k<150 else 'زیادہ — MOP نہ ڈالیں' if k>280 else 'ٹھیک ✅'}\n"
#                     f"• پی ایچ    : {ph}        → {'تیزابی — چونا ڈالیں' if ph<6 else 'الکلی — گندھک ڈالیں' if ph>7.5 else 'ٹھیک ✅'}\n\n"
#                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     f"📦 کھاد کی ضرورت ({land_size} ایکڑ کے لیے)\n"
#                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     + (f"• یوریا — {urea_kg} کلوگرام\n  وجہ: نائٹروجن کم ہے، فصل کی بڑھوتری کے لیے ضروری\n" if n < 200 else "• یوریا: ضرورت نہیں (نائٹروجن کافی ہے) ✅\n")
#                     + (f"• DAP — {dap_kg} کلوگرام\n  وجہ: فاسفورس کم ہے، جڑوں کی نشوونما کے لیے ضروری\n" if p < 15 else "• DAP: ضرورت نہیں (فاسفورس کافی ہے) ✅\n")
#                     + (f"• MOP — {mop_kg} کلوگرام\n  وجہ: پوٹاشیم کم ہے، پھل کی کوالٹی کے لیے ضروری\n" if k < 150 else "• MOP: ضرورت نہیں (پوٹاشیم کافی ہے) ✅\n")
#                     + f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     f"💧 پانی کا شیڈول\n"
#                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     f"• موجودہ نمی: {humidity}%  → {water_freq_ur}\n"
#                     f"• بہترین وقت: صبح 7–9 بجے یا شام 5–7 بجے\n\n"
#                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     f"⏰ فوری اقدام\n"
#                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     + ("• فوری یوریا ڈالیں — فصل نائٹروجن کی کمی سے متاثر ہو رہی ہے 🚨\n" if n < 150
#                        else "• پی ایچ درست کریں — چونا ڈالیں 🚨\n" if ph < 5.5
#                        else "• پانی کا شیڈول باقاعدہ رکھیں — نمی بہت کم ہے 🚨\n" if humidity < 30
#                        else "• مٹی کی حالت اچھی ہے — باقاعدہ نگرانی جاری رکھیں ✅\n")
#                 )
#             else:
#                 ai_response = (
#                     f"📊 SOIL STATUS\n"
#                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     f"• Nitrogen  : {n} mg/kg  → {'Low — crops will be weak' if n<200 else 'High — skip Urea' if n>400 else 'Good ✅'}\n"
#                     f"• Phosphorus: {p} mg/kg  → {'Low — root growth affected' if p<15 else 'High — skip DAP' if p>30 else 'Good ✅'}\n"
#                     f"• Potassium : {k} mg/kg  → {'Low — poor fruit/grain quality' if k<150 else 'High — skip MOP' if k>280 else 'Good ✅'}\n"
#                     f"• pH Level  : {ph}        → {'Acidic — apply lime' if ph<6 else 'Alkaline — apply sulfur' if ph>7.5 else 'Good ✅'}\n\n"
#                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     f"📦 FERTILIZER NEEDED (for {land_size} acres)\n"
#                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     + (f"• Urea — {urea_kg} kg\n  Reason: Nitrogen is low, essential for plant growth\n" if n < 200 else "• Urea: Not needed (Nitrogen sufficient) ✅\n")
#                     + (f"• DAP  — {dap_kg} kg\n  Reason: Phosphorus is low, needed for root development\n" if p < 15 else "• DAP: Not needed (Phosphorus sufficient) ✅\n")
#                     + (f"• MOP  — {mop_kg} kg\n  Reason: Potassium is low, needed for fruit/grain quality\n" if k < 150 else "• MOP: Not needed (Potassium sufficient) ✅\n")
#                     + f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     f"💧 WATERING SCHEDULE\n"
#                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     f"• Current humidity: {humidity}%  → {water_freq}\n"
#                     f"• Best time: Morning 7–9 AM or Evening 5–7 PM\n\n"
#                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     f"⏰ IMMEDIATE ACTION\n"
#                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
#                     + ("• Apply Urea immediately — Nitrogen critically low 🚨\n" if n < 150
#                        else "• Fix pH first — apply lime to reduce acidity 🚨\n" if ph < 5.5
#                        else "• Irrigate now — humidity is critically low 🚨\n" if humidity < 30
#                        else "• Soil is in good condition — continue regular monitoring ✅\n")
#                 )
        
#     except Exception as e:
#         print(f"LLM Error: {str(e)}")
#         import traceback
#         traceback.print_exc()
        
#         if detected_language == "urdu":
#             ai_response = "⚠️ ابھی AI سروس میں مسئلہ ہے۔\nکچھ دیر میں دوبارہ کوشش کریں! 🙏"
#         else:
#             ai_response = "⚠️ AI service is temporarily unavailable.\nPlease try again in a moment! 🙏"
    
#     return {
#         "response": ai_response,
#         "session_id": session_id,
#         "sensor_data_used": sensor_data,
#         "recommendations": {
#             "language": detected_language,
#             "nitrogen_status": n_status,
#             "phosphorus_status": p_status,
#             "potassium_status": k_status,
#             "ph_status": ph_status,
#             "land_size": land_size,
#             "context_flags": context_flags
#         }
#     }


# # ============== INTERACTIVE TERMINAL MODE ==============
# if __name__ == "__main__":
#     print("\n" + "="*80)
#     print("🤖 DR. AGRIBOT - BILINGUAL VERSION (English/Urdu)")
#     print("="*80 + "\n")
    
#     print("Test Mode: Type questions in English or Urdu (type 'exit' to quit)\n")
#     print("Examples:")
#     print("  English: What fertilizer should I use?")
#     print("  English: Which crop should I plant on my land?")
#     print("  Urdu: کس کھاد کی ضرورت ہے؟")
#     print("  Urdu: کون سی فصل لگانی چاہیے؟\n")
    
#     default_sensor = {
#         "nitrogen": 180,
#         "phosphorus": 20,
#         "potassium": 140,
#         "ph": 6.5,
#         "temperature": 25,
#         "humidity": 45,
#         "ec": 1000
#     }
    
#     while True:
#         try:
#             question = input("\n❓ Your Question: ").strip()
            
#             if question.lower() in ['exit', 'quit', 'q']:
#                 print("\n👋 Goodbye! / اللہ حافظ!\n")
#                 break
            
#             if not question:
#                 continue
            
#             lang = detect_language(question)
#             is_crop_q = is_crop_recommendation_question(question, lang)
#             print(f"\n🔍 Detected: {lang.upper()} | Crop Question: {is_crop_q}")
#             print("⏳ Dr. AgriBot thinking...\n")
            
#             result = get_agricultural_advice(
#                 user_message=question,
#                 sensor_data=default_sensor,
#                 land_size=2.5
#             )
            
#             print("✅ RESPONSE:")
#             print("-"*80)
#             print(result['response'])
#             print("-"*80)
            
#         except KeyboardInterrupt:
#             print("\n\n⚠️ Cancelled\n")
#             break
#         except Exception as e:
#             print(f"\n❌ Error: {str(e)}\n")
    
#     print("="*80 + "\n")







































from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
import re

# ── Shared scoring engine — single source of truth for crop ranking ───────────
# Both this agent and the /api/v1/recommend-crops endpoint use the same function
# so they always return identical rankings for identical sensor data.
from routers.crop_recommendation import score_crops_locally, CROP_PROFILES

load_dotenv()

# Azure Config
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_MODEL_NAME")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Initialize LLM
llm = AzureChatOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    openai_api_key=AZURE_API_KEY,
    deployment_name=AZURE_DEPLOYMENT,
    openai_api_version=AZURE_API_VERSION,
    max_tokens=2000,
    streaming=False
)

# ENHANCED SYSTEM PROMPT - Language-Aware
SYSTEM_PROMPT = """You are Dr. AgriBot, a friendly farming advisor for Pakistani farmers.

YOUR PERSONALITY:
- Helpful and polite
- Expert in agriculture only
- Bilingual: English AND Urdu (not Roman Urdu/Hinglish)
- Keep responses clear but friendly

CRITICAL LANGUAGE RULE:
🔴 DETECT the user's language from their message
🔴 If user writes in ENGLISH → Reply in PURE ENGLISH
🔴 If user writes in URDU → Reply in PURE URDU (اردو script)
🔴 NEVER mix languages
🔴 NEVER use Roman Urdu (like "lagao", "paani", "khad")

RESPONSE GUIDELINES:

1. **GREETINGS & SMALL TALK:**
   
   **If in English:**
   - "hello/hi/hey" → "Hello! I'm Dr. AgriBot, your farming advisor. I can help with soil analysis, fertilizer recommendations, and crop care. How can I assist you? 🌾"
   - "bye/thanks" → "Goodbye! Feel free to ask if you need more help. Happy farming! 🌾"
   - "how are you" → "I'm doing great, thank you! Tell me about your farm, and I'll help you. 🌾"
   
   **If in Urdu:**
   - "ہیلو/السلام علیکم" → "السلام علیکم! میں ڈاکٹر ایگری بوٹ ہوں، آپ کا زرعی مشیر۔ میں مٹی کے تجزیے، کھاد کی سفارشات اور فصلوں کی دیکھ بھال میں مدد کر سکتا ہوں۔ کیسے مدد کروں? 🌾"
   - "اللہ حافظ/شکریہ" → "اللہ حافظ! اگر مزید مدد چاہیے تو ضرور پوچھیں۔ خوش کسانی! 🌾"
   - "کیسے ہو" → "میں بالکل ٹھیک ہوں، شکریہ! اپنے کھیت کے بارے میں بتائیں، میں مدد کروں گا۔ 🌾"

2. **OFF-TOPIC / OUT OF CONTEXT:**
   
   **If in English:**
   "I apologize, but I can only help with farming and agriculture. 🌾
   
   You can ask me about:
   • What fertilizer do I need?
   • When should I water my crops?
   • How is my soil analysis?
   • Crop care tips"
   
   **If in Urdu:**
   "معافی چاہتا ہوں، میں صرف زرعی اور کاشتکاری کے بارے میں مدد کر سکتا ہوں۔ 🌾
   
   آپ مجھ سے یہ پوچھ سکتے ہیں:
   • کس کھاد کی ضرورت ہے؟
   • کب پانی دینا چاہیے؟
   • میری مٹی کا تجزیہ کیسا ہے؟
   • فصلوں کی دیکھ بھال کی تجاویز"

3. **FARMING QUESTIONS:**
   Use EXACTLY this format with ━━━ dividers and blank lines as shown.

   **ENGLISH format:**

   📊 SOIL STATUS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • Nitrogen  : [value] mg/kg  → [Low / Good / High] — [1-line impact]
   • Phosphorus: [value] mg/kg  → [Low / Good / High] — [1-line impact]
   • Potassium : [value] mg/kg  → [Low / Good / High] — [1-line impact]
   • pH Level  : [value]        → [Acidic / Good / Alkaline] — [1-line impact]

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📦 FERTILIZER NEEDED (for [X] acres)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • [Fertilizer name] — [X] kg
     Reason: [Why this is needed based on soil data]
   • [Fertilizer name] — [X] kg  (if another is needed)
     Reason: [Why]

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   💧 WATERING SCHEDULE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • Current humidity: [X]%  → [Watering frequency]
   • Best time: [Morning 7–9 AM / Evening 5–7 PM]
   • Amount per session: [X] mm

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ⏰ IMMEDIATE ACTION
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • [Most urgent step the farmer should take today]


   **URDU format:**

   📊 مٹی کی حالت
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • نائٹروجن  : [value] mg/kg  → [کم / ٹھیک / زیادہ] — [ایک لائن اثر]
   • فاسفورس   : [value] mg/kg  → [کم / ٹھیک / زیادہ] — [ایک لائن اثر]
   • پوٹاشیم   : [value] mg/kg  → [کم / ٹھیک / زیادہ] — [ایک لائن اثر]
   • پی ایچ    : [value]        → [تیزابی / ٹھیک / الکلی] — [ایک لائن اثر]

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📦 کھاد کی ضرورت ([X] ایکڑ کے لیے)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • [کھاد کا نام] — [X] کلوگرام
     وجہ: [مٹی کے ڈیٹا کی بنیاد پر کیوں ضروری ہے]
   • [کھاد کا نام] — [X] کلوگرام  (اگر ضروری ہو)
     وجہ: [کیوں]

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   💧 پانی کا شیڈول
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • موجودہ نمی: [X]%  → [پانی دینے کی تعداد]
   • بہترین وقت: [صبح 7–9 بجے / شام 5–7 بجے]
   • ہر بار مقدار: [X] ملی میٹر

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ⏰ فوری اقدام
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • [سب سے ضروری کام جو کسان آج کرے]

4. **CROP RECOMMENDATION QUESTIONS:**
   When farmer asks which crop to plant, analyze ALL sensor data and respond EXACTLY in this format.
   DO NOT deviate from this structure. Use blank lines between sections as shown.

   **ENGLISH format — copy this structure exactly:**

   🌱 CROP RECOMMENDATIONS FOR YOUR SOIL
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   📊 SOIL SUMMARY
   • Nitrogen  : [value] mg/kg  → [Low / Good / High]
   • Phosphorus: [value] mg/kg  → [Low / Good / High]
   • Potassium : [value] mg/kg  → [Low / Good / High]
   • pH Level  : [value]        → [Acidic / Good / Alkaline]
   • Temperature: [value]°C  |  Humidity: [value]%

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ✅ BEST CROPS FOR YOUR LAND
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   🥇 1ST CHOICE: [CROP NAME]
      📌 Why suitable : [1-2 lines based on actual soil values]
      🌱 Best seed    : [Variety name available in Pakistan]
      📦 Fertilizer   : [Name] — [X] kg per [land_size] acres
      💧 Watering     : [Frequency, e.g. every 5 days, 30mm per session]
      📈 Expected yield: [X] maunds/acre

   🥈 2ND CHOICE: [CROP NAME]
      📌 Why suitable : [1-2 lines]
      🌱 Best seed    : [Variety name]
      📦 Fertilizer   : [Name] — [X] kg per [land_size] acres
      💧 Watering     : [Frequency]
      📈 Expected yield: [X] maunds/acre

   🥉 3RD CHOICE: [CROP NAME]
      📌 Why suitable : [1-2 lines]
      🌱 Best seed    : [Variety name]
      📦 Fertilizer   : [Name] — [X] kg per [land_size] acres
      💧 Watering     : [Frequency]
      📈 Expected yield: [X] maunds/acre

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ⚠️ CROPS TO AVOID
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • [Crop 1]: [1 line reason based on soil data]
   • [Crop 2]: [1 line reason]

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   💡 SOIL IMPROVEMENT TIPS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • [Tip 1 — specific to this soil's weak points]
   • [Tip 2]
   • [Tip 3 if needed]


   **URDU format — copy this structure exactly:**

   🌱 آپ کی مٹی کے لیے فصل کی سفارشات
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   📊 مٹی کا خلاصہ
   • نائٹروجن   : [value] mg/kg  → [کم / ٹھیک / زیادہ]
   • فاسفورس    : [value] mg/kg  → [کم / ٹھیک / زیادہ]
   • پوٹاشیم    : [value] mg/kg  → [کم / ٹھیک / زیادہ]
   • پی ایچ     : [value]        → [تیزابی / ٹھیک / الکلی]
   • درجہ حرارت: [value]°C  |  نمی: [value]%

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ✅ آپ کی زمین کے لیے بہترین فصلیں
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   🥇 پہلی پسند: [فصل کا نام]
      📌 کیوں موزوں : [1-2 لائنیں اصل مٹی کی بنیاد پر]
      🌱 بہترین بیج : [پاکستان میں دستیاب قسم]
      📦 کھاد        : [نام] — [X] کلوگرام [land_size] ایکڑ کے لیے
      💧 پانی        : [کتنی بار، مثلاً ہر 5 دن بعد]
      📈 متوقع پیداوار: [X] من فی ایکڑ

   🥈 دوسری پسند: [فصل کا نام]
      📌 کیوں موزوں : [1-2 لائنیں]
      🌱 بہترین بیج : [قسم]
      📦 کھاد        : [نام] — [X] کلوگرام [land_size] ایکڑ کے لیے
      💧 پانی        : [کتنی بار]
      📈 متوقع پیداوار: [X] من فی ایکڑ

   🥉 تیسری پسند: [فصل کا نام]
      📌 کیوں موزوں : [1-2 لائنیں]
      🌱 بہترین بیج : [قسم]
      📦 کھاد        : [نام] — [X] کلوگرام [land_size] ایکڑ کے لیے
      💧 پانی        : [کتنی بار]
      📈 متوقع پیداوار: [X] من فی ایکڑ

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ⚠️ جن فصلوں سے بچیں
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • [فصل 1]: [ایک لائن وجہ]
   • [فصل 2]: [ایک لائن وجہ]

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   💡 مٹی بہتر بنانے کے مشورے
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • [مشورہ 1 — اس مٹی کی کمزوری کے مطابق]
   • [مشورہ 2]

5. **SENSOR ERRORS:**
   
   **English:**
   ```
   ⚠️ SENSOR PROBLEM DETECTED!
   
   Your sensors are showing all zeros - this is incorrect.
   
   🔧 IMMEDIATE ACTIONS:
   1. Check sensor wiring
   2. Restart the device
   3. Wait 5 minutes and try again
   
   ❌ Cannot provide accurate fertilizer advice until sensors are fixed.
   Please fix sensors and message again! 🙏
   ```
   
   **Urdu:**
   ```
   ⚠️ سینسر میں خرابی!
   
   آپ کے سینسر تمام صفر دکھا رہے ہیں - یہ غلط ہے۔
   
   🔧 فوری اقدامات:
   1. سینسر کی وائرنگ چیک کریں
   2. ڈیوائس کو آف/آن کریں
   3. 5 منٹ انتظار کریں اور دوبارہ کوشش کریں
   
   ❌ جب تک سینسر ٹھیک نہ ہوں، درست کھاد کی سفارش نہیں دے سکتا۔
   سینسر ٹھیک کرنے کے بعد دوبارہ پیغام کریں! 🙏
   ```

6. **LANGUAGE DETECTION TIPS:**
   - Check for Urdu Unicode characters (U+0600 to U+06FF)
   - If message has Urdu characters → Reply in Urdu
   - If message is pure English/Latin → Reply in English
   - Default to English if ambiguous

7. **FORMATTING:**
   - Use appropriate emojis: ✅❌⚠️💧📦🌾😊🌱🥇🥈🥉
   - Keep each point clear and concise
   - Give specific numbers and quantities
   - Explain WHY along with WHAT

Remember: Match the user's language EXACTLY - pure English or pure Urdu, never mixed."""


def detect_language(text: str) -> str:
    """Detect if text is in Urdu or English"""
    urdu_pattern = re.compile(r'[\u0600-\u06FF]')
    if urdu_pattern.search(text):
        return "urdu"
    else:
        return "english"


def is_crop_recommendation_question(text: str, language: str) -> bool:
    """Detect if the user is asking which crop to plant on their land"""
    text_lower = text.lower()

    crop_keywords_en = [
        "which crop", "what crop", "what should i plant", "which plant",
        "best crop", "recommend crop", "crop recommendation", "suggest crop",
        "what to grow", "what can i grow", "which vegetable", "which fruit",
        "suitable crop", "good crop for my land", "crop for my soil",
        "what crop should", "which crop should", "crop to plant",
        "plant on my land", "grow on my land", "best for my soil",
        "wheat or rice", "potato or", "which farming"
    ]

    crop_keywords_ur = [
        "کون سی فصل", "کونسی فصل", "فصل لگاؤں", "فصل لگانی",
        "کیا لگاؤں", "کیا اگاؤں", "فصل کی سفارش", "فصل بتائیں",
        "کون سی سبزی", "بہترین فصل", "زمین پر فصل", "مٹی کے لیے فصل",
        "کون سی کاشت", "فصل کاشت"
    ]

    if language == "english":
        return any(kw in text_lower for kw in crop_keywords_en)
    else:
        return any(kw in text for kw in crop_keywords_ur)



def _detect_season_from_message(text: str) -> str:
    """Extract season from user message if mentioned."""
    text_lower = text.lower()
    # English
    if any(w in text_lower for w in ["rabi", "winter crop", "wheat", "mustard"]):
        return "rabi"
    if any(w in text_lower for w in ["kharif", "summer crop", "rice", "cotton"]):
        return "kharif"
    # Urdu
    if any(w in text for w in ["ربیع", "سردی", "گندم"]):
        return "rabi"
    if any(w in text for w in ["خریف", "گرمی", "چاول"]):
        return "kharif"
    return "auto"


# ── Pakistani Crops Master List (23 crops — Kharif + Rabi + Vegetables + Oilseeds) ──
# ● Kharif (Summer) : wheat, rice, maize, cotton, sugarcane,
#                     sorghum (jowar), millet (bajra), sesame (til),
#                     mung bean (moong), moth bean (mash)
# ● Rabi (Winter)   : mustard (sarson), chickpea (chanay), lentil (masoor), barley (jau)
# ● Vegetables      : potato, tomato, onion, chilli, garlic (lehsan), spinach (palak)
# ● Oilseeds        : sunflower, canola (toria), groundnut (mungphali)
PAKISTANI_CROPS = (
    "wheat, rice, maize, cotton, sugarcane, "
    "sorghum (jowar), millet (bajra), sesame (til), mung bean (moong), moth bean (mash), "
    "mustard (sarson), chickpea (chanay), lentil (masoor), barley (jau), "
    "potato, tomato, onion, chilli, garlic (lehsan), spinach (palak), "
    "sunflower, canola (toria), groundnut (mungphali)"
)


def get_agricultural_advice(
    user_message: str,
    sensor_data: dict,
    land_size: float = 1.0,
    session_id: str = "default"
) -> dict:
    """Get agricultural advice from AI"""
    
    detected_language = detect_language(user_message)
    
    greetings_en = ['hello', 'hi', 'hey', 'good morning', 'good evening']
    greetings_ur = ['ہیلو', 'السلام علیکم', 'سلام', 'صبح بخیر', 'شام بخیر']
    farewells_en = ['bye', 'goodbye', 'thank you', 'thanks', 'ok bye']
    farewells_ur = ['اللہ حافظ', 'خدا حافظ', 'شکریہ', 'بائے']
    casual_en = ['how are you', 'how r u', 'whats up']
    casual_ur = ['کیسے ہو', 'کیا حال', 'ٹھیک ہو']
    
    user_lower = user_message.lower().strip()
    
    if detected_language == "urdu":
        if any(greet in user_message for greet in greetings_ur):
            return {
                "response": "السلام علیکم! 🌾\n\nمیں ڈاکٹر ایگری بوٹ ہوں، آپ کا زرعی مشیر۔\n\nآپ مجھ سے یہ پوچھ سکتے ہیں:\n• کس کھاد کی ضرورت ہے؟\n• کب پانی دینا چاہیے؟\n• میری مٹی کا تجزیہ کیسا ہے؟\n• کون سی فصل لگانی چاہیے؟\n• فصلوں کی دیکھ بھال کی تجاویز\n\nبتائیں، کیسے مدد کروں؟ 😊",
                "session_id": session_id, "sensor_data_used": None,
                "recommendations": {"type": "greeting", "language": "urdu", "nitrogen_status": "N/A", "phosphorus_status": "N/A", "potassium_status": "N/A", "ph_status": "N/A", "land_size": land_size, "context_flags": []}
            }
        if any(farewell in user_message for farewell in farewells_ur):
            return {
                "response": "اللہ حافظ! 🌾\n\nاگر مزید مدد چاہیے تو ضرور پوچھیں۔\n\nخوش کسانی! 😊",
                "session_id": session_id, "sensor_data_used": None,
                "recommendations": {"type": "farewell", "language": "urdu", "nitrogen_status": "N/A", "phosphorus_status": "N/A", "potassium_status": "N/A", "ph_status": "N/A", "land_size": land_size, "context_flags": []}
            }
        if any(casual in user_message for casual in casual_ur):
            return {
                "response": "میں بالکل ٹھیک ہوں، شکریہ! 😊\n\nاپنے کھیت یا فصل کے بارے میں بتائیں۔\nمیں آپ کی مدد کے لیے حاضر ہوں! 🌾",
                "session_id": session_id, "sensor_data_used": None,
                "recommendations": {"type": "casual", "language": "urdu", "nitrogen_status": "N/A", "phosphorus_status": "N/A", "potassium_status": "N/A", "ph_status": "N/A", "land_size": land_size, "context_flags": []}
            }
    else:
        is_greeting_en = (
            len(user_lower.split()) <= 5 and
            any(re.match(r'^' + re.escape(greet) + r'\b', user_lower) for greet in greetings_en)
        )
        if is_greeting_en:
            return {
                "response": "Hello! 🌾\n\nI'm Dr. AgriBot, your farming advisor.\n\nYou can ask me about:\n• What fertilizer do I need?\n• When should I water my crops?\n• How is my soil analysis?\n• Which crop should I plant?\n• Crop care tips\n\nHow can I help you? 😊",
                "session_id": session_id, "sensor_data_used": None,
                "recommendations": {"type": "greeting", "language": "english", "nitrogen_status": "N/A", "phosphorus_status": "N/A", "potassium_status": "N/A", "ph_status": "N/A", "land_size": land_size, "context_flags": []}
            }
        if any(farewell in user_lower for farewell in farewells_en):
            return {
                "response": "Goodbye! 🌾\n\nFeel free to ask if you need more help.\n\nHappy farming! 😊",
                "session_id": session_id, "sensor_data_used": None,
                "recommendations": {"type": "farewell", "language": "english", "nitrogen_status": "N/A", "phosphorus_status": "N/A", "potassium_status": "N/A", "ph_status": "N/A", "land_size": land_size, "context_flags": []}
            }
        if any(casual in user_lower for casual in casual_en):
            return {
                "response": "I'm doing great, thank you! 😊\n\nTell me about your farm or crops.\nI'm here to help! 🌾",
                "session_id": session_id, "sensor_data_used": None,
                "recommendations": {"type": "casual", "language": "english", "nitrogen_status": "N/A", "phosphorus_status": "N/A", "potassium_status": "N/A", "ph_status": "N/A", "land_size": land_size, "context_flags": []}
            }
    
    n = sensor_data.get('nitrogen', 0)
    p = sensor_data.get('phosphorus', 0)
    k = sensor_data.get('potassium', 0)
    ph = sensor_data.get('ph', 7.0)
    temp = sensor_data.get('temperature', 0)
    humidity = sensor_data.get('humidity', 0)
    ec = sensor_data.get('ec', 0)
    
    n_status = "Low" if n < 200 else "High" if n > 400 else "Good"
    p_status = "Low" if p < 15 else "High" if p > 30 else "Good"
    k_status = "Low" if k < 150 else "High" if k > 280 else "Good"
    ph_status = "Acidic" if ph < 6.0 else "Alkaline" if ph > 7.5 else "Good"
    
    context_flags = []
    if n == 0 and p == 0 and k == 0 and ph == 0 and ec == 0:
        context_flags.append("SENSOR_ERROR")
    if humidity < 35:
        context_flags.append("LOW_HUMIDITY")
    if humidity > 80:
        context_flags.append("HIGH_HUMIDITY")
    if ph < 5.5:
        context_flags.append("CRITICAL_LOW_pH")
    if ph > 8.0:
        context_flags.append("CRITICAL_HIGH_pH")

    is_crop_question = is_crop_recommendation_question(user_message, detected_language)

    if is_crop_question:
        # ── Pre-score using the shared engine (same as /api/v1/recommend-crops) ──
        sensor_dict = dict(n=n, p=p, k=k, ph=ph,
                           humidity=humidity, temperature=temp, ec=ec)
        #scored_top3 = score_crops_locally(sensor_dict)   # [{rank,name,reason}, ...]
        user_season = _detect_season_from_message(user_message)
        scored_top3 = score_crops_locally(sensor_dict, season=user_season)
        ranked_names = [c["name"] for c in scored_top3]   # locked-in order

        crop_instruction = f"""DETECTED LANGUAGE: {detected_language.upper()}
        f"   Season filter applied: {user_season.upper()}\n"

⚠️ CRITICAL: You MUST reply in {detected_language.upper()} language only!
- If English → Use PURE ENGLISH
- If Urdu → Use PURE URDU (اردو script), NOT Roman Urdu

FARMER'S QUESTION: "{user_message}"
QUESTION TYPE: CROP RECOMMENDATION

CURRENT SOIL DATA:
• Nitrogen (N): {n} mg/kg - Status: {n_status}
• Phosphorus (P): {p} mg/kg - Status: {p_status}
• Potassium (K): {k} mg/kg - Status: {k_status}
• pH Level: {ph} - Status: {ph_status}
• Temperature: {temp}°C
• Humidity: {humidity}%
• EC: {ec} µS/cm

FARM SIZE: {land_size} acres

CONTEXT ALERTS:
{chr(10).join('• ' + flag for flag in context_flags) if context_flags else '• No critical issues'}

⚠️ RANKING ALREADY DECIDED BY AGRONOMIC SCORING ENGINE — DO NOT CHANGE IT:
   🥇 1st: {ranked_names[0]}
   🥈 2nd: {ranked_names[1]}
   🥉 3rd: {ranked_names[2]}

STRICT INSTRUCTIONS:
1. Reply in {detected_language.upper()} ONLY — pure English or pure Urdu script, never mixed.
2. Use EXACTLY the formatted template from your system instructions for crop recommendations.
   - Include the ━━━ divider lines between sections
   - Keep the emoji labels (📌 Why suitable, 🌱 Best seed, 📦 Fertilizer, 💧 Watering, 📈 Expected yield)
   - Leave a blank line between each crop block
3. The 3 crops above are FIXED — write reasons, seed varieties, fertilizer & watering for THESE exact crops.
4. Base ALL reasons on the actual sensor values — do NOT use generic defaults.
5. Give exact kg amounts calculated for {land_size} acres.
6. Include 2 crops to AVOID with reason based on the soil data.
7. Include 2-3 soil improvement tips specific to this soil's weak points.

Answer now in {detected_language.upper()} using the exact template structure:"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=crop_instruction)
        ]

        try:
            response = llm.invoke(messages)
            ai_response = None

            if hasattr(response, 'content') and response.content:
                ai_response = response.content
            else:
                # best1 = "Wheat" if 6.0 <= ph <= 7.5 else "Maize"
                # best2 = "Potato" if k >= 150 else "Onion"
                # best3 = "Mustard (Sarson)" if temp <= 25 else "Sunflower"
                best1 = scored_top3[0]["name"]
                best2 = scored_top3[1]["name"]
                best3 = scored_top3[2]["name"]
                water_tip = "every 4 days" if humidity < 35 else "every 6–7 days" if humidity < 60 else "every 9–10 days"

                BASE_UREA = {"Wheat": 40, "Maize": 50, "Potato": 30, "Onion": 25, "Mustard (Sarson)": 30, "Sunflower": 35}
                BASE_DAP  = {"Wheat": 25, "Maize": 30, "Potato": 35, "Onion": 20, "Mustard (Sarson)": 20, "Sunflower": 25}
                BASE_MOP  = {"Wheat": 15, "Maize": 20, "Potato": 30, "Onion": 15, "Mustard (Sarson)": 10, "Sunflower": 15}

                def fert(crop, nutrient_val, base_dict, low_thresh, high_thresh, base_key):
                    base = base_dict.get(base_key, 25)
                    if nutrient_val > high_thresh:
                        return round(base * 0.6 * land_size, 1)
                    elif nutrient_val < low_thresh:
                        return round(base * 1.3 * land_size, 1)
                    else:
                        return round(base * land_size, 1)

                c1_urea = fert(best1, n, BASE_UREA, 200, 400, best1)
                c1_dap  = fert(best1, p, BASE_DAP,  15,  30,  best1)
                c1_mop  = fert(best1, k, BASE_MOP,  150, 280, best1)
                c2_urea = fert(best2, n, BASE_UREA, 200, 400, best2)
                c2_dap  = fert(best2, p, BASE_DAP,  15,  30,  best2)
                c2_mop  = fert(best2, k, BASE_MOP,  150, 280, best2)
                c3_urea = fert(best3, n, BASE_UREA, 200, 400, best3)
                c3_dap  = fert(best3, p, BASE_DAP,  15,  30,  best3)
                c3_mop  = fert(best3, k, BASE_MOP,  150, 280, best3)

                if detected_language == "urdu":
                    ai_response = (
                        f"🌱 آپ کی مٹی کے لیے فصل کی سفارشات\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"📊 مٹی کا خلاصہ\n"
                        f"• نائٹروجن   : {n} mg/kg  → {'کم' if n<200 else 'زیادہ' if n>400 else 'ٹھیک'}\n"
                        f"• فاسفورس    : {p} mg/kg  → {'کم' if p<15 else 'زیادہ' if p>30 else 'ٹھیک'}\n"
                        f"• پوٹاشیم    : {k} mg/kg  → {'کم' if k<150 else 'زیادہ' if k>280 else 'ٹھیک'}\n"
                        f"• پی ایچ     : {ph}        → {'تیزابی' if ph<6 else 'الکلی' if ph>7.5 else 'ٹھیک'}\n"
                        f"• درجہ حرارت: {temp}°C  |  نمی: {humidity}%\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"✅ آپ کی زمین کے لیے بہترین فصلیں\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"🥇 پہلی پسند: {best1}\n"
                        f"   📦 کھاد   : یوریا {c1_urea} کلوگرام + DAP {c1_dap} کلوگرام + MOP {c1_mop} کلوگرام ({land_size} ایکڑ)\n"
                        f"   💧 پانی   : {water_tip.replace('every','ہر').replace('days','دن بعد')}\n\n"
                        f"🥈 دوسری پسند: {best2}\n"
                        f"   📦 کھاد   : یوریا {c2_urea} کلوگرام + DAP {c2_dap} کلوگرام + MOP {c2_mop} کلوگرام ({land_size} ایکڑ)\n"
                        f"   💧 پانی   : ہر 5 دن بعد\n\n"
                        f"🥉 تیسری پسند: {best3}\n"
                        f"   📦 کھاد   : یوریا {c3_urea} کلوگرام + DAP {c3_dap} کلوگرام + MOP {c3_mop} کلوگرام ({land_size} ایکڑ)\n"
                        f"   💧 پانی   : ہر 7 دن بعد\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"💡 مٹی بہتر بنانے کے مشورے\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• {'نائٹروجن کم ہے — یوریا ڈالیں' if n<200 else 'نائٹروجن زیادہ ہے — یوریا نہ ڈالیں'}\n"
                        f"• {'نمی بہت کم ہے — باقاعدہ آبپاشی ضروری ہے' if humidity<35 else 'نمی ٹھیک ہے'}\n"
                        f"• نامیاتی کھاد (گوبر/کمپوسٹ) ڈالنے سے مٹی کی ساخت بہتر ہوگی۔"
                    )
                else:
                    ai_response = (
                        f"🌱 CROP RECOMMENDATIONS FOR YOUR SOIL\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"📊 SOIL SUMMARY\n"
                        f"• Nitrogen  : {n} mg/kg  → {'Low' if n<200 else 'High' if n>400 else 'Good'}\n"
                        f"• Phosphorus: {p} mg/kg  → {'Low' if p<15 else 'High' if p>30 else 'Good'}\n"
                        f"• Potassium : {k} mg/kg  → {'Low' if k<150 else 'High' if k>280 else 'Good'}\n"
                        f"• pH Level  : {ph}        → {'Acidic' if ph<6 else 'Alkaline' if ph>7.5 else 'Good'}\n"
                        f"• Temperature: {temp}°C  |  Humidity: {humidity}%\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"✅ BEST CROPS FOR YOUR LAND\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"🥇 1ST CHOICE: {best1.upper()}\n"
                        f"   📦 Fertilizer   : Urea {c1_urea} kg + DAP {c1_dap} kg + MOP {c1_mop} kg (for {land_size} acres)\n"
                        f"   💧 Watering     : {water_tip}\n\n"
                        f"🥈 2ND CHOICE: {best2.upper()}\n"
                        f"   📦 Fertilizer   : Urea {c2_urea} kg + DAP {c2_dap} kg + MOP {c2_mop} kg (for {land_size} acres)\n"
                        f"   💧 Watering     : every 5 days\n\n"
                        f"🥉 3RD CHOICE: {best3.upper()}\n"
                        f"   📦 Fertilizer   : Urea {c3_urea} kg + DAP {c3_dap} kg + MOP {c3_mop} kg (for {land_size} acres)\n"
                        f"   💧 Watering     : every 7 days\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"💡 SOIL IMPROVEMENT TIPS\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• {'Nitrogen is low — apply Urea before sowing' if n<200 else 'Nitrogen is high — skip extra Urea'}\n"
                        f"• {'Humidity is very low — irrigate regularly' if humidity<35 else 'Humidity is adequate'}\n"
                        f"• Add organic compost to improve soil texture and nutrient retention."
                    )

        except Exception as e:
            print(f"LLM Error (crop): {str(e)}")
            import traceback
            traceback.print_exc()
            if detected_language == "urdu":
                ai_response = "⚠️ ابھی AI سروس میں مسئلہ ہے۔\nکچھ دیر میں دوبارہ کوشش کریں! 🙏"
            else:
                ai_response = "⚠️ AI service is temporarily unavailable.\nPlease try again in a moment! 🙏"

        return {
            "response": ai_response,
            "session_id": session_id,
            "sensor_data_used": sensor_data,
            "recommendations": {
                "type": "crop_recommendation",
                "language": detected_language,
                "nitrogen_status": n_status,
                "phosphorus_status": p_status,
                "potassium_status": k_status,
                "ph_status": ph_status,
                "land_size": land_size,
                "context_flags": context_flags
            }
        }

    detailed_message = f"""DETECTED LANGUAGE: {detected_language.upper()}

⚠️ CRITICAL: You MUST reply in {detected_language.upper()} language only!
- If English → Use PURE ENGLISH
- If Urdu → Use PURE URDU (اردو script), NOT Roman Urdu

FARMER'S QUESTION: "{user_message}"

CURRENT SOIL DATA:
• Nitrogen (N): {n} mg/kg - Status: {n_status}
• Phosphorus (P): {p} mg/kg - Status: {p_status}
• Potassium (K): {k} mg/kg - Status: {k_status}
• pH Level: {ph} - Status: {ph_status}
• Temperature: {temp}°C
• Humidity: {humidity}%
• EC: {ec} µS/cm

FARM SIZE: {land_size} acres

CONTEXT ALERTS:
{chr(10).join('• ' + flag for flag in context_flags) if context_flags else '• No critical issues'}

INSTRUCTIONS:
1. Respond in {detected_language.upper()} language ONLY
2. Check if question is about farming/agriculture
3. If NOT farming → politely decline and redirect
4. Response length: 8-15 lines for detailed questions, 3-5 for simple ones
5. Explain WHY along with WHAT
6. Give specific kg amounts for {land_size} acres
7. Include emojis for clarity
8. Be helpful and professional

Answer now in {detected_language.upper()}:"""
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=detailed_message)
    ]
    
    try:
        response = llm.invoke(messages)
        ai_response = None
        
        if hasattr(response, 'content') and response.content:
            ai_response = response.content
        else:
            print(f"⚠️ Empty response")
            urea_kg = round(max(0, (280 - n) / 100 * 20 * land_size), 1)
            dap_kg  = round(max(0, (25  - p) / 10  * 15 * land_size), 1)
            mop_kg  = round(max(0, (200 - k) / 50  * 10 * land_size), 1)
            water_freq    = "Daily (humidity critical)" if humidity < 35 else "Every 2-3 days" if humidity < 55 else "Every 5-6 days"
            water_freq_ur = "روزانہ (نمی بہت کم)" if humidity < 35 else "ہر 2-3 دن بعد" if humidity < 55 else "ہر 5-6 دن بعد"

            if detected_language == "urdu":
                ai_response = (
                    f"📊 مٹی کی حالت\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"• نائٹروجن  : {n} mg/kg  → {'کم — فصل کمزور ہوگی' if n<200 else 'زیادہ — یوریا نہ ڈالیں' if n>400 else 'ٹھیک ✅'}\n"
                    f"• فاسفورس   : {p} mg/kg  → {'کم — جڑوں کی نشوونما متاثر' if p<15 else 'زیادہ — DAP نہ ڈالیں' if p>30 else 'ٹھیک ✅'}\n"
                    f"• پوٹاشیم   : {k} mg/kg  → {'کم — پھل/دانہ کمزور' if k<150 else 'زیادہ — MOP نہ ڈالیں' if k>280 else 'ٹھیک ✅'}\n"
                    f"• پی ایچ    : {ph}        → {'تیزابی — چونا ڈالیں' if ph<6 else 'الکلی — گندھک ڈالیں' if ph>7.5 else 'ٹھیک ✅'}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📦 کھاد کی ضرورت ({land_size} ایکڑ کے لیے)\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    + (f"• یوریا — {urea_kg} کلوگرام\n  وجہ: نائٹروجن کم ہے\n" if n < 200 else "• یوریا: ضرورت نہیں ✅\n")
                    + (f"• DAP — {dap_kg} کلوگرام\n  وجہ: فاسفورس کم ہے\n" if p < 15 else "• DAP: ضرورت نہیں ✅\n")
                    + (f"• MOP — {mop_kg} کلوگرام\n  وجہ: پوٹاشیم کم ہے\n" if k < 150 else "• MOP: ضرورت نہیں ✅\n")
                    + f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💧 پانی کا شیڈول\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"• موجودہ نمی: {humidity}%  → {water_freq_ur}\n"
                    f"• بہترین وقت: صبح 7–9 بجے یا شام 5–7 بجے\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏰ فوری اقدام\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    + ("• فوری یوریا ڈالیں 🚨\n" if n < 150
                       else "• پی ایچ درست کریں 🚨\n" if ph < 5.5
                       else "• پانی کا شیڈول باقاعدہ رکھیں 🚨\n" if humidity < 30
                       else "• مٹی کی حالت اچھی ہے ✅\n")
                )
            else:
                ai_response = (
                    f"📊 SOIL STATUS\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"• Nitrogen  : {n} mg/kg  → {'Low — crops will be weak' if n<200 else 'High — skip Urea' if n>400 else 'Good ✅'}\n"
                    f"• Phosphorus: {p} mg/kg  → {'Low — root growth affected' if p<15 else 'High — skip DAP' if p>30 else 'Good ✅'}\n"
                    f"• Potassium : {k} mg/kg  → {'Low — poor fruit/grain quality' if k<150 else 'High — skip MOP' if k>280 else 'Good ✅'}\n"
                    f"• pH Level  : {ph}        → {'Acidic — apply lime' if ph<6 else 'Alkaline — apply sulfur' if ph>7.5 else 'Good ✅'}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📦 FERTILIZER NEEDED (for {land_size} acres)\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    + (f"• Urea — {urea_kg} kg\n  Reason: Nitrogen is low\n" if n < 200 else "• Urea: Not needed ✅\n")
                    + (f"• DAP  — {dap_kg} kg\n  Reason: Phosphorus is low\n" if p < 15 else "• DAP: Not needed ✅\n")
                    + (f"• MOP  — {mop_kg} kg\n  Reason: Potassium is low\n" if k < 150 else "• MOP: Not needed ✅\n")
                    + f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💧 WATERING SCHEDULE\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"• Current humidity: {humidity}%  → {water_freq}\n"
                    f"• Best time: Morning 7–9 AM or Evening 5–7 PM\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏰ IMMEDIATE ACTION\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    + ("• Apply Urea immediately 🚨\n" if n < 150
                       else "• Fix pH first — apply lime 🚨\n" if ph < 5.5
                       else "• Irrigate now — humidity critically low 🚨\n" if humidity < 30
                       else "• Soil is in good condition ✅\n")
                )
        
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        import traceback
        traceback.print_exc()
        if detected_language == "urdu":
            ai_response = "⚠️ ابھی AI سروس میں مسئلہ ہے۔\nکچھ دیر میں دوبارہ کوشش کریں! 🙏"
        else:
            ai_response = "⚠️ AI service is temporarily unavailable.\nPlease try again in a moment! 🙏"
    
    return {
        "response": ai_response,
        "session_id": session_id,
        "sensor_data_used": sensor_data,
        "recommendations": {
            "language": detected_language,
            "nitrogen_status": n_status,
            "phosphorus_status": p_status,
            "potassium_status": k_status,
            "ph_status": ph_status,
            "land_size": land_size,
            "context_flags": context_flags
        }
    }


# ============== INTERACTIVE TERMINAL MODE ==============
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🤖 DR. AGRIBOT - BILINGUAL VERSION (English/Urdu)")
    print("="*80 + "\n")
    
    print("Test Mode: Type questions in English or Urdu (type 'exit' to quit)\n")
    print("Examples:")
    print("  English: What fertilizer should I use?")
    print("  English: Which crop should I plant on my land?")
    print("  Urdu: کس کھاد کی ضرورت ہے؟")
    print("  Urdu: کون سی فصل لگانی چاہیے؟\n")
    
    default_sensor = {
        "nitrogen": 180,
        "phosphorus": 20,
        "potassium": 140,
        "ph": 6.5,
        "temperature": 25,
        "humidity": 45,
        "ec": 1000
    }
    
    while True:
        try:
            question = input("\n❓ Your Question: ").strip()
            if question.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye! / اللہ حافظ!\n")
                break
            if not question:
                continue
            lang = detect_language(question)
            is_crop_q = is_crop_recommendation_question(question, lang)
            print(f"\n🔍 Detected: {lang.upper()} | Crop Question: {is_crop_q}")
            print("⏳ Dr. AgriBot thinking...\n")
            result = get_agricultural_advice(
                user_message=question,
                sensor_data=default_sensor,
                land_size=2.5
            )
            print("✅ RESPONSE:")
            print("-"*80)
            print(result['response'])
            print("-"*80)
        except KeyboardInterrupt:
            print("\n\n⚠️ Cancelled\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
    
    print("="*80 + "\n")
