CREATE TABLE IF NOT EXISTS tool_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    tool_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    target_country TEXT NOT NULL,
    target_intake TEXT NOT NULL DEFAULT '',
    target_college TEXT NOT NULL DEFAULT '',
    target_course TEXT NOT NULL DEFAULT '',
    journey_stage TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tool_leads_created_at
ON tool_leads (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_tool_leads_tool_name
ON tool_leads (tool_name);
