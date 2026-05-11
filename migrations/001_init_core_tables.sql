-- TRENDFULNESS CORE INITIALIZATION
-- Version: 1.0.0
-- Purpose: Setup fundamental tables for price storage and scoring logic.

-- 1. Create Commodity Metadata (Master Table)
CREATE TABLE IF NOT EXISTS commodities (
    symbol TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    asset_class TEXT NOT NULL, -- 'PRECIOUS_METALS', 'ENERGY', 'INDICES'
    currency TEXT DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Seed Commodities
INSERT INTO commodities (symbol, display_name, asset_class) VALUES
('GC=F', 'Gold', 'PRECIOUS_METALS'),
('SI=F', 'Silver', 'PRECIOUS_METALS'),
('CL=F', 'Crude Oil', 'ENERGY'),
('NG=F', 'Natural Gas', 'ENERGY'),
('GOLDM.MCX', 'Gold Mini MCX', 'PRECIOUS_METALS'),
('SILVERM.MCX', 'Silver Mini MCX', 'PRECIOUS_METALS'),
('CRUDEOIL.MCX', 'Crude Oil MCX', 'PRECIOUS_METALS')
ON CONFLICT (symbol) DO NOTHING;

-- 3. Live Price Snapshot (For BOT 1 & Frontend quick access)
CREATE TABLE IF NOT EXISTS live_prices (
    symbol TEXT PRIMARY KEY REFERENCES commodities(symbol),
    price NUMERIC(18, 4) NOT NULL,
    change_pct NUMERIC(8, 2),
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Multi-Timeframe Scoring Engine Results
-- Stores the output of services/scoring_engine.py
CREATE TABLE IF NOT EXISTS commodity_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT REFERENCES commodities(symbol),
    timeframe TEXT NOT NULL, -- 'SHORT', 'MID', 'LONG'
    total_score NUMERIC(5, 2) NOT NULL, -- 0-100
    technical_score NUMERIC(5, 2),
    macro_score NUMERIC(5, 2),
    regime_score NUMERIC(5, 2),
    signal_type TEXT NOT NULL, -- 'BULLISH', 'BEARISH', 'NEUTRAL'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. System Config (For BOT 5: Cost & Token Manager)
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO system_config (key, value, description) VALUES
('token_budget', '{"monthly_limit": 50.00, "current_spend": 0.00}', 'Gemini API Monthly Spend Tracking')
ON CONFLICT (key) DO NOTHING;

-- 6. Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_scores_symbol_timeframe ON commodity_scores(symbol, timeframe);
CREATE INDEX IF NOT EXISTS idx_prices_updated ON live_prices(last_updated);
