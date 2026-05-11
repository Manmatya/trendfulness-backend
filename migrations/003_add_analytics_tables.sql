-- TRENDFULNESS ANALYTICS & MARKET INTELLIGENCE
-- Version: 1.0.2
-- Purpose: Advanced data storage for inter-commodity ratios and volume surges.

-- 1. Commodity Ratios (For BOT 9: Ratio Monitor)
-- Stores Gold-Silver, Gold-Oil, etc. for mean reversion analysis.
CREATE TABLE IF NOT EXISTS market_ratios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pair_name TEXT NOT NULL, -- e.g., 'GOLD_SILVER'
    current_ratio NUMERIC(12, 4) NOT NULL,
    z_score NUMERIC(6, 2), -- Measures how far from the 100-day mean
    percentile_rank NUMERIC(5, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Volume & Liquidity Anomalies (For BOT 10: Volume Detector)
CREATE TABLE IF NOT EXISTS volume_anomalies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT REFERENCES commodities(symbol),
    surge_multiplier NUMERIC(6, 2), -- e.g., 2.5x normal volume
    timeframe_detected TEXT, -- '15m', '1h', '4h'
    is_pre_cot_surge BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Daily Aggregated Metrics
-- This stores the "Final Answer" for the day so the dashboard loads instantly.
CREATE TABLE IF NOT EXISTS daily_market_summary (
    summary_date DATE PRIMARY KEY,
    overall_sentiment TEXT, -- 'BULLISH', 'BEARISH', 'SIDEWAYS'
    top_performer_symbol TEXT,
    bottom_performer_symbol TEXT,
    avg_score_precious_metals NUMERIC(5, 2),
    avg_score_energy NUMERIC(5, 2),
    metadata JSONB -- Stores miscellaneous macro notes
);

-- 4. User Interaction Deep-Dive (For BOT 12)
-- Tracks which "Trendfulness" cards are flipped or shared.
CREATE TABLE IF NOT EXISTS engagement_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT,
    commodity_viewed TEXT,
    action_type TEXT, -- 'FLIP_CARD', 'SHARE_NARRATIVE', 'SWITCH_TIMEFRAME'
    is_mobile BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Indexes for fast dashboard loading
CREATE INDEX IF NOT EXISTS idx_ratios_pair ON market_ratios(pair_name);
CREATE INDEX IF NOT EXISTS idx_anomalies_symbol ON volume_anomalies(symbol);
CREATE INDEX IF NOT EXISTS idx_engagement_commodity ON engagement_metrics(commodity_viewed);

-- 6. Trigger to clean up old analytics (Retention Policy: 90 Days)
-- Keeps the database lean for the 10,000+ user scale.
CREATE OR REPLACE FUNCTION delete_old_analytics() RETURNS trigger AS $$
BEGIN
    DELETE FROM market_ratios WHERE created_at < NOW() - INTERVAL '90 days';
    DELETE FROM volume_anomalies WHERE created_at < NOW() - INTERVAL '90 days';
    DELETE FROM engagement_metrics WHERE created_at < NOW() - INTERVAL '90 days';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_cleanup_analytics
AFTER INSERT ON daily_market_summary
EXECUTE FUNCTION delete_old_analytics();
