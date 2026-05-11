import json
from typing import Dict, Any
from services.gemini_service import model
from cache.redis_client import cache_get

class SignalConsistencyBot:
    """
    BOT 3: Validates AI-generated narratives against raw numerical scores.
    Ensures the 'Tone' matches the 'Math'.
    """

    @staticmethod
    async def validate(commodity: str, timeframe: str, score: float, narrative_json: Dict[str, Any]) -> bool:
        """
        Compares the numerical score with the text sentiment.
        Returns True if consistent, False if a contradiction is detected.
        """
        
        # 1. Determine expected sentiment based on score
        # Using the thresholds defined in scoring_engine.py
        expected_sentiment = "NEUTRAL"
        if score > 60: expected_sentiment = "BULLISH"
        elif score < 40: expected_sentiment = "BEARISH"

        # 2. Extract direction from the narrative (Gemini output)
        # We look at the 'en' version of the direction_statement
        narrative_text = narrative_json.get("direction_statement", {}).get("en", "").upper()

        # 3. Perform basic check
        # If score says Bullish but text contains 'downside', 'fall', or 'bearish'
        contradiction = False
        if expected_sentiment == "BULLISH" and any(word in narrative_text for word in ["FALL", "BEARISH", "DROP", "DOWNSIDE"]):
            contradiction = True
        elif expected_sentiment == "BEARISH" and any(word in narrative_text for word in ["RISE", "BULLISH", "UPWARD", "GAINS"]):
            contradiction = True

        # 4. If basic check is ambiguous, use Gemini 3 Flash to audit itself
        if contradiction:
            audit_passed = await SignalConsistencyBot._ai_audit(expected_sentiment, narrative_text)
            return audit_passed

        return True

    @staticmethod
    async def _ai_audit(expected: str, text: str) -> bool:
        """Uses a quick Gemini 3 Flash call to verify if the text matches the sentiment."""
        prompt = f"""
        Audit Task: Compare the Sentiment to the Text.
        Expected Sentiment: {expected}
        Text to Audit: "{text}"
        
        Does the text logically support the {expected} sentiment? 
        Answer only with 'YES' or 'NO'.
        """
        try:
            response = await model.generate_content_async(prompt)
            return "YES" in response.text.upper()
        except:
            # If the auditor fails, we default to False to be safe
            return False

async def run():
    """Scheduled task to audit recent signals stored in cache/DB."""
    # This would typically loop through active commodities
    print("BOT 3: Signal Consistency Check initiated...")
    # Logic to fetch latest signals and validate them
