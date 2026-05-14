# from langchain_openai import AzureChatOpenAI
# from langchain_core.messages import SystemMessage, HumanMessage
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # ============================================
# # AGRICHECK PUBLIC AGENT
# # Dashboard LLM Button - No Auth Required
# # ============================================

# # Azure Config
# AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_MODEL_NAME")
# AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# # Intent Types
# GENERAL_INFO = "GENERAL_INFO"
# DETAIL_REQUIRED = "DETAIL_REQUIRED"
# OFF_TOPIC = "OFF_TOPIC"

# # Short Feature Summary
# AGRICHECK_FEATURES = """
# 🌱 AgriCheck helps you monitor soil health (NPK, pH, EC, Temp, Humidity), get AI-powered crop advice in Urdu & English, and receive smart fertilizer recommendations — all in real time!

# 👉 Login or Sign Up to get started!
# """

# # Login Required Message
# LOGIN_REQUIRED_MESSAGE = """🔒 I'd love to help with your soil data! But to see your real-time readings and get personalized advice, you'll need an account.

# 👉 Please Login or Sign Up — it's free and takes only a minute!"""

# # Off-Topic Message
# OFF_TOPIC_MESSAGE = """😊 That's an interesting question! But I'm AgriCheck's farming assistant — I'm best at helping with soil health, crops, and agriculture.

# Feel free to ask me anything about farming! For example: "What does AgriCheck do?" or "How can I improve my soil?"

# 👉 Login or Sign Up to get personalized soil advice!"""


# def get_llm():
#     """Initialize Azure OpenAI LLM"""
#     return AzureChatOpenAI(
#         azure_endpoint=AZURE_ENDPOINT,
#         openai_api_key=AZURE_API_KEY,
#         deployment_name=AZURE_DEPLOYMENT,
#         openai_api_version=AZURE_API_VERSION,
#         max_tokens=200,
#         streaming=False
#     )


# async def classify_intent(user_message: str) -> str:
#     """
#     Classify user intent into 3 categories:
#     - GENERAL_INFO: About AgriCheck or general farming
#     - DETAIL_REQUIRED: Needs specific sensor data
#     - OFF_TOPIC: Not related to agriculture at all
#     """

#     llm = get_llm()

#     classification_prompt = f"""
# You are an intent classifier for AgriCheck (a farming/agriculture app).

# Classify this message into EXACTLY one category:

# 1. GENERAL_INFO - Questions about:
#    - AgriCheck features, services, how it works
#    - General farming, crops, soil, agriculture topics
#    - Getting started, pricing

# 2. DETAIL_REQUIRED - Questions about:
#    - Their specific sensor readings (NPK, pH, EC values)
#    - Their farm data, history, trends
#    - Specific crop recommendations for their land
#    - Personalized soil analysis

# 3. OFF_TOPIC - Questions about:
#    - Driving, cooking, sports, movies, gaming
#    - Programming, math, science (non-agriculture)
#    - Personal advice, relationships
#    - Anything NOT related to farming or AgriCheck

# Message: "{user_message}"

# Reply ONLY one word: GENERAL_INFO or DETAIL_REQUIRED or OFF_TOPIC
# """

#     response = await llm.ainvoke([
#         HumanMessage(content=classification_prompt)
#     ])

#     intent = response.content.strip().upper().replace(" ", "_")

#     # Validate
#     if intent not in [GENERAL_INFO, DETAIL_REQUIRED, OFF_TOPIC]:
#         # Fallback keyword check
#         message_lower = user_message.lower()

#         detail_keywords = [
#             "my data", "my reading", "my soil", "my farm", "my field",
#             "nitrogen level", "ph level", "current", "history", "trend",
#             "meri zameen", "mera data", "mera khet", "sensor data"
#         ]

#         agri_keywords = [
#             "soil", "crop", "farm", "fertilizer", "npk", "ph", "seed",
#             "agri", "plant", "harvest", "irrigation", "khet", "fasal",
#             "zameen", "khad", "pani", "beej"
#         ]

#         if any(kw in message_lower for kw in detail_keywords):
#             return DETAIL_REQUIRED
#         elif any(kw in message_lower for kw in agri_keywords):
#             return GENERAL_INFO
#         else:
#             return OFF_TOPIC

