CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sop_review_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    university TEXT NOT NULL,
    intake TEXT NOT NULL,
    country TEXT NOT NULL,
    sop_word_count INTEGER NOT NULL CHECK (sop_word_count >= 0),
    overall_score NUMERIC(4, 2) NOT NULL CHECK (
        overall_score >= 1
        AND overall_score <= 10
    ),
    grade_json JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sop_review_submissions_created_at
ON sop_review_submissions (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_sop_review_submissions_university
ON sop_review_submissions (university);

CREATE TABLE IF NOT EXISTS admissions_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    target_intake TEXT NOT NULL,
    target_country TEXT NOT NULL,
    profile_summary_json JSONB NOT NULL,
    target_programs_json JSONB NOT NULL,
    prediction_json JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_admissions_predictions_created_at
ON admissions_predictions (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_admissions_predictions_target_country
ON admissions_predictions (target_country);

CREATE TABLE IF NOT EXISTS rate_limit_buckets (
    scope TEXT NOT NULL,
    key_hash TEXT NOT NULL,
    window_start TIMESTAMPTZ NOT NULL,
    window_seconds INTEGER NOT NULL CHECK (window_seconds > 0),
    hit_count INTEGER NOT NULL DEFAULT 0 CHECK (hit_count >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (scope, key_hash, window_start)
);

CREATE INDEX IF NOT EXISTS idx_rate_limit_buckets_updated_at
ON rate_limit_buckets (updated_at DESC);
