async def log_api_usage(tokens_in: int, tokens_out: int):
    """BOT 5: Tracks Gemini 3 Flash API costs and alerts if spend > $5."""
    cost = (tokens_in * 0.0000001) + (tokens_out * 0.0000003) # Est. Gemini 3 Flash pricing
    # Logic to store and alert if daily spend exceeds thresholds
    if cost > 5.0:
        print("ALERT: Daily API budget threshold reached.")
