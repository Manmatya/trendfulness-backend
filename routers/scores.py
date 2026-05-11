from fastapi import APIRouter
from services.scoring_engine import calculate_commodity_scores

router = APIRouter(prefix="/api/scores", tags=["Scoring Engine"])

@router.get("/{commodity}")
async def get_commodity_scores(commodity: str):
    """Returns raw numerical scores for Short, Mid, and Long timeframes."""
    # Logic pulled from scoring_engine.py
    data = {"dummy_all_data": {}} # Context from fetchers
    results = await calculate_commodity_scores(commodity, data)
    return results
