import json
import re
from typing import Dict, Any, List
from services.gemini_service import model

class GeminiValidator:
    """
    BOT 2: Content & Format Validator.
    Ensures Gemini 3 Flash output follows strict formatting and jargon-free rules.
    """
    
    FORBIDDEN_JARGON = ["CVD", "POC", "BACKWARDATION", "CONTANGO", "ORDER FLOW", "DELTA"]
    REQUIRED_KEYS = ["direction_statement", "headline", "macro_drivers", "intelligence"]

    @classmethod
    async def validate_output(cls, commodity: str, raw_json: Dict[str, Any]) -> bool:
        """
        Main validation pipeline.
        Returns True if the content is safe and properly formatted for Trendfulness.
        """
        # 1. Structural Validation
        if not all(key in raw_json for key in cls.REQUIRED_KEYS):
            print(f"BOT 2 Error: Missing keys in {commodity} narrative.")
            return False

        # 2. Jargon Check (Multi-language)
        # Flatten all text into one string for easier searching
        content_string = json.dumps(raw_json).upper()
        for word in cls.FORBIDDEN_JARGON:
            if word in content_string:
                print(f"BOT 2 Error: Forbidden jargon '{word}' found in {commodity} output.")
                return False

        # 3. Compliance Check (Financial Advice)
        # We ensure Gemini didn't add "This is not financial advice" 
        # because the app handles its own global legal disclaimers.
        legal_keywords = ["FINANCIAL ADVICE", "BUY NOW", "INVEST AT YOUR OWN RISK"]
        if any(kw in content_string for kw in legal_keywords):
            print(f"BOT 2 Error: AI attempted to provide explicit financial advice/disclaimers.")
            return False

        # 4. Translation Completeness
        # Check if both 'en' and 'hi' (Hindi) exist for direction_statement
        ds = raw_json.get("direction_statement", {})
        if "en" not in ds or "hi" not in ds:
            print(f"BOT 2 Error: Translation missing for {commodity}.")
            return False

        return True

    @classmethod
    async def fix_with_ai(cls, original_output: Dict[str, Any], error_reason: str) -> Dict[str, Any]:
        """
        If validation fails, we send it back to Gemini 3 Flash one time to 'fix' its mistake.
        """
        fix_prompt = f"""
        The previous JSON output failed validation for: {error_reason}.
        Original JSON: {json.dumps(original_output)}
        
        Task: 
        - Remove all technical jargon (CVD, POC, etc.)
        - Ensure both English (en) and Hindi (hi) translations are present.
        - Do not include financial advice disclaimers.
        - Return ONLY valid JSON.
        """
        try:
            response = await model.generate_content_async(fix_prompt)
            return json.loads(response.text)
        except Exception as e:
            print(f"BOT 2 critical failure during AI fix: {e}")
            return {}

async def run():
    """Bot interface for the scheduler."""
    print("BOT 2: Gemini Validator online. Monitoring AI narrative quality...")
