import google.generativeai as genai
import os
import json
from typing import Dict, Any

# Initializing Gemini 3 Flash
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3-flash') # Updated to Gemini 3

async def generate_commodity_narrative(commodity: str, timeframe: str, scores: dict, signal: str, conviction: float):
    prompt = f"""
    Analyze {commodity} for the {timeframe} timeframe.
    Current Signal: {signal} (Conviction: {conviction}%).
    Factor Scores: {json.dumps(scores)}.
    
    Rules:
    - Use plain language. 
    - No jargon like CVD, POC, or Backwardation.
    - Explain 'what this means for the price'.
    - Provide a headline and key drivers.
    - Output in JSON format with 'en' and 'hi' keys.
    """
    
    try:
        # Gemini 3 Flash call with search grounding
        response = await model.generate_content_async(prompt, tools=[{"google_search_retrieval": {}}])
        return json.loads(response.text)
    except Exception as e:
        # BOT 4: Graceful Degradation logic would trigger here
        return {"error": "Intelligence unavailable", "details": str(e)}

async def generate_why_prices_moved():
    prompt = "Explain today's major price movements in Gold, Silver, and Oil using latest market news."
    response = await model.generate_content_async(prompt, tools=[{"google_search_retrieval": {}}])
    return response.text
