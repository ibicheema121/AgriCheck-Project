# # import os
# # from dotenv import load_dotenv
# # from openai import AzureOpenAI
# # from typing import Optional
# # import json

# # load_dotenv()

# # # Initialize Azure OpenAI client (NOT regular OpenAI)
# # client = AzureOpenAI(
# #     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
# #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
# #     api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
# # )

# # MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL_NAME", "o4-mini")

# # print(f"🤖 Voice LLM: Azure OpenAI ({MODEL_NAME})")

# # # Store conversation history per session (separate from chat endpoint)
# # voice_conversation_sessions = {}

# # VOICE_SYSTEM_PROMPT_EN = """You are Dr. AgriBot, an expert agricultural advisor for Pakistani farmers.
# # You are speaking through a VOICE interface, so keep responses clear and concise for speech.

# # RULES:
# # 1. ONLY answer farming/agriculture questions. Reject everything else politely.
# # 2. You MUST use the sensor data provided to give specific, actionable advice.
# # 3. Answer the user's SPECIFIC question using sensor data.
# # 4. If user asks about watering, focus on watering advice.
# # 5. If user asks about fertilizer, focus on fertilizer advice.
# # 6. If user just greets, introduce yourself briefly and ask how to help.
# # 7. Keep responses SHORT (under 200 words) since this is voice output.
# # 8. Do NOT use emojis or special symbols in the response since it will be read aloud by TTS.

# # ALWAYS respond in this format:

# # SOIL STATUS:
# # - Nitrogen: {value} mg/kg - {Good/Low/High} ({brief reason})
# # - Phosphorus: {value} mg/kg - {Good/Low/High} ({brief reason})
# # - Potassium: {value} mg/kg - {Good/Low/High} ({brief reason})
# # - pH Level: {value} - {Acidic/Neutral/Alkaline} ({brief impact})

# # FERTILIZER NEEDED:
# # - {Fertilizer name}: {amount} for {land_size} acre
# #   Reason: {why this fertilizer based on sensor readings}

# # WATERING SCHEDULE:
# # - Humidity {value}% - {recommendation}
# # - Best time: {specific time recommendation}

# # IMPORTANT:
# # - {One critical action item based on the data}
# # """

# # VOICE_SYSTEM_PROMPT_UR = """Aap Dr. AgriBot hain, Pakistani kisaanon ke liye ek expert ziraati musheer.
# # Aap VOICE interface se baat kar rahe hain, toh jawaab saaf aur mukhtasar rakhein.

# # QAWAID:
# # 1. SIRF kheti/ziraat ke sawaalon ka jawaab dein. Baqi sab ko politely reject karein.
# # 2. Sensor data ka istemal karke specific, amal-qaabil mashwara dena LAZMI hai.
# # 3. User ke KHAS sawaal ka jawaab sensor data se dein.
# # 4. Agar user paani ke baare mein poochhe, toh paani par focus karein.
# # 5. Agar user khad ke baare mein poochhe, toh khad par focus karein.
# # 6. Agar user sirf salam kare, toh apna mukhtasar taaruf dein.
# # 7. Jawaab CHHOTA rakhein (200 alfaaz se kam) kyunke yeh voice output hai.
# # 8. Jawaab mein emojis ya special symbols NAHI use karna kyunke yeh TTS se bola jayega.

# # HAMESHA is format mein jawaab dein:

# # ZAMIN KI HALAT:
# # - Nitrogen: {value} mg/kg - {Acha/Kam/Zyada} ({mukhtasar wajah})
# # - Phosphorus: {value} mg/kg - {Acha/Kam/Zyada} ({mukhtasar wajah})
# # - Potassium: {value} mg/kg - {Acha/Kam/Zyada} ({mukhtasar wajah})
# # - pH Level: {value} - {Tezabi/Neutral/Khari} ({asar})

# # KHAD KI ZAROORAT:
# # - {Khad ka naam}: {miqdar} baraye {land_size} acre
# #   Wajah: {sensor readings ki buniyad par yeh khad kyun}

# # PANI KA SCHEDULE:
# # - Humidity {value}% - {mashwara}
# # - Behtareen waqt: {specific waqt ka mashwara}

# # ZAROORI:
# # - {Data ki buniyad par ek ahem qadam}
# # """


# # # Common Roman Urdu words for language detection
# # ROMAN_URDU_WORDS = {
# #     'mujhe', 'mujhay', 'mein', 'main', 'hai', 'hain', 'kya', 'kyun',
# #     'kaise', 'kab', 'kahan', 'kon', 'kaun', 'aur', 'ya', 'se', 'ka', 'ke', 'ki',
# #     'ko', 'par', 'pe', 'ne', 'ho', 'hona', 'karna', 'dena', 'lena',
# #     'batao', 'bata', 'bataye', 'bataen', 'btao', 'btaye', 'bataiye',
# #     'fasal', 'kheti', 'khet', 'zameen', 'zamin', 'mitti',
# #     'pani', 'paani', 'khad', 'beej', 'bij',
# #     'gandum', 'chawal', 'makki', 'kapas', 'ganna', 'sarson',
# #     'haan', 'nahi', 'nhi', 'ji', 'shukriya', 'meherbani',
# #     'kitna', 'kitni', 'kitne', 'kaunsa', 'kaunsi', 'konsa', 'konsi',
# #     'chahiye', 'chahie', 'zaroorat', 'zarurat',
# #     'abhi', 'pehle', 'baad', 'kal', 'aaj',
# #     'apni', 'apna', 'apne', 'mera', 'meri', 'mere',
# #     'zyada', 'kam', 'acha', 'achi', 'bura', 'theek', 'thik',
# #     'waqt', 'din', 'raat', 'subah', 'shaam', 'dopahar',
# #     'lagana', 'lagao', 'dalna', 'dalo', 'daalna',
# #     'ye', 'yeh', 'woh', 'wo', 'is', 'us', 'iska', 'uska',
# #     'kaisa', 'kaisi', 'kaise', 'achha', 'achhi',
# #     'hum', 'tum', 'aap', 'yahan', 'wahan',
# #     'sab', 'kuch', 'bohat', 'bahut', 'thoda', 'thodi',
# # }


