from pydantic import BaseModel, EmailStr
from typing import Optional

class UserProfile(BaseModel):
    id: str
    display_name: Optional[str]
    preferred_language: str = "en"
    is_admin: bool = False

class FeedbackSubmit(BaseModel):
    commodity: str
    timeframe: str
    vote: str # 'like' or 'dislike'
    comment: Optional[str]
