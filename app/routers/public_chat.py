from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from ..services.public_agent import public_chat_agent

# ============================================
# PUBLIC CHAT ROUTER
# Dashboard LLM Button - No Auth Required
# ============================================

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Dashboard LLM Button"]
)


# ─── Request / Response Models ────────────────────────────────

class PublicChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="User's message or question",
        example="What services does AgriCheck provide?"
    )
    language: Optional[str] = Field(
        default="auto",
        description="Language preference: 'en', 'ur', or 'auto'",
        example="auto"
    )


class PublicChatResponse(BaseModel):
    response: str = Field(description="AI generated response")
    intent: str = Field(description="Classified intent: GENERAL_INFO or DETAIL_REQUIRED")
    requires_login: bool = Field(description="True if user needs to login for this query")
    show_features: bool = Field(description="True if feature list should be shown")
    agricheck_features: Optional[str] = Field(
        default=None,
        description="AgriCheck features list (only for general queries)"
    )
    endpoint_info: dict = Field(
        default_factory=dict,
        description="Info about private endpoint (after login)"
    )


# ─── Endpoint ─────────────────────────────────────────────────

@router.post(
    "/public",
    response_model=PublicChatResponse,
    summary="Dashboard LLM Button",
    description="""
## 🌱 AgriCheck Public AI Assistant

**No authentication required** - Public dashboard button.

### How it works:
- **General queries** → AI explains AgriCheck features & capabilities
- **Specific/detailed queries** → Prompts user to login/signup

### Intent Classification:
| Intent | Example Query | Response |
|--------|--------------|----------|
| `GENERAL_INFO` | "What services do you provide?" | Feature explanation |
| `DETAIL_REQUIRED` | "What is my soil's nitrogen level?" | Login required message |

### After Login (Private Endpoint):
Once authenticated with Firebase JWT token:
```
POST /api/v1/chat/private
Authorization: Bearer <firebase_jwt_token>
```
    """
)
async def dashboard_llm_button(request: PublicChatRequest):
    """
    Dashboard LLM Button - Public Chat Endpoint

    - No auth required
    - No real sensor data returned
    - Encourages signup for detailed analysis
    """

    try:
        # Call Public Agent
        result = await public_chat_agent(request.message)

        # Add endpoint info for frontend
        result["endpoint_info"] = {
            "public_endpoint": "POST /api/v1/chat/public",
            "private_endpoint": "POST /api/v1/chat/private",
            "auth_required_for_private": True,
            "auth_type": "Firebase JWT Token",
            "how_to_get_token": "Login/Signup at AgriCheck → Get JWT → Use in Authorization header",
            "private_features": [
                "Real-time sensor data analysis",
                "Historical trends",
                "Personalized crop recommendations",
                "Custom fertilizer calculations",
                "Voice AI advisor"
            ]
        }

        return PublicChatResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )


# ─── Health Check ──────────────────────────────────────────────

@router.get(
    "/public/health",
    summary="Dashboard LLM Button Health Check",
    tags=["Dashboard LLM Button"]
)
async def public_chat_health():
    """Check if public chat service is running"""
    return {
        "status": "✅ Online",
        "endpoint": "Dashboard LLM Button",
        "auth_required": False,
        "available_intents": ["GENERAL_INFO", "DETAIL_REQUIRED"],
        "supported_languages": ["English", "Urdu", "Auto-detect"]
    }