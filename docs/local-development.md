# Local development

## Prerequisites

- Node.js compatible with the Next.js frontend
- Python 3.11 for the SOP review service
- Python 3.10-3.12 for the admissions service
- `uv` for Python dependency management

## Frontend

```bash
cd apps/web
cp .env.example .env
npm ci
npm run dev
```

Required frontend environment values:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

The SOP review and Admit Predictor pages support both live and demo mode. Demo
mode calls mock API endpoints and does not incur model cost.

## SOP review service

```bash
cd services/sop_review
cp .env.example .env
uv sync --locked
uv run streamlit run app.py
```

This service currently requires a DeepSeek key via `DEEPSEEK_API_KEY`.

## Admissions service

```bash
cd services/admissions
cp .env.example .env
uv sync --locked
uv run streamlit run app.py
```

This service currently requires a DeepSeek key via `DEEPSEEK_API_KEY`.

## API

```bash
cd apps/api
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

Generated docs are available at `/docs`; the OpenAPI schema is available at `/openapi.json`.
Live endpoints require `DEEPSEEK_API_KEY`; mock endpoints do not call DeepSeek.

Local API persistence is optional. By default, `apps/api/.env.example` keeps
`API_PERSISTENCE_ENABLED=false` and `API_RATE_LIMIT_STORE=memory`, so contributors
do not need a local database for normal frontend/API work.

The API enforces JSON-only requests, a default 64 KB request-body limit, shared
contract validation, and live-only rate limiting. Configure these with
`API_MAX_REQUEST_BODY_BYTES`, `API_LIVE_RATE_LIMIT_COUNT`, and
`API_LIVE_RATE_LIMIT_WINDOW_SECONDS`.

To test against Postgres locally, create a local Postgres database or Neon
development branch, set `DATABASE_URL`, then run:

```bash
cd apps/api
uv run python -m app.persistence.migrations
```

Use a Neon-style URL with `sslmode=require` for hosted development databases.
Do not commit `.env` files or local database artifacts.

## Quality commands

```bash
# Frontend
cd apps/web
npm run lint
npm run typecheck
npm run build

# Admissions service
cd services/admissions
uv run ruff check app.py
uv run pytest
uv run python -m py_compile app.py

# SOP review service
cd services/sop_review
uv run python -m unittest discover -s tests
uv run python -m py_compile app.py

# API
cd apps/api
uv run pytest
uv run ruff check .
uv run mypy app
```

Automated tests now exist for both Python tools, the API, shared contracts, and frontend build/type/lint checks. Integration coverage is still planned later in the migration.
