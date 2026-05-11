from fastapi import APIRouter, Depends
from models.user_models import FeedbackSubmit
from database.supabase_client import supabase

router = APIRouter(prefix="/api/feedback", tags=["User Interaction"])

@router.post("/submit")
async def post_feedback(feedback: FeedbackSubmit):
    """Saves user feedback to Supabase; later processed by BOT 13."""
    data = {
        "commodity": feedback.commodity,
        "timeframe": feedback.timeframe,
        "vote": feedback.vote,
        "comment": feedback.comment
    }
    result = supabase.table("feedback").insert(data).execute()
    return {"status": "success", "id": result.data[0]["id"]}