# # def detect_voice_language(text: str) -> str:
# #     """
# #     Detect if voice text is Urdu (Unicode Urdu or Roman Urdu) or English.
# #     Returns 'ur-PK' or 'en-US'
# #     """

# #     # Check Unicode Urdu characters first
# #     urdu_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
# #     if urdu_chars > 3:
# #         print(f"🌐 Language: ur-PK (Unicode Urdu detected: {urdu_chars} chars)")
# #         return "ur-PK"

# #     # Check Roman Urdu words
# #     words = text.lower().split()
# #     if len(words) == 0:
# #         return "en-US"

# #     urdu_word_count = sum(1 for w in words if w.strip('.,?!:;') in ROMAN_URDU_WORDS)
# #     ratio = urdu_word_count / len(words)

# #     print(f"🌐 Language detection: {urdu_word_count}/{len(words)} Urdu words ({ratio:.0%})")

# #     if ratio >= 0.25:
# #         print(f"🌐 Language: ur-PK (Roman Urdu)")
# #         return "ur-PK"

# #     print(f"🌐 Language: en-US")
# #     return "en-US"


# # def get_voice_agricultural_advice(
# #     user_message: str,
# #     sensor_data: dict,
# #     land_size: float = 1.0,
# #     session_id: str = "default"
# # ) -> dict:
# #     """
# #     Get agricultural advice for VOICE interface using Azure OpenAI.
# #     Separate from the chat endpoint's llm_agent.
# #     Detects language and responds in Urdu or English.
# #     """

# #     is_urdu = False

# #     try:
# #         # Detect language
# #         language = detect_voice_language(user_message)
# #         is_urdu = (language == "ur-PK")

# #         # Choose system prompt based on language
# #         system_prompt = VOICE_SYSTEM_PROMPT_UR if is_urdu else VOICE_SYSTEM_PROMPT_EN

# #         # Build sensor context
# #         sensor_context = f"""
# # CURRENT SENSOR DATA (from IoT device):
# # - Nitrogen (N): {sensor_data.get('nitrogen', 'N/A')} mg/kg
# # - Phosphorus (P): {sensor_data.get('phosphorus', 'N/A')} mg/kg
# # - Potassium (K): {sensor_data.get('potassium', 'N/A')} mg/kg
# # - pH Level: {sensor_data.get('ph', 'N/A')}
# # - Temperature: {sensor_data.get('temperature', 'N/A')}°C
# # - Humidity: {sensor_data.get('humidity', 'N/A')}%
# # - EC (Electrical Conductivity): {sensor_data.get('ec', 'N/A')} µS/cm
# # - Land Size: {land_size} acre(s)
# # """

# #         # Get or create voice session conversation history
# #         if session_id not in voice_conversation_sessions:
# #             voice_conversation_sessions[session_id] = []

# #         history = voice_conversation_sessions[session_id]

# #         # Build messages — o4-mini uses "developer" role instead of "system"
# #         messages = [
# #             {"role": "developer", "content": system_prompt + "\n\n" + sensor_context}
# #         ]

# #         # Add conversation history (last 6 messages max)
# #         messages.extend(history[-6:])

# #         # Add current user message with language hint
# #         if is_urdu:
# #             messages.append({
# #                 "role": "user",
# #                 "content": f"[Yeh sawaal Roman Urdu mein hai] {user_message}\n\n(Roman Urdu mein jawaab dein. Sensor data zaroor istemal karein.)"
# #             })
# #         else:
# #             messages.append({
# #                 "role": "user",
# #                 "content": user_message
# #             })

        
# #         print(f"📤 Sending to Azure OpenAI ({MODEL_NAME}): {len(messages)} messages")

# #         # Call Azure OpenAI
# #         # o4-mini is a reasoning model: max_completion_tokens covers BOTH
# #         # reasoning tokens (internal thinking) + output tokens (actual response)
# #         # 800 was too low — model used all tokens for reasoning, 0 left for output
# #         response = client.chat.completions.create(
# #             model=MODEL_NAME,
# #             messages=messages,
# #             max_completion_tokens=4000
# #         )

# #         # Extract response — try output_text first (reasoning models), then content
# #         ai_response = ""

# #         choice = response.choices[0]

# #         # Try standard content first
# #         if choice.message and choice.message.content:
# #             ai_response = choice.message.content.strip()

# #         # If empty, check if there's output in a different format
# #         if not ai_response:
# #             # Some reasoning models put output differently
# #             raw_message = choice.message
# #             print(f"⚠️ Empty content. Message object: {raw_message}")
# #             print(f"⚠️ Full response: {response}")

# #             # Try to get any text from the response
# #             if hasattr(raw_message, 'refusal') and raw_message.refusal:
# #                 ai_response = f"Model refused: {raw_message.refusal}"
# #             elif hasattr(response, 'usage'):
# #                 print(f"📊 Token usage: {response.usage}")

# #         if not ai_response:
# #             print("❌ AI returned empty response!")
# #             if is_urdu:
# #                 ai_response = "Maaf kijiye, AI se koi jawaab nahi mila. Dobara poochein."
# #             else:
# #                 ai_response = "Sorry, the AI did not return a response. Please try again."

# #         print(f"🤖 AI Response length: {len(ai_response)} chars")
# #         print(f"🤖 AI Response preview: {ai_response[:200]}")

# #         # Save to voice conversation history
# #         history.append({"role": "user", "content": user_message})
# #         history.append({"role": "assistant", "content": ai_response})

# #         # Keep only last 10 messages
# #         if len(history) > 10:
# #             voice_conversation_sessions[session_id] = history[-10:]

# #         return {
# #             "response": ai_response,
# #             "language": language,
# #             "sensor_data_used": sensor_data
# #         }

# #     except Exception as e:
# #         print(f"❌ Voice LLM Error: {str(e)}")
# #         import traceback
# #         traceback.print_exc()
# #         if is_urdu:
# #             return {
# #                 "response": "Maaf kijiye, jawaab mein masla aaya. Dobara koshish karein.",
# #                 "language": "ur-PK",
# #                 "sensor_data_used": sensor_data
# #             }
# #         return {
# #             "response": "Sorry, there was an error getting advice. Please try again.",
# #             "language": "en-US",
# #             "sensor_data_used": sensor_data
# #         }


