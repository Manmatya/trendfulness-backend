-- TRENDFULNESS BOT MONITORING & AUDIT LOGS
-- Version: 1.0.1
-- Purpose: Track bot heartbeats, API costs, and quality audits.

-- 1. Bot Heartbeats (For BOT 8: Uptime Monitor)
CREATE TABLE IF NOT EXISTS bot_heartbeats (
    bot_id TEXT PRIMARY KEY, -- e.g., 'BOT_01_HEALTH', 'BOT_05_COST'
    last_run TIMESTAMPTZ DEFAULT NOW(),
    status TEXT CHECK (status IN ('HEALTHY', 'DEGRADED', 'FAILED')),
    last_message TEXT,
    metadata JSONB -- Stores latency, specific errors, or task counts
);

-- 2. API Usage & Cost Tracking (For BOT 5: Cost Manager)
CREATE TABLE IF NOT EXISTS api_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name TEXT NOT NULL, -- 'GEMINI_3_FLASH', 'FRED', 'EIA'
    tokens_used INT DEFAULT 0,
    estimated_cost_usd NUMERIC(10, 6),
    endpoint_called TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. AI Quality Audits (For BOT 2 & 3: Validator/Consistency)
CREATE TABLE IF NOT EXISTS ai_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commodity TEXT,
    score_at_time NUMERIC,
    narrative_preview TEXT,
    validation_status BOOLEAN,
    fail_reason TEXT, -- e.g., 'Jargon detected', 'Sentiment mismatch'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. User Feedback Loops (For BOT 13: Feedback Classifier)
-- This extends the previous feedback table with classification columns
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid = 'feedback'::regclass AND attname = 'is_processed') THEN
        ALTER TABLE feedback ADD COLUMN is_processed BOOLEAN DEFAULT FALSE;
        ALTER TABLE feedback ADD COLUMN sentiment_score NUMERIC; -- -1 to 1
    END IF;
END $$;

-- 5. Seed Initial Bot States
INSERT INTO bot_heartbeats (bot_id, status, last_message) VALUES
('BOT_01_HEALTH', 'HEALTHY', 'System Initialized'),
('BOT_02_VALIDATOR', 'HEALTHY', 'System Initialized'),
('BOT_03_CONSISTENCY', 'HEALTHY', 'System Initialized'),
('BOT_04_DEGRADATION', 'HEALTHY', 'System Initialized'),
('BOT_05_COST', 'HEALTHY', 'System Initialized'),
('BOT_13_FEEDBACK', 'HEALTHY', 'System Initialized')
ON CONFLICT (bot_id) DO NOTHING;

-- 6. Indexes for Monitoring
CREATE INDEX IF NOT EXISTS idx_api_usage_service ON api_usage_logs(service_name);
CREATE INDEX IF NOT EXISTS idx_audit_commodity ON ai_audit_logs(commodity);
