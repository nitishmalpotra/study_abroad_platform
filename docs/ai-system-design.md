# AI system design

## Provider model

Live AI calls use DeepSeek through `packages/ai_runtime`. The frontend never receives or stores the DeepSeek key.

Backend-only environment:

```dotenv
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-v4-flash
# DEEPSEEK_MODELS=deepseek-chat,deepseek-reasoner
# DEEPSEEK_BASE_URL=https://api.deepseek.com
```

`DEEPSEEK_MODELS` is an optional comma-separated fallback order. If set, it overrides the single `DEEPSEEK_MODEL` value.

## Shared runtime responsibilities

`packages/ai_runtime` owns concerns that should not be duplicated in task services:

- provider settings
- DeepSeek HTTP calls
- retries and backoff
- timeout configuration
- response normalization
- JSON parsing helpers
- secret redaction for errors and logs

## Task services

SOP Review and Admissions Prediction remain separate domain services because they have different schemas, prompts, validation rules, and evaluation needs.

SOP Review:

- validates applicant profile fields and SOP text bounds
- applies a local word-count gate before model grading
- uses a validity check and grading pass
- returns gatekeeper status plus a structured grade
- grades Academic Fit, University Specificity, Career Clarity, Narrative Flow, and Language & Tone

Admissions Prediction:

- validates academic profile fields and test-score ranges
- predicts one to five target programs
- returns chance categories, probabilities, reasoning, strengths, weaknesses, roadmap items, and recommended universities
- includes structured parsing and repair behavior in the service layer

## API integration

FastAPI exposes both live and deterministic mock endpoints:

- `POST /api/v1/sop/review`
- `POST /api/v1/sop/review/mock`
- `POST /api/v1/admissions/predict`
- `POST /api/v1/admissions/predict/mock`

Live endpoints call DeepSeek through the shared runtime and are backend-rate-limited. Mock endpoints validate request shape, return deterministic contract-compliant payloads, do not instantiate live providers, and are excluded from live quotas.

## Prompt assets

Prompt code is versioned in each service:

- `services/sop_review/sop_review/prompts/v1.py`
- `services/sop_review/sop_review/prompts/v2.py`
- `services/admissions/admissions/prompts/v1.py`
- `services/admissions/admissions/prompts/v2.py`

The active prompt version is imported through each service's prompt package. Historical prompt files are retained for migration context and regression comparison.

## Guardrails

- Validate structured outputs with Pydantic instead of trusting raw model text.
- Keep provider-specific code out of core orchestration.
- Keep mock/demo mode explicit in UI and API paths.
- Enforce live AI cost controls on the backend, not through frontend state.
- Redact secrets before surfacing provider failures.
- Do not commit raw user submissions, real provider logs, or API keys.

## Current limitations

- Live quality is covered by synthetic regression fixtures, not a large human-labeled evaluation set.
- There is no multi-provider failover beyond DeepSeek model fallback configuration.
- There is no streaming response support.
- Human review workflows and admin moderation are not implemented.
