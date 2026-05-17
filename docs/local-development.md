# Local development

## Prerequisites

- Node.js compatible with the existing Vite app
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

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

The SOP page in the frontend is currently mock-only. A unified demo mode across both tools is planned but not implemented yet.

## SOP review service

```bash
cd services/sop_review
cp .env.example .env
uv sync --locked
uv run streamlit run app.py
```

This service currently requires a Gemini key via `GOOGLE_API_KEY`.

## Admissions service

```bash
cd services/admissions
cp .env.example .env
uv sync --locked
uv run streamlit run app.py
```

This service currently requires a Gemini key via `GOOGLE_API_KEY`.

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
uv run python -m py_compile app.py

# SOP review service
cd services/sop_review
uv run python -m py_compile app.py
```

Automated repo-wide tests are not yet in place. The migration blueprint calls for frontend, backend, and integration coverage later in the migration.
