from services.gemini_service import model
from cache.redis_client import cache_set
import json

async def run():
    """
    BOT 11: News Impact Scraper & Analyzer.
    Uses Gemini 3 Flash to scan news and adjust sentiment scores.
    """
    prompt = "Scan current top financial news for Gold, Oil, and Natural Gas. Return a JSON impact score (-5 to +5) for each."
    try:
        # Utilizing search grounding for real-time news
        response = await model.generate_content_async(prompt, tools=[{"google_search_retrieval": {}}])
        impact_data = response.text # Assuming JSON format from Gemini
        await cache_set("news_impact_scores", impact_data, 7200)
        print("BOT 11: News impact scores updated.")
    except Exception as e:
        print(f"BOT 11 Error: {e}")
