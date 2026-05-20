# Study Abroad Platform

Study Abroad Platform is a public monorepo in transition. It currently contains a KlassFin-themed Next.js frontend, a FastAPI backend, a Streamlit SOP review tool, and a Streamlit admissions predictor. The approved migration target is a cleaner monorepo with a shared backend, a shared AI runtime, reusable task-specific domain modules, and public-repo-grade operations; that work is still in progress.

## Current layout

- `apps/web` — Next.js frontend with static marketing pages, Supabase-backed lead capture, and API-backed live/mock SOP review plus Admit Predictor tools
- `apps/api` — FastAPI backend exposing health, live SOP/admissions endpoints, deterministic mock endpoints, and optional Neon-backed persistence
- `services/sop_review` — DeepSeek-backed Streamlit SOP review tool with local SQLite persistence
- `services/admissions` — DeepSeek-backed Streamlit admissions predictor with local SQLite persistence
- `docs` — architecture, development, deployment, security, and migration documentation

## Architecture

The current architecture is documented in `docs/architecture.md`. The migration target is defined in `docs/MIGRATION_BLUEPRINT.md`.

## Run locally

See `docs/local-development.md` for setup and commands for each app.

## AI provider status

- Current services and live API endpoints require a bring-your-own DeepSeek API key via `DEEPSEEK_API_KEY`.
- The SOP review and Admit Predictor frontend tools now call the FastAPI live and mock endpoints; the DeepSeek key remains server-side only.
- Mock API endpoints are separate from live endpoints and do not call DeepSeek.

## Deployment overview

See `docs/deployment.md`. The API now has Neon Postgres migrations and optional production persistence; a unified deployment pipeline is not implemented yet.

## Security and privacy

See `SECURITY.md` and `docs/security-and-privacy.md`.

The public API is anonymous by design. Live AI endpoints enforce backend rate
limits, JSON/body-size guards, safe structured errors, restricted CORS, and
secret-redacted structured logging; mock endpoints remain usable without model
cost.

Public-repo hygiene is mandatory:

- no committed secrets
- no local databases
- no raw user documents
- no personal absolute paths
- no generated runtime logs

## Quality commands

```bash
# Frontend
cd apps/web
npm run test
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

Automated tests now exist for both Python services, the API, shared contracts, and frontend test/build/type/lint checks. End-to-end coverage is still planned later in the migration.
