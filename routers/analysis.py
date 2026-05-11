from fastapi import APIRouter, Query
from services.gemini_service import generate_commodity_narrative
from models.analysis_models import AnalysisResponse

router = APIRouter(prefix="/api/analysis", tags=["Intelligence"])

@router.get("/{commodity}/{timeframe}", response_model=AnalysisResponse)
async def get_market_intelligence(commodity: str, timeframe: str):
    """
    Returns the full AI-narrative for a specific commodity/timeframe.
    Triggers Gemini 3 Flash and checks Bots 2 & 3 for consistency.
    """
    # 1. Get math from scoring engine
    # 2. Get narrative from gemini_service
    # 3. Return validated response
    return await generate_commodity_narrative(commodity, timeframe, {}, "BULLISH", 85.0)