# # def clear_voice_session(session_id: str):
# #     """Clear voice conversation history for a session"""
# #     if session_id in voice_conversation_sessions:
# #         del voice_conversation_sessions[session_id]
# #         print(f"🗑️ Voice session cleared: {session_id}")















# import os
# from dotenv import load_dotenv
# from openai import AzureOpenAI
# from typing import Optional
# import json

# load_dotenv()

# # Initialize Azure OpenAI client (NOT regular OpenAI)
# client = AzureOpenAI(
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
# )

# MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL_NAME", "o4-mini")

# print(f"🤖 Voice LLM: Azure OpenAI ({MODEL_NAME})")

# # Store conversation history per session (separate from chat endpoint)
# voice_conversation_sessions = {}

# VOICE_SYSTEM_PROMPT_EN = """You are Dr. AgriBot, an expert agricultural advisor for Pakistani farmers.
# You are speaking through a VOICE interface, so keep responses clear and concise for speech.

# RULES:
# 1. ONLY answer farming/agriculture questions. Reject everything else politely.
# 2. You MUST use the sensor data provided to give specific, actionable advice.
# 3. Answer the user's SPECIFIC question using sensor data.
# 4. If user asks about watering, focus on watering advice.
# 5. If user asks about fertilizer, focus on fertilizer advice.
# 6. If user just greets, introduce yourself briefly and ask how to help.
# 7. Keep responses SHORT (under 200 words) since this is voice output.
# 8. Do NOT use emojis or special symbols in the response since it will be read aloud by TTS.
# 9. Do NOT use brackets, dashes, colons, bullet points or any special formatting.
# 10. Write in plain conversational sentences that sound natural when spoken aloud.

# Example good response:
# Your soil nitrogen is 300 milligrams per kilogram which is good for healthy leaf growth.
# Phosphorus is 327 milligrams per kilogram which is high so you don't need extra phosphorus fertilizer.
# Potassium is 340 milligrams per kilogram which is also high.
# Your soil pH is 7.9 which is alkaline and may reduce micronutrient availability.
# For fertilizer, you don't need additional NPK right now since all levels are adequate.
# For watering, with humidity at 28 percent, water every 2 days. Best time is early morning 6 to 9 AM.
# """

# VOICE_SYSTEM_PROMPT_UR = """آپ ڈاکٹر ایگری بوٹ ہیں، پاکستانی کسانوں کے لیے ایک ماہر زرعی مشیر۔
# آپ وائس انٹرفیس سے بات کر رہے ہیں، تو جواب صاف اور مختصر رکھیں۔

# قواعد:
# 1. صرف کھیتی اور زراعت کے سوالوں کا جواب دیں۔ باقی سب کو شائستگی سے مسترد کریں۔
# 2. سینسر ڈیٹا کا استعمال کر کے مخصوص اور عملی مشورہ دینا لازمی ہے۔
# 3. صارف کے خاص سوال کا جواب سینسر ڈیٹا سے دیں۔
# 4. اگر صارف پانی کے بارے میں پوچھے تو پانی پر فوکس کریں۔
# 5. اگر صارف کھاد کے بارے میں پوچھے تو کھاد پر فوکس کریں۔
# 6. اگر صارف صرف سلام کرے تو اپنا مختصر تعارف دیں۔
# 7. جواب مختصر رکھیں کیونکہ یہ وائس آؤٹ پٹ ہے۔
# 8. جواب میں ایموجی یا خاص نشانیاں بالکل استعمال نہ کریں۔
# 9. جواب ہمیشہ اردو رسم الخط میں لکھیں۔ رومن اردو ہرگز استعمال نہ کریں۔
# 10. انگریزی الفاظ کو اردو میں لکھیں۔ مثلاً نائٹروجن، فاسفورس، پوٹاشیم، پی ایچ۔
# 11. اعداد بھی اردو میں لکھیں مثلاً تین سو ملی گرام فی کلوگرام۔
# 12. بریکٹ، ڈیش، کولن، بلٹ پوائنٹ جیسی کوئی علامت استعمال نہ کریں۔
# 13. سادہ بول چال کے جملے لکھیں جو بولنے میں فطری لگیں۔

# مثال اچھا جواب:
# آپ کی زمین میں نائٹروجن تین سو ملی گرام فی کلوگرام ہے جو اچھی مقدار ہے اور پتوں کی صحت مند نشوونما کے لیے کافی ہے۔ فاسفورس تین سو ستائیس ملی گرام فی کلوگرام ہے جو زیادہ ہے اس لیے اضافی فاسفورس کھاد کی ضرورت نہیں۔ پوٹاشیم تین سو چالیس ملی گرام فی کلوگرام ہے جو بھی کافی ہے۔ پی ایچ لیول سات اعشاریہ نو ہے جو قلعی ہے۔ کھاد کے لیے ابھی اضافی این پی کے کی ضرورت نہیں۔ پانی کے لیے نمی اٹھائیس فیصد ہے تو ہر دو دن بعد پانی دیں۔ بہترین وقت صبح چھ سے نو بجے ہے۔
# """


# # Common Roman Urdu words for language detection
# ROMAN_URDU_WORDS = {
#     'mujhe', 'mujhay', 'mein', 'main', 'hai', 'hain', 'kya', 'kyun',
#     'kaise', 'kab', 'kahan', 'kon', 'kaun', 'aur', 'ya', 'se', 'ka', 'ke', 'ki',
#     'ko', 'par', 'pe', 'ne', 'ho', 'hona', 'karna', 'dena', 'lena',
#     'batao', 'bata', 'bataye', 'bataen', 'btao', 'btaye', 'bataiye',
#     'fasal', 'kheti', 'khet', 'zameen', 'zamin', 'mitti',
#     'pani', 'paani', 'khad', 'beej', 'bij',
#     'gandum', 'chawal', 'makki', 'kapas', 'ganna', 'sarson',
#     'haan', 'nahi', 'nhi', 'ji', 'shukriya', 'meherbani',
#     'kitna', 'kitni', 'kitne', 'kaunsa', 'kaunsi', 'konsa', 'konsi',
#     'chahiye', 'chahie', 'zaroorat', 'zarurat',
#     'abhi', 'pehle', 'baad', 'kal', 'aaj',
#     'apni', 'apna', 'apne', 'mera', 'meri', 'mere',
#     'zyada', 'kam', 'acha', 'achi', 'bura', 'theek', 'thik',
#     'waqt', 'din', 'raat', 'subah', 'shaam', 'dopahar',
#     'lagana', 'lagao', 'dalna', 'dalo', 'daalna',
#     'ye', 'yeh', 'woh', 'wo', 'is', 'us', 'iska', 'uska',
#     'kaisa', 'kaisi', 'kaise', 'achha', 'achhi',
#     'hum', 'tum', 'aap', 'yahan', 'wahan',
#     'sab', 'kuch', 'bohat', 'bahut', 'thoda', 'thodi',
# }


