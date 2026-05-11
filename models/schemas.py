from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .price_models import TickerDetail, AllPricesResponse
from .analysis_models import AnalysisResponse, NarrativeContent
from .user_models import UserProfile, FeedbackSubmit

# --- Combined & Utility Schemas ---

class MarketState(BaseModel):
    """
    Schema for the global market state used by the Regime Service.
    """
    regime_label: str = Field(..., example="Risk-On")
    description: str
    volatility_index: float
    top_driver: str
    last_updated: str

class BotStatus(BaseModel):
    """
    Schema for individual bot heartbeats.
    """
    bot_name: str
    last_run: str
    status: str # 'HEALTHY', 'DEGRADED', 'FAILING'
    last_action: str

class SystemOverview(BaseModel):
    """
    The high-level schema for the Admin Dashboard.
    """
    api_version: str
    uptime_pct: float
    active_users_24h: int
    bot_states: List[BotStatus]
    data_health: Dict[str, str]

class ErrorResponse(BaseModel):
    """
    Standardized error format for the Frontend.
    """
    error_code: str
    message: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None

# Re-exporting for easy access across the app
__all__ = [
    "TickerDetail", 
    "AllPricesResponse", 
    "AnalysisResponse", 
    "NarrativeContent", 
    "UserProfile", 
    "FeedbackSubmit",
    "MarketState",
    "BotStatus",
    "SystemOverview",
    "ErrorResponse"
]
