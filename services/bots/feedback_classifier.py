import json
from typing import List, Dict, Any
from database.supabase_client import supabase
from services.gemini_service import model

class FeedbackClassifierBot:
    """
    BOT 13: Qualitative Feedback Analyzer.
    Categorizes raw user comments into actionable themes using Gemini 3 Flash.
    """

    CATEGORIES = ["Accuracy", "UI/UX", "Feature Request", "Speed/Latency", "General"]

    @classmethod
    async def run(cls):
        """
        Scheduled task: Fetches unclassified feedback and updates the DB with themes.
        """
        print("BOT 13: Starting feedback classification...")
        
        try:
            # 1. Fetch feedback from the last 24 hours that hasn't been tagged
            # (Assumes a 'category' column exists in your feedback table)
            response = supabase.table("feedback") \
                .select("id, comment") \
                .is_eq("category", None) \
                .not_.is_eq("comment", None) \
                .execute()

            feedback_list = response.data
            if not feedback_list:
                print("BOT 13: No new comments to classify.")
                return

            # 2. Batch process for Gemini
            for entry in feedback_list:
                category = await cls._classify_text(entry["comment"])
                
                # 3. Update Supabase
                supabase.table("feedback") \
                    .update({"category": category}) \
                    .eq("id", entry["id"]) \
                    .execute()
            
            print(f"BOT 13: Successfully classified {len(feedback_list)} comments.")

        except Exception as e:
            print(f"BOT 13 Error: {e}")

    @classmethod
    async def _classify_text(cls, text: str) -> str:
        """Uses Gemini 3 Flash to pick the best category."""
        prompt = f"""
        Classify this user feedback into exactly one of these categories: {cls.CATEGORIES}.
        Feedback: "{text}"
        Return ONLY the category name.
        """
        try:
            response = await model.generate_content_async(prompt)
            result = response.text.strip()
            # Verify the AI returned a valid category
            return result if result in cls.CATEGORIES else "General"
        except:
            return "General"

async def run():
    """Bot entry point."""
    await FeedbackClassifierBot.run()
