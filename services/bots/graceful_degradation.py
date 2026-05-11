async def handle_failure(source_name: str):
    """BOT 4: Serves cached data if a source fails, attaching a warning."""
    # Triggered on failure
    return {
        "data": "last_cached_value",
        "warning": "Data may be delayed due to upstream provider issues."
    }