#     return intent


# async def generate_general_response(user_message: str) -> str:
#     """Generate short, simple & unique response for each question"""

#     llm = get_llm()

#     system_prompt = """You are AgriCheck's friendly AI Assistant.

# STRICT RULES:
# 1. Reply in MAX 2-3 short sentences
# 2. Use very simple and easy words — like talking to a farmer
# 3. If user writes Urdu, reply in Urdu (Roman or Nastaliq)
# 4. If user writes English, reply in English
# 5. NEVER share actual sensor data — you don't have access
# 6. Always end with: "Login or Sign Up to explore more! 🌱"
# 7. No bullet points, no long lists — just plain friendly sentences
# 8. Give a DIFFERENT answer each time — don't repeat yourself
# 9. If asked about general farming (not AgriCheck specific), give a short helpful tip then mention AgriCheck can help more

# AgriCheck = Soil monitoring app (NPK, pH, EC, Temp, Humidity) + AI crop advice in Urdu & English + Smart fertilizer & irrigation tips + ESP32 IoT sensors"""

#     response = await llm.ainvoke([
#         SystemMessage(content=system_prompt),
#         HumanMessage(content=user_message)
#     ])

#     result = response.content.strip()

#     # Safety: if empty response, return features
#     if not result or len(result) < 5:
#         return AGRICHECK_FEATURES.strip()

#     return result


# async def public_chat_agent(user_message: str) -> dict:
#     """
#     Main Public Chat Agent - Dashboard LLM Button

#     Flow:
#     1. Classify intent (GENERAL_INFO / DETAIL_REQUIRED / OFF_TOPIC)
#     2. GENERAL_INFO → AI generates unique helpful response
#     3. DETAIL_REQUIRED → Login required message
#     4. OFF_TOPIC → Polite diversion to farming
#     """

#     try:
#         intent = await classify_intent(user_message)
#     except Exception as e:
#         print(f"❌ Intent Error: {e}")
#         intent = GENERAL_INFO

#     if intent == GENERAL_INFO:
#         try:
#             response_text = await generate_general_response(user_message)
#         except Exception as e:
#             print(f"❌ Response Error: {e}")
#             response_text = AGRICHECK_FEATURES.strip()
#         requires_login = False
#         show_features = True

#     elif intent == DETAIL_REQUIRED:
#         response_text = LOGIN_REQUIRED_MESSAGE
#         requires_login = True
#         show_features = False

#     else:  # OFF_TOPIC
#         response_text = OFF_TOPIC_MESSAGE
#         requires_login = False
#         show_features = False

#     return {
#         "response": response_text,
#         "intent": intent,
#         "requires_login": requires_login,
#         "show_features": show_features,
#         "agricheck_features": AGRICHECK_FEATURES.strip() if show_features else None
#     }
















































from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# AGRICHECK PUBLIC AGENT
# Dashboard LLM Button - No Auth Required
# ============================================

# Azure Config
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_MODEL_NAME")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Intent Types
GENERAL_INFO = "GENERAL_INFO"
DETAIL_REQUIRED = "DETAIL_REQUIRED"
OFF_TOPIC = "OFF_TOPIC"
GREETING = "GREETING"
GOODBYE = "GOODBYE"

# Short Feature Summary
AGRICHECK_FEATURES = """
🌱 AgriCheck helps you monitor soil health (NPK, pH, EC, Temp, Humidity), get AI-powered crop advice in Urdu & English, and receive smart fertilizer recommendations — all in real time!

👉 Login or Sign Up to get started!
"""

# Login Required Message
LOGIN_REQUIRED_MESSAGE = """🔒 I'd love to help with your soil data! But to see your real-time readings and get personalized advice, you'll need an account.

👉 Please Login or Sign Up — it's free and takes only a minute!"""

# Off-Topic Message
OFF_TOPIC_MESSAGE = """😊 That's an interesting question! But I'm AgriCheck's farming assistant — I'm best at helping with soil health, crops, and agriculture.

Feel free to ask me anything about farming! For example: "What does AgriCheck do?" or "How can I improve my soil?"

👉 Login or Sign Up to get personalized soil advice!"""

