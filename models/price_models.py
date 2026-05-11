from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class TickerDetail(BaseModel):
    label: str
    price: float
    change_pct: Optional[float] = None
    currency: str = "USD"
    timestamp: str

class AllPricesResponse(BaseModel):
    status: str = "success"
    data: Dict[str, TickerDetail]
