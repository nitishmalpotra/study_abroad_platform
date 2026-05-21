# Local development

## Prerequisites

- Node.js 20
- Python 3.11
- `uv`
- DeepSeek API key for live AI calls
- Optional Supabase project for lead capture
- Optional Neon or local Postgres database for API persistence testing

There is no root workspace command yet. Run each app/package from its own directory.

## Environment files

Create local env files from the examples:

```bash
cp apps/web/.env.example apps/web/.env
cp apps/api/.env.example apps/api/.env
cp services/sop_review/.env.example services/sop_review/.env
cp services/admissions/.env.example services/admissions/.env
```

Do not commit `.env` files.

## Web app

```bash
cd apps/web
npm ci
npm run dev
```

The frontend runs at `http://localhost:3000`.

`apps/web/.env`:

```dotenv
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
NEXT_PUBLIC_STUDY_ABROAD_API_URL=http://localhost:8000
```

`NEXT_PUBLIC_STUDY_ABROAD_API_URL` points browser API calls at FastAPI. Do not put backend secrets in `apps/web/.env`; all `NEXT_PUBLIC_` values are visible in the browser.

Supabase values are required to unlock the lead-gated tool UI in the browser. The FastAPI endpoints can still be tested directly without Supabase.

## API

```bash
cd apps/api
uv sync
uv run uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

Generated docs are available at `http://localhost:8000/docs`; the OpenAPI schema is available at `http://localhost:8000/openapi.json`.

`apps/api/.env`:

```dotenv
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-v4-flash
# DEEPSEEK_MODELS=deepseek-chat,deepseek-reasoner
# DEEPSEEK_BASE_URL=https://api.deepseek.com

API_PERSISTENCE_ENABLED=false
API_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
API_LIVE_RATE_LIMIT_COUNT=6
API_LIVE_RATE_LIMIT_WINDOW_SECONDS=3600
API_MAX_REQUEST_BODY_BYTES=64000
API_TRUST_PROXY_HEADERS=false
API_RATE_LIMIT_STORE=memory
```

Live endpoints require `DEEPSEEK_API_KEY`. Mock endpoints do not call DeepSeek.

Local persistence is optional. To test with Postgres:

```bash
cd apps/api
# set DATABASE_URL and API_PERSISTENCE_ENABLED=true in apps/api/.env first
uv run python -m app.persistence.migrations
```

Use a Neon-style URL with `sslmode=require` for hosted development databases.

## SOP review Streamlit app

```bash
cd services/sop_review
uv sync --locked
uv run streamlit run app.py
```

Streamlit usually serves at `http://localhost:8501`.

This standalone app requires `DEEPSEEK_API_KEY` for real review and stores local SQLite data at `SOP_DB_PATH` from `services/sop_review/.env`.

## Admissions Streamlit app

```bash
cd services/admissions
uv sync --locked
uv run streamlit run app.py
```

Streamlit usually serves at `http://localhost:8501`.

This standalone app requires `DEEPSEEK_API_KEY` for real prediction and stores local SQLite data.

## Mock/demo development

Use the web app's demo buttons or call the mock endpoints directly:

```bash
POST http://localhost:8000/api/v1/sop/review/mock
POST http://localhost:8000/api/v1/admissions/predict/mock
```

Mock endpoints validate request shape, return deterministic responses, do not call DeepSeek, and are excluded from live AI quotas.

## Checks

```bash
cd apps/web
npm run test
npm run lint
npm run typecheck
npm run build

cd ../api
uv run pytest
uv run ruff check .
uv run mypy app

cd ../../packages/contracts
uv run pytest

cd ../ai_runtime
uv run pytest

cd ../../services/admissions
uv run ruff check app.py
uv run pytest
uv run python -m py_compile app.py

cd ../sop_review
uv run python -m unittest discover -s tests
uv run python -m py_compile app.py
```

No dedicated Markdown/documentation linter is configured.
