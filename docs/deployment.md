# Deployment

## Current deployment reality

The repo does not yet include a unified production deployment pipeline.

Deployable units today:

- `apps/web`: Next.js app that can be built with `npm run build`.
- `apps/api`: FastAPI app that can run under Uvicorn or another ASGI server.
- `services/sop_review`: standalone Streamlit app with a Dockerfile.
- `services/admissions`: standalone Streamlit app package.

For the public platform, treat `apps/web` and `apps/api` as the primary deployment units. The Streamlit apps are temporary standalone adapters for local or internal use during migration.

## Build and smoke commands

```bash
cd apps/web
npm ci
npm run build

cd ../api
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

cd ../../services/sop_review
docker build -t sop-review-grader .
```

Run API migrations before routing production traffic:

```bash
cd apps/api
uv run python -m app.persistence.migrations
```

## Web deployment

Deploy `apps/web` as a Next.js app.

Required browser-safe values:

```dotenv
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
NEXT_PUBLIC_STUDY_ABROAD_API_URL=https://your-api-origin.example
```

Do not expose DeepSeek or database credentials to the web app.

## API deployment

Deploy `apps/api` as an ASGI service.

Required production values:

```dotenv
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-v4-flash
DATABASE_URL=your_neon_postgres_connection_string_with_sslmode_require
API_PERSISTENCE_ENABLED=true
API_RATE_LIMIT_STORE=postgres
API_RATE_LIMIT_HASH_SALT=replace_with_high_entropy_secret
API_CORS_ORIGINS=https://your-web-origin.example
API_LIVE_RATE_LIMIT_COUNT=6
API_LIVE_RATE_LIMIT_WINDOW_SECONDS=3600
API_MAX_REQUEST_BODY_BYTES=64000
API_TRUST_PROXY_HEADERS=false
```

Set `API_TRUST_PROXY_HEADERS=true` only behind a trusted reverse proxy that strips untrusted forwarding headers. The default avoids trusting spoofable public `x-forwarded-for` values.

## Database

Neon Postgres is the production relational target for API persistence.

The API persistence layer stores:

- summarized SOP review records
- summarized admissions prediction records
- salted hash rate-limit buckets

It does not store raw SOP text, uploaded files, phone numbers, full names, raw provider output, or raw client IP addresses.

Use `API_RATE_LIMIT_STORE=postgres` for production. The in-memory limiter is process-local and suitable only for local development or single-process smoke tests.

## SOP uploads and blob storage

The public API currently accepts pasted SOP text only. It processes text transiently and does not persist original SOP uploads. Vercel Blob or another object store is not required for the current public API.

If product requirements later require retaining uploaded files, store file bytes in object storage, keep only references and minimal metadata in Postgres, add scanning/validation, and define deletion rules before launch.

## Operational gaps

- No unified deploy workflow is committed.
- API, contract, and shared runtime checks are not yet in GitHub Actions CI.
- Retention deletion jobs are not implemented.
- Backup/restore procedures are not documented.
- Centralized observability and alerting are not implemented.
- Stronger bot mitigation such as CAPTCHA, WAF, or queueing is not implemented.