# def detect_voice_language(text: str) -> str:
#     """
#     Detect if voice text is Urdu (Unicode Urdu or Roman Urdu) or English.
#     Returns 'ur-PK' or 'en-US'
#     """

#     # Check Unicode Urdu characters first
#     urdu_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
#     if urdu_chars > 3:
#         print(f"🌐 Language: ur-PK (Unicode Urdu detected: {urdu_chars} chars)")
#         return "ur-PK"

#     # Check Roman Urdu words
#     words = text.lower().split()
#     if len(words) == 0:
#         return "en-US"

#     urdu_word_count = sum(1 for w in words if w.strip('.,?!:;') in ROMAN_URDU_WORDS)
#     ratio = urdu_word_count / len(words)

#     print(f"🌐 Language detection: {urdu_word_count}/{len(words)} Urdu words ({ratio:.0%})")

#     if ratio >= 0.25:
#         print(f"🌐 Language: ur-PK (Roman Urdu)")
#         return "ur-PK"

#     print(f"🌐 Language: en-US")
#     return "en-US"


# def get_voice_agricultural_advice(
#     user_message: str,
#     sensor_data: dict,
#     land_size: float = 1.0,
#     session_id: str = "default"
# ) -> dict:
#     """
#     Get agricultural advice for VOICE interface using Azure OpenAI.
#     Separate from the chat endpoint's llm_agent.
#     Detects language and responds in Urdu or English.
#     """

#     is_urdu = False

#     try:
#         # Detect language
#         language = detect_voice_language(user_message)
#         is_urdu = (language == "ur-PK")

#         # Choose system prompt based on language
#         system_prompt = VOICE_SYSTEM_PROMPT_UR if is_urdu else VOICE_SYSTEM_PROMPT_EN

#         # Build sensor context (in Urdu script if Urdu, else English)
#         if is_urdu:
#             sensor_context = f"""
# موجودہ سینسر ڈیٹا:
# نائٹروجن: {sensor_data.get('nitrogen', 'N/A')} ملی گرام فی کلوگرام
# فاسفورس: {sensor_data.get('phosphorus', 'N/A')} ملی گرام فی کلوگرام
# پوٹاشیم: {sensor_data.get('potassium', 'N/A')} ملی گرام فی کلوگرام
# پی ایچ لیول: {sensor_data.get('ph', 'N/A')}
# درجہ حرارت: {sensor_data.get('temperature', 'N/A')} ڈگری سیلسیس
# نمی: {sensor_data.get('humidity', 'N/A')} فیصد
# ای سی: {sensor_data.get('ec', 'N/A')} مائیکرو سیمنز
# رقبہ: {land_size} ایکڑ
# """
#         else:
#             sensor_context = f"""
# CURRENT SENSOR DATA from IoT device:
# Nitrogen N is {sensor_data.get('nitrogen', 'N/A')} milligrams per kilogram.
# Phosphorus P is {sensor_data.get('phosphorus', 'N/A')} milligrams per kilogram.
# Potassium K is {sensor_data.get('potassium', 'N/A')} milligrams per kilogram.
# pH Level is {sensor_data.get('ph', 'N/A')}.
# Temperature is {sensor_data.get('temperature', 'N/A')} degrees Celsius.
# Humidity is {sensor_data.get('humidity', 'N/A')} percent.
# EC Electrical Conductivity is {sensor_data.get('ec', 'N/A')} microsiemens per centimeter.
# Land Size is {land_size} acres.
# """

#         # Get or create voice session conversation history
#         if session_id not in voice_conversation_sessions:
#             voice_conversation_sessions[session_id] = []

#         history = voice_conversation_sessions[session_id]

#         # Build messages — o4-mini uses "developer" role instead of "system"
#         messages = [
#             {"role": "developer", "content": system_prompt + "\n\n" + sensor_context}
#         ]

#         # Add conversation history (last 6 messages max)
#         messages.extend(history[-6:])

#         # Add current user message with language hint
#         if is_urdu:
#             messages.append({
#                 "role": "user",
#                 "content": f"یہ سوال اردو میں ہے: {user_message}\n\nجواب اردو رسم الخط میں دیں۔ رومن اردو نہیں۔ سینسر ڈیٹا ضرور استعمال کریں۔ بریکٹ اور خاص علامات استعمال نہ کریں۔"
#             })
#         else:
#             messages.append({
#                 "role": "user",
#                 "content": f"{user_message}\n\nRespond in plain conversational English sentences. No brackets, no dashes, no bullet points, no special formatting. Write as if you are speaking to someone."
#             })

#         print(f"📤 Sending to Azure OpenAI ({MODEL_NAME}): {len(messages)} messages")

#         # Call Azure OpenAI
#         response = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=messages,
#             max_completion_tokens=4000
#         )

#         # Extract response
#         ai_response = ""
#         choice = response.choices[0]

#         if choice.message and choice.message.content:
#             ai_response = choice.message.content.strip()

#         if not ai_response:
#             raw_message = choice.message
#             print(f"⚠️ Empty content. Message object: {raw_message}")
#             print(f"⚠️ Full response: {response}")

#             if hasattr(raw_message, 'refusal') and raw_message.refusal:
#                 ai_response = f"Model refused: {raw_message.refusal}"
#             elif hasattr(response, 'usage'):
#                 print(f"📊 Token usage: {response.usage}")

