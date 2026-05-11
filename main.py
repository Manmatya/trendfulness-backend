import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

from routers import prices, scores, analysis, feedback, analytics
from services.bots import (
    data_health_monitor, uptime_monitor, ratio_monitor, 
    weekly_analytics, signal_quality_tracker, feedback_classifier,
    precot_volume_detector, news_impact
)

scheduler = AsyncIOScheduler()

def start_bots():
    """Initializes the 13-bot monitoring suite."""
    scheduler.add_job(data_health_monitor.run, 'interval', minutes=60)
    scheduler.add_job(uptime_monitor.run, 'interval', minutes=5)
    scheduler.add_job(ratio_monitor.run, 'interval', minutes=30)
    scheduler.add_job(precot_volume_detector.run, 'cron', day_of_week='fri')
    scheduler.add_job(feedback_classifier.run, 'cron', day_of_week='sun', hour=9)
    scheduler.add_job(news_impact.run, 'cron', hour=6)
    scheduler.add_job(weekly_analytics.run, 'cron', day_of_week='sun', hour=9)
    scheduler.add_job(signal_quality_tracker.run, 'cron', day_of_week='mon', hour=7)
    scheduler.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_bots()
    yield
    scheduler.shutdown()

app = FastAPI(title="Trendfulness Backend (Gemini 3 Powered)", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prices.router)
app.include_router(scores.router)
app.include_router(analysis.router)
app.include_router(feedback.router)
app.include_router(analytics.router)

@app.get("/health")
async def health():
    return {"status": "online", "engine": "Gemini 3"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
