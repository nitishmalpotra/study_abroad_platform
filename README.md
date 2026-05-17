# Study Abroad Platform

Study Abroad Platform is a public monorepo in transition. It currently contains a KlassFin-themed Vite frontend, a Streamlit SOP review tool, and a Streamlit admissions predictor. The approved migration target is a cleaner monorepo with a shared backend, a shared AI runtime, reusable task-specific domain modules, and public-repo-grade operations; that work is still in progress.

## Current layout

- `apps/web` — Vite + React frontend with static marketing pages, Supabase-backed lead capture, and a mock-only SOP page
- `apps/api` — FastAPI backend exposing health, live SOP/admissions endpoints, and deterministic mock endpoints
- `services/sop_review` — DeepSeek-backed Streamlit SOP review tool with local SQLite persistence
- `services/admissions` — DeepSeek-backed Streamlit admissions predictor with local SQLite persistence
- `docs` — architecture, development, deployment, security, and migration documentation

## Architecture

The current architecture is documented in `docs/architecture.md`. The migration target is defined in `docs/MIGRATION_BLUEPRINT.md`.

## Run locally

See `docs/local-development.md` for setup and commands for each app.

## AI provider status

- Current services require a bring-your-own DeepSeek API key via `DEEPSEEK_API_KEY`.
- Bring-your-own DeepSeek API key support is planned in the migration blueprint but is not implemented yet.
- Mock/demo endpoints now exist in `apps/api`; the frontend still has only its older hard-coded SOP demo flow.

## Deployment overview

See `docs/deployment.md`. A unified production deployment path is not implemented yet.

## Security and privacy

See `SECURITY.md` and `docs/security-and-privacy.md`.

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

Automated tests now exist for both Python services and the API. Frontend, contract-generation, and end-to-end coverage are still planned later in the migration.
