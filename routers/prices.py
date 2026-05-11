from fastapi import APIRouter, HTTPException
from services.price_fetcher import fetch_all_prices
from services.mcx_service import fetch_mcx_prices
from models.price_models import AllPricesResponse

router = APIRouter(prefix="/api/prices", tags=["Market Data"])

@router.get("/", response_model=AllPricesResponse)
async def get_live_prices():
    """Returns combined live data from Global (yFinance) and Indian (MCX) markets."""
    try:
        global_data = await fetch_all_prices()
        mcx_data = await fetch_mcx_prices()
        
        # Merge dictionaries
        combined = {**global_data, **mcx_data}
        return {"status": "success", "data": combined}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
