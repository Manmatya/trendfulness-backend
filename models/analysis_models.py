from pydantic import BaseModel
from typing import List, Dict

class NarrativeContent(BaseModel):
    en: str
    hi: str

class AnalysisResponse(BaseModel):
    commodity: str
    timeframe: str
    score: float
    signal: str
    conviction: float
    headline: NarrativeContent
    direction_statement: NarrativeContent
    macro_drivers: List[Dict[str, str]]
    intelligence: NarrativeContent
