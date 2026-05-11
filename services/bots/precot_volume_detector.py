from services.price_fetcher import get_historical_ohlcv

async def run():
    """
    BOT 10: Pre-COT Volume Surge Detector.
    Identifies abnormal volume on Fridays before COT report release.
    """
    commodities = ["GC=F", "SI=F", "CL=F"]
    for symbol in commodities:
        df = await get_historical_ohlcv(symbol, interval="3hr", bars=5)
        if df is not None:
            avg_vol = df['Volume'].mean()
            last_vol = df['Volume'].iloc[-1]
            
            if last_vol > (avg_vol * 1.5):
                print(f"ALERT: Volume surge detected in {symbol} ahead of COT.")