# Greeting Messages
GREETING_MESSAGES = [
    "👋 Hello! Welcome to AgriCheck! I'm your farming assistant. Ask me anything about soil health, crops, or how AgriCheck works! 🌱",
    "👋 Assalam-o-Alaikum! AgriCheck mein khush aamdeed! Mujhse zameen, fasal ya AgriCheck ke baare mein kuch bhi poochein! 🌾",
]

# Goodbye Messages
GOODBYE_MESSAGES = [
    "👋 Goodbye! Happy farming! Come back anytime you need soil advice. Login or Sign Up to unlock full features! 🌱",
    "👋 Allah Hafiz! Khush raho aur kheti mein kamyab raho! AgriCheck hamesha aapke saath hai! 🌾",
]


def get_llm():
    """Initialize Azure OpenAI LLM"""
    return AzureChatOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        openai_api_key=AZURE_API_KEY,
        deployment_name=AZURE_DEPLOYMENT,
        openai_api_version=AZURE_API_VERSION,
        max_tokens=200,
        streaming=False
    )


def quick_intent_check(user_message: str) -> str:
    """
    Fast keyword-based check for greetings & goodbyes
    No LLM call needed — saves time & tokens!
    """
    msg = user_message.lower().strip()

    greeting_keywords = [
        "hi", "hello", "hey", "hola", "good morning", "good afternoon",
        "good evening", "good to meet you", "nice to meet you",
        "howdy", "sup", "what's up", "whats up",
        "assalam", "salam", "aoa", "aslam o alaikum",
        "assalamualaikum", "walaikum", "kya hal hai",
        "how are you", "how r u", "hru"
    ]

    goodbye_keywords = [
        "bye", "goodbye", "good bye", "see you", "see ya",
        "take care", "later", "cya", "gtg", "gotta go",
        "thanks bye", "thank you bye", "ok bye",
        "allah hafiz", "khuda hafiz", "fi aman allah",
        "alvida", "phir milte hain", "chalta hun"
    ]

    # Check greetings
    for kw in greeting_keywords:
        if kw in msg or msg == kw:
            return GREETING

    # Check goodbyes
    for kw in goodbye_keywords:
        if kw in msg or msg == kw:
            return GOODBYE

    return None


async def classify_intent(user_message: str) -> str:
    """
    Classify user intent into 5 categories:
    - GREETING: Hi, Hello, etc
    - GOODBYE: Bye, See you, etc
    - GENERAL_INFO: About AgriCheck or general farming
    - DETAIL_REQUIRED: Needs specific sensor data
    - OFF_TOPIC: Not related to agriculture at all
    """

    # Step 1: Fast check for greetings/goodbyes (no LLM needed)
    quick_result = quick_intent_check(user_message)
    if quick_result:
        return quick_result

    # Step 2: LLM for complex classification
    llm = get_llm()

    classification_prompt = f"""
You are an intent classifier for AgriCheck (a farming/agriculture app).

Classify this message into EXACTLY one category:

1. GENERAL_INFO - Questions about:
   - AgriCheck features, services, how it works
   - General farming, crops, soil, agriculture topics
   - Getting started, pricing

2. DETAIL_REQUIRED - Questions about:
   - Their specific sensor readings (NPK, pH, EC values)
   - Their farm data, history, trends
   - Specific crop recommendations for their land
   - Personalized soil analysis

3. OFF_TOPIC - Questions about:
   - Driving, cooking, sports, movies, gaming
   - Programming, math, science (non-agriculture)
   - Personal advice, relationships
   - Anything NOT related to farming or AgriCheck

Message: "{user_message}"

Reply ONLY one word: GENERAL_INFO or DETAIL_REQUIRED or OFF_TOPIC
"""

    response = await llm.ainvoke([
        HumanMessage(content=classification_prompt)
    ])

    intent = response.content.strip().upper().replace(" ", "_")

    # Validate
    if intent not in [GENERAL_INFO, DETAIL_REQUIRED, OFF_TOPIC]:
        message_lower = user_message.lower()

        detail_keywords = [
            "my data", "my reading", "my soil", "my farm", "my field",
            "nitrogen level", "ph level", "current", "history", "trend",
            "meri zameen", "mera data", "mera khet", "sensor data"
        ]

        agri_keywords = [
            "soil", "crop", "farm", "fertilizer", "npk", "ph", "seed",
            "agri", "plant", "harvest", "irrigation", "khet", "fasal",
            "zameen", "khad", "pani", "beej"
        ]

        if any(kw in message_lower for kw in detail_keywords):
            return DETAIL_REQUIRED
        elif any(kw in message_lower for kw in agri_keywords):
            return GENERAL_INFO
        else:
            return OFF_TOPIC

    return intent


async def generate_general_response(user_message: str) -> str:
    """Generate short, simple & unique response"""

    llm = get_llm()

    system_prompt = """You are AgriCheck's friendly AI Assistant.

STRICT RULES:
1. Reply in MAX 2-3 short sentences
2. Use very simple and easy words — like talking to a farmer
3. If user writes Urdu, reply in Urdu (Roman or Nastaliq)
4. If user writes English, reply in English
5. NEVER share actual sensor data — you don't have access
6. Always end with: "Login or Sign Up to explore more! 🌱"
7. No bullet points, no long lists — just plain friendly sentences
8. Give a DIFFERENT answer each time — don't repeat yourself
9. If asked about general farming (not AgriCheck specific), give a short helpful tip then mention AgriCheck can help more

AgriCheck = Soil monitoring app (NPK, pH, EC, Temp, Humidity) + AI crop advice in Urdu & English + Smart fertilizer & irrigation tips + ESP32 IoT sensors"""

    response = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ])

    result = response.content.strip()

    if not result or len(result) < 5:
        return AGRICHECK_FEATURES.strip()

    return result


def get_greeting_response(user_message: str) -> str:
    """Pick greeting based on language"""
    msg = user_message.lower()
    urdu_keywords = ["assalam", "salam", "aoa", "kya hal", "aslam"]

    if any(kw in msg for kw in urdu_keywords):
        return GREETING_MESSAGES[1]  # Urdu greeting
    return GREETING_MESSAGES[0]  # English greeting


def get_goodbye_response(user_message: str) -> str:
    """Pick goodbye based on language"""
    msg = user_message.lower()
    urdu_keywords = ["allah hafiz", "khuda hafiz", "alvida", "phir milte", "chalta"]

    if any(kw in msg for kw in urdu_keywords):
        return GOODBYE_MESSAGES[1]  # Urdu goodbye
    return GOODBYE_MESSAGES[0]  # English goodbye


async def public_chat_agent(user_message: str) -> dict:
    """
    Main Public Chat Agent - Dashboard LLM Button

    Flow:
    1. GREETING → Friendly welcome
    2. GOODBYE → Warm farewell
    3. GENERAL_INFO → AI generates unique helpful response
    4. DETAIL_REQUIRED → Login required message
    5. OFF_TOPIC → Polite diversion to farming
    """

    try:
        intent = await classify_intent(user_message)
    except Exception as e:
        print(f"❌ Intent Error: {e}")
        intent = GENERAL_INFO

    if intent == GREETING:
        response_text = get_greeting_response(user_message)
        requires_login = False
        show_features = False

    elif intent == GOODBYE:
        response_text = get_goodbye_response(user_message)
        requires_login = False
        show_features = False

    elif intent == GENERAL_INFO:
        try:
            response_text = await generate_general_response(user_message)
        except Exception as e:
            print(f"❌ Response Error: {e}")
            response_text = AGRICHECK_FEATURES.strip()
        requires_login = False
        show_features = True

    elif intent == DETAIL_REQUIRED:
        response_text = LOGIN_REQUIRED_MESSAGE
        requires_login = True
        show_features = False

    else:  # OFF_TOPIC
        response_text = OFF_TOPIC_MESSAGE
        requires_login = False
        show_features = False

    return {
        "response": response_text,
        "intent": intent,
        "requires_login": requires_login,
        "show_features": show_features,
        "agricheck_features": AGRICHECK_FEATURES.strip() if show_features else None
    }