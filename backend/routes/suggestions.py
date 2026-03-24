from fastapi import APIRouter, HTTPException
from models.schemas import SuggestionInput, SuggestionResponse
from services.ai_service import get_ai_suggestions

router = APIRouter(prefix="/api", tags=["AI Suggestions"])


@router.post("/ai-suggestions", response_model=SuggestionResponse)
async def ai_suggestions(input: SuggestionInput):
    """Get AI-powered emission reduction suggestions."""
    try:
        result = await get_ai_suggestions(
            input.total_co2,
            input.electricity_kwh,
            input.fuel_litres,
            input.business_type or "MSME",
        )
        return SuggestionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