#         if not ai_response:
#             print("❌ AI returned empty response!")
#             if is_urdu:
#                 ai_response = "معذرت، جواب میں مسئلہ آیا۔ دوبارہ کوشش کریں۔"
#             else:
#                 ai_response = "Sorry, the AI did not return a response. Please try again."

#         print(f"🤖 AI Response length: {len(ai_response)} chars")
#         print(f"🤖 AI Response preview: {ai_response[:200]}")

#         # Save to voice conversation history
#         history.append({"role": "user", "content": user_message})
#         history.append({"role": "assistant", "content": ai_response})

#         # Keep only last 10 messages
#         if len(history) > 10:
#             voice_conversation_sessions[session_id] = history[-10:]

#         return {
#             "response": ai_response,
#             "language": language,
#             "sensor_data_used": sensor_data
#         }

#     except Exception as e:
#         print(f"❌ Voice LLM Error: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         if is_urdu:
#             return {
#                 "response": "معذرت، جواب میں مسئلہ آیا۔ دوبارہ کوشش کریں۔",
#                 "language": "ur-PK",
#                 "sensor_data_used": sensor_data
#             }
#         return {
#             "response": "Sorry, there was an error getting advice. Please try again.",
#             "language": "en-US",
#             "sensor_data_used": sensor_data
#         }


# def clear_voice_session(session_id: str):
#     """Clear voice conversation history for a session"""
#     if session_id in voice_conversation_sessions:
#         del voice_conversation_sessions[session_id]
#         print(f"🗑️ Voice session cleared: {session_id}")































import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from typing import Optional
import json
import re

load_dotenv()

# Initialize Azure OpenAI client (NOT regular OpenAI)
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
)

MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL_NAME", "o4-mini")

print(f"🤖 Voice LLM: Azure OpenAI ({MODEL_NAME})")

# Store conversation history per session (separate from chat endpoint)
voice_conversation_sessions = {}

VOICE_SYSTEM_PROMPT_EN = """You are Dr. AgriBot, an expert agricultural advisor for Pakistani farmers.
You are speaking through a VOICE interface, so keep responses clear and concise for speech.

RULES:
1. ONLY answer farming/agriculture questions. Reject everything else politely.
2. You MUST use the sensor data provided to give specific, actionable advice.
3. Answer the user's SPECIFIC question using sensor data.
4. If user asks about watering, focus on watering advice.
5. If user asks about fertilizer, focus on fertilizer advice.
6. If user asks which crop to plant or which crop is best for their land, give crop recommendations based on soil data.
7. If user just greets, introduce yourself briefly and ask how to help.
8. Keep responses SHORT (under 200 words) since this is voice output.
9. Do NOT use emojis or special symbols in the response since it will be read aloud by TTS.
10. Do NOT use brackets, dashes, colons, bullet points or any special formatting.
11. Write in plain conversational sentences that sound natural when spoken aloud.

For CROP RECOMMENDATION questions, structure your spoken response like this:
First mention the top crop choice and why the soil suits it based on actual sensor values.
Then mention the fertilizer needed for that crop in kilograms.
Then briefly mention second and third best crop options.
Finally mention one or two crops to avoid and why based on the soil data.
Keep it conversational and natural for voice.

Example good response:
Your soil nitrogen is 300 milligrams per kilogram which is good for healthy leaf growth.
Phosphorus is 327 milligrams per kilogram which is high so you don't need extra phosphorus fertilizer.
Potassium is 340 milligrams per kilogram which is also high.
Your soil pH is 7.9 which is alkaline and may reduce micronutrient availability.
For fertilizer, you don't need additional NPK right now since all levels are adequate.
For watering, with humidity at 28 percent, water every 2 days. Best time is early morning 6 to 9 AM.
"""

VOICE_SYSTEM_PROMPT_UR = """آپ ڈاکٹر ایگری بوٹ ہیں، پاکستانی کسانوں کے لیے ایک ماہر زرعی مشیر۔
آپ وائس انٹرفیس سے بات کر رہے ہیں، تو جواب صاف اور مختصر رکھیں۔

قواعد:
1. صرف کھیتی اور زراعت کے سوالوں کا جواب دیں۔ باقی سب کو شائستگی سے مسترد کریں۔
2. سینسر ڈیٹا کا استعمال کر کے مخصوص اور عملی مشورہ دینا لازمی ہے۔
3. صارف کے خاص سوال کا جواب سینسر ڈیٹا سے دیں۔
4. اگر صارف پانی کے بارے میں پوچھے تو پانی پر فوکس کریں۔
5. اگر صارف کھاد کے بارے میں پوچھے تو کھاد پر فوکس کریں۔
6. اگر صارف پوچھے کہ کون سی فصل لگائیں یا زمین کے لیے بہترین فصل کون سی ہے، تو مٹی کے ڈیٹا کی بنیاد پر فصل کی سفارش کریں۔
7. اگر صارف صرف سلام کرے تو اپنا مختصر تعارف دیں۔
8. جواب مختصر رکھیں کیونکہ یہ وائس آؤٹ پٹ ہے۔
9. جواب میں ایموجی یا خاص نشانیاں بالکل استعمال نہ کریں۔
10. جواب ہمیشہ اردو رسم الخط میں لکھیں۔ رومن اردو ہرگز استعمال نہ کریں۔
11. انگریزی الفاظ کو اردو میں لکھیں۔ مثلاً نائٹروجن، فاسفورس، پوٹاشیم، پی ایچ۔
12. اعداد بھی اردو میں لکھیں مثلاً تین سو ملی گرام فی کلوگرام۔
13. بریکٹ، ڈیش، کولن، بلٹ پوائنٹ جیسی کوئی علامت استعمال نہ کریں۔
14. سادہ بول چال کے جملے لکھیں جو بولنے میں فطری لگیں۔

فصل کی سفارش کے سوالوں کے لیے جواب اس طرح دیں:
پہلے بتائیں کہ مٹی کے ڈیٹا کی بنیاد پر کون سی فصل سب سے بہتر ہے اور کیوں۔
پھر اس فصل کے لیے کتنی کھاد چاہیے وہ بتائیں۔
پھر دوسری اور تیسری بہترین فصلوں کا مختصر ذکر کریں۔
آخر میں ایک دو فصلیں بتائیں جن سے بچنا چاہیے اور کیوں۔
جواب بول چال کے انداز میں فطری رکھیں۔

مثال اچھا جواب:
آپ کی زمین میں نائٹروجن تین سو ملی گرام فی کلوگرام ہے جو اچھی مقدار ہے اور پتوں کی صحت مند نشوونما کے لیے کافی ہے۔ فاسفورس تین سو ستائیس ملی گرام فی کلوگرام ہے جو زیادہ ہے اس لیے اضافی فاسفورس کھاد کی ضرورت نہیں۔ پوٹاشیم تین سو چالیس ملی گرام فی کلوگرام ہے جو بھی کافی ہے۔ پی ایچ لیول سات اعشاریہ نو ہے جو قلعی ہے۔ کھاد کے لیے ابھی اضافی این پی کے کی ضرورت نہیں۔ پانی کے لیے نمی اٹھائیس فیصد ہے تو ہر دو دن بعد پانی دیں۔ بہترین وقت صبح چھ سے نو بجے ہے۔
"""


# Common Roman Urdu words for language detection
ROMAN_URDU_WORDS = {
    'mujhe', 'mujhay', 'mein', 'main', 'hai', 'hain', 'kya', 'kyun',
    'kaise', 'kab', 'kahan', 'kon', 'kaun', 'aur', 'ya', 'se', 'ka', 'ke', 'ki',
    'ko', 'par', 'pe', 'ne', 'ho', 'hona', 'karna', 'dena', 'lena',
    'batao', 'bata', 'bataye', 'bataen', 'btao', 'btaye', 'bataiye',
    'fasal', 'kheti', 'khet', 'zameen', 'zamin', 'mitti',
    'pani', 'paani', 'khad', 'beej', 'bij',
    'gandum', 'chawal', 'makki', 'kapas', 'ganna', 'sarson',
    'haan', 'nahi', 'nhi', 'ji', 'shukriya', 'meherbani',
    'kitna', 'kitni', 'kitne', 'kaunsa', 'kaunsi', 'konsa', 'konsi',
    'chahiye', 'chahie', 'zaroorat', 'zarurat',
    'abhi', 'pehle', 'baad', 'kal', 'aaj',
    'apni', 'apna', 'apne', 'mera', 'meri', 'mere',
    'zyada', 'kam', 'acha', 'achi', 'bura', 'theek', 'thik',
    'waqt', 'din', 'raat', 'subah', 'shaam', 'dopahar',
    'lagana', 'lagao', 'dalna', 'dalo', 'daalna',
    'ye', 'yeh', 'woh', 'wo', 'is', 'us', 'iska', 'uska',
    'kaisa', 'kaisi', 'kaise', 'achha', 'achhi',
    'hum', 'tum', 'aap', 'yahan', 'wahan',
    'sab', 'kuch', 'bohat', 'bahut', 'thoda', 'thodi',
    # crop recommendation Roman Urdu keywords
    'konsi', 'fasal', 'lagaon', 'lgaon', 'lgaun', 'lagaun',
    'konsa', 'behtareen', 'behtar', 'best', 'kaun', 'kaisi',
    'zameen', 'zamin', 'mitti', 'khet', 'kheti',
}

# Crop recommendation keywords
CROP_KEYWORDS_EN = [
    "which crop", "what crop", "what should i plant", "which plant",
    "best crop", "recommend crop", "crop recommendation", "suggest crop",
    "what to grow", "what can i grow", "which vegetable", "which fruit",
    "suitable crop", "good crop for my land", "crop for my soil",
    "what crop should", "which crop should", "crop to plant",
    "plant on my land", "grow on my land", "best for my soil",
    "wheat or rice", "which farming"
]

CROP_KEYWORDS_UR = [
    "کون سی فصل", "کونسی فصل", "فصل لگاؤں", "فصل لگانی",
    "کیا لگاؤں", "کیا اگاؤں", "فصل کی سفارش", "فصل بتائیں",
    "کون سی سبزی", "بہترین فصل", "زمین پر فصل", "مٹی کے لیے فصل",
    "کون سی کاشت", "فصل کاشت"
]

CROP_KEYWORDS_ROMAN_UR = [
    "konsi fasal", "kaunsi fasal", "kaun si fasal",
    "fasal lagaon", "fasal lgaon", "fasal lagaun",
    "konsa fasal", "best fasal", "behtareen fasal",
    "zameen pe kya", "khet mein kya", "mitti ke liye",
    "fasal batao", "fasal suggest", "kaun si fasal lagaon",
    "kya lagaon", "kya ugaon", "kya kaasht"
]


def detect_voice_language(text: str) -> str:
    """
    Detect if voice text is Urdu (Unicode Urdu or Roman Urdu) or English.
    Returns 'ur-PK' or 'en-US'
    """

    # Check Unicode Urdu characters first
    urdu_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
    if urdu_chars > 3:
        print(f"🌐 Language: ur-PK (Unicode Urdu detected: {urdu_chars} chars)")
        return "ur-PK"

    # Check Roman Urdu words
    words = text.lower().split()
    if len(words) == 0:
        return "en-US"

    urdu_word_count = sum(1 for w in words if w.strip('.,?!:;') in ROMAN_URDU_WORDS)
    ratio = urdu_word_count / len(words)

    print(f"🌐 Language detection: {urdu_word_count}/{len(words)} Urdu words ({ratio:.0%})")

    if ratio >= 0.25:
        print(f"🌐 Language: ur-PK (Roman Urdu)")
        return "ur-PK"

    print(f"🌐 Language: en-US")
    return "en-US"


def is_crop_recommendation_question(text: str, language: str) -> bool:
    """
    Detect if the user is asking which crop to plant on their land.
    Handles English, Unicode Urdu, and Roman Urdu.
    """
    text_lower = text.lower()

    # Unicode Urdu check
    if language == "ur-PK":
        if any(kw in text for kw in CROP_KEYWORDS_UR):
            return True

    # Roman Urdu check (even if detected as English, cover it)
    if any(kw in text_lower for kw in CROP_KEYWORDS_ROMAN_UR):
        return True

    # English check
    if any(kw in text_lower for kw in CROP_KEYWORDS_EN):
        return True

    return False


def get_crop_recommendation_context(
    sensor_data: dict,
    land_size: float,
    language: str
) -> str:
    """
    Build a crop-recommendation-specific context string injected into the prompt.
    Uses agronomic base doses so fertilizer amounts are never zero.
    """
    n    = sensor_data.get('nitrogen',    0)
    p    = sensor_data.get('phosphorus',  0)
    k    = sensor_data.get('potassium',   0)
    ph   = sensor_data.get('ph',          7.0)
    temp = sensor_data.get('temperature', 25)
    hum  = sensor_data.get('humidity',    50)

    # Status labels
    n_s = "low"      if n < 200  else "high"      if n > 400  else "good"
    p_s = "low"      if p < 15   else "high"       if p > 30   else "good"
    k_s = "low"      if k < 150  else "high"       if k > 280  else "good"
    ph_s = "acidic"  if ph < 6.0 else "alkaline"   if ph > 7.5 else "neutral/good"

    # Best 3 crops based on soil profile
    best1 = "Wheat"     if 6.0 <= ph <= 7.5 else "Maize"
    best2 = "Potato"    if k >= 150          else "Onion"
    best3 = "Mustard"   if temp <= 25        else "Sunflower"

    # Crop-specific base doses (kg/acre) — Pakistan agronomic standards
    BASE_UREA = {"Wheat": 40, "Maize": 50, "Potato": 30, "Onion": 25, "Mustard": 30, "Sunflower": 35}
    BASE_DAP  = {"Wheat": 25, "Maize": 30, "Potato": 35, "Onion": 20, "Mustard": 20, "Sunflower": 25}
    BASE_MOP  = {"Wheat": 15, "Maize": 20, "Potato": 30, "Onion": 15, "Mustard": 10, "Sunflower": 15}

    def dose(base_dict, crop, nutrient_val, low_t, high_t):
        base = base_dict.get(crop, 25) * land_size
        if nutrient_val > high_t:   return round(base * 0.6, 1)   # already high — reduce
        elif nutrient_val < low_t:  return round(base * 1.3, 1)   # deficient — increase
        else:                       return round(base,        1)   # good — standard dose

    c1 = (dose(BASE_UREA, best1, n, 200, 400), dose(BASE_DAP, best1, p, 15, 30), dose(BASE_MOP, best1, k, 150, 280))
    c2 = (dose(BASE_UREA, best2, n, 200, 400), dose(BASE_DAP, best2, p, 15, 30), dose(BASE_MOP, best2, k, 150, 280))
    c3 = (dose(BASE_UREA, best3, n, 200, 400), dose(BASE_DAP, best3, p, 15, 30), dose(BASE_MOP, best3, k, 150, 280))

    water_advice = (
        "irrigate every 3 to 4 days since humidity is very low"  if hum < 35 else
        "irrigate every 5 to 6 days"                             if hum < 60 else
        "irrigate every 8 to 10 days since soil moisture is adequate"
    )

    if language == "ur-PK":
        water_ur = (
            "نمی بہت کم ہے اس لیے ہر تین سے چار دن بعد پانی دیں"  if hum < 35 else
            "ہر پانچ سے چھ دن بعد پانی دیں"                         if hum < 60 else
            "نمی کافی ہے اس لیے ہر آٹھ سے دس دن بعد پانی دیں"
        )
        avoid = "چاول" if ph > 7.5 or hum < 40 else "کپاس" if ph < 6.5 else "گنا"
        context = f"""
فصل کی سفارش کے لیے اضافی تجزیہ:
بہترین پہلی فصل: {best1} — یوریا {c1[0]} کلوگرام، ڈی اے پی {c1[1]} کلوگرام، ایم او پی {c1[2]} کلوگرام ({land_size} ایکڑ کے لیے)
بہترین دوسری فصل: {best2} — یوریا {c2[0]} کلوگرام، ڈی اے پی {c2[1]} کلوگرام، ایم او پی {c2[2]} کلوگرام
بہترین تیسری فصل: {best3} — یوریا {c3[0]} کلوگرام، ڈی اے پی {c3[1]} کلوگرام، ایم او پی {c3[2]} کلوگرام
جس فصل سے بچیں: {avoid}
آبپاشی: {water_ur}
نائٹروجن حالت: {n_s} ({n} ملی گرام فی کلوگرام)
فاسفورس حالت: {p_s} ({p} ملی گرام فی کلوگرام)
پوٹاشیم حالت: {k_s} ({k} ملی گرام فی کلوگرام)
پی ایچ حالت: {ph_s} ({ph})
ان اعداد و شمار کی بنیاد پر وائس کے لیے مناسب جواب دیں۔ اعداد اردو میں لکھیں اور بولنے میں فطری لگیں۔
"""
    else:
        avoid = "Rice" if ph > 7.5 or hum < 40 else "Cotton" if ph < 6.5 else "Sugarcane"
        context = f"""
CROP RECOMMENDATION ANALYSIS:
Best 1st crop: {best1} — Urea {c1[0]} kg, DAP {c1[1]} kg, MOP {c1[2]} kg (for {land_size} acres)
Best 2nd crop: {best2} — Urea {c2[0]} kg, DAP {c2[1]} kg, MOP {c2[2]} kg
Best 3rd crop: {best3} — Urea {c3[0]} kg, DAP {c3[1]} kg, MOP {c3[2]} kg
Crop to avoid: {avoid}
Watering: {water_advice}
Nitrogen status: {n_s} ({n} mg/kg)
Phosphorus status: {p_s} ({p} mg/kg)
Potassium status: {k_s} ({k} mg/kg)
pH status: {ph_s} ({ph})
Use these calculated values in your voice response. Speak naturally without any special formatting.
"""
    return context


def get_voice_agricultural_advice(
    user_message: str,
    sensor_data: dict,
    land_size: float = 1.0,
    session_id: str = "default"
) -> dict:
    """
    Get agricultural advice for VOICE interface using Azure OpenAI.
    Separate from the chat endpoint's llm_agent.
    Detects language and responds in Urdu or English.
    """

    is_urdu = False

    try:
        # Detect language
        language = detect_voice_language(user_message)
        is_urdu = (language == "ur-PK")

        # Detect if this is a crop recommendation question
        crop_question = is_crop_recommendation_question(user_message, language)
        if crop_question:
            print(f"🌱 Crop recommendation question detected")

        # Choose system prompt based on language
        system_prompt = VOICE_SYSTEM_PROMPT_UR if is_urdu else VOICE_SYSTEM_PROMPT_EN

        # Build sensor context (in Urdu script if Urdu, else English)
        if is_urdu:
            sensor_context = f"""
موجودہ سینسر ڈیٹا:
نائٹروجن: {sensor_data.get('nitrogen', 'N/A')} ملی گرام فی کلوگرام
فاسفورس: {sensor_data.get('phosphorus', 'N/A')} ملی گرام فی کلوگرام
پوٹاشیم: {sensor_data.get('potassium', 'N/A')} ملی گرام فی کلوگرام
پی ایچ لیول: {sensor_data.get('ph', 'N/A')}
درجہ حرارت: {sensor_data.get('temperature', 'N/A')} ڈگری سیلسیس
نمی: {sensor_data.get('humidity', 'N/A')} فیصد
ای سی: {sensor_data.get('ec', 'N/A')} مائیکرو سیمنز
رقبہ: {land_size} ایکڑ
"""
        else:
            sensor_context = f"""
CURRENT SENSOR DATA from IoT device:
Nitrogen N is {sensor_data.get('nitrogen', 'N/A')} milligrams per kilogram.
Phosphorus P is {sensor_data.get('phosphorus', 'N/A')} milligrams per kilogram.
Potassium K is {sensor_data.get('potassium', 'N/A')} milligrams per kilogram.
pH Level is {sensor_data.get('ph', 'N/A')}.
Temperature is {sensor_data.get('temperature', 'N/A')} degrees Celsius.
Humidity is {sensor_data.get('humidity', 'N/A')} percent.
EC Electrical Conductivity is {sensor_data.get('ec', 'N/A')} microsiemens per centimeter.
Land Size is {land_size} acres.
"""

        # If crop question, append the pre-calculated crop recommendation context
        if crop_question:
            sensor_context += get_crop_recommendation_context(sensor_data, land_size, language)

        # Get or create voice session conversation history
        if session_id not in voice_conversation_sessions:
            voice_conversation_sessions[session_id] = []

        history = voice_conversation_sessions[session_id]

        # Build messages — o4-mini uses "developer" role instead of "system"
        messages = [
            {"role": "developer", "content": system_prompt + "\n\n" + sensor_context}
        ]

        # Add conversation history (last 6 messages max)
        messages.extend(history[-6:])

        # Add current user message with language hint
        if is_urdu:
            if crop_question:
                messages.append({
                    "role": "user",
                    "content": f"یہ سوال اردو میں ہے: {user_message}\n\nاوپر دیے گئے سینسر ڈیٹا اور فصل کی سفارش کے تجزیے کی بنیاد پر جواب دیں۔ جواب اردو رسم الخط میں دیں۔ رومن اردو نہیں۔ بریکٹ اور خاص علامات استعمال نہ کریں۔ اعداد اردو میں بولیں۔"
                })
            else:
                messages.append({
                    "role": "user",
                    "content": f"یہ سوال اردو میں ہے: {user_message}\n\nجواب اردو رسم الخط میں دیں۔ رومن اردو نہیں۔ سینسر ڈیٹا ضرور استعمال کریں۔ بریکٹ اور خاص علامات استعمال نہ کریں۔"
                })
        else:
            if crop_question:
                messages.append({
                    "role": "user",
                    "content": f"{user_message}\n\nUse the crop recommendation analysis above to answer. Respond in plain conversational English sentences. No brackets, no dashes, no bullet points, no special formatting. Write as if you are speaking to someone."
                })
            else:
                messages.append({
                    "role": "user",
                    "content": f"{user_message}\n\nRespond in plain conversational English sentences. No brackets, no dashes, no bullet points, no special formatting. Write as if you are speaking to someone."
                })

        print(f"📤 Sending to Azure OpenAI ({MODEL_NAME}): {len(messages)} messages | crop_question={crop_question}")

        # Call Azure OpenAI
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_completion_tokens=4000
        )

        # Extract response
        ai_response = ""
        choice = response.choices[0]

        if choice.message and choice.message.content:
            ai_response = choice.message.content.strip()

        if not ai_response:
            raw_message = choice.message
            print(f"⚠️ Empty content. Message object: {raw_message}")
            print(f"⚠️ Full response: {response}")

            if hasattr(raw_message, 'refusal') and raw_message.refusal:
                ai_response = f"Model refused: {raw_message.refusal}"
            elif hasattr(response, 'usage'):
                print(f"📊 Token usage: {response.usage}")

        if not ai_response:
            print("❌ AI returned empty response!")
            if is_urdu:
                ai_response = "معذرت، جواب میں مسئلہ آیا۔ دوبارہ کوشش کریں۔"
            else:
                ai_response = "Sorry, the AI did not return a response. Please try again."

        print(f"🤖 AI Response length: {len(ai_response)} chars")
        print(f"🤖 AI Response preview: {ai_response[:200]}")

        # Save to voice conversation history
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": ai_response})

        # Keep only last 10 messages
        if len(history) > 10:
            voice_conversation_sessions[session_id] = history[-10:]

        return {
            "response": ai_response,
            "language": language,
            "sensor_data_used": sensor_data
        }

    except Exception as e:
        print(f"❌ Voice LLM Error: {str(e)}")
        import traceback
        traceback.print_exc()
        if is_urdu:
            return {
                "response": "معذرت، جواب میں مسئلہ آیا۔ دوبارہ کوشش کریں۔",
                "language": "ur-PK",
                "sensor_data_used": sensor_data
            }
        return {
            "response": "Sorry, there was an error getting advice. Please try again.",
            "language": "en-US",
            "sensor_data_used": sensor_data
        }


def clear_voice_session(session_id: str):
    """Clear voice conversation history for a session"""
    if session_id in voice_conversation_sessions:
        del voice_conversation_sessions[session_id]
        print(f"🗑️ Voice session cleared: {session_id}")