# Deployment

## Current deployment reality

No single production deployment path is implemented in this monorepo yet.

Today:

- the frontend can be built as a Next.js app
- each Python tool can be run independently as a Streamlit app
- the FastAPI backend can be run independently
- the SOP service includes a Dockerfile
- the FastAPI backend includes the first production persistence layer and migrations
- the FastAPI backend includes public request guards, structured safe errors,
  CORS configuration, live-only rate limiting, and deterministic mock endpoints
- the repo does not yet include a unified deploy pipeline

## Current build commands

```bash
cd apps/web && npm run build
cd services/sop_review && docker build -t sop-review-grader .
cd services/admissions && uv build
```

## Planned deployment direction

Per `docs/MIGRATION_BLUEPRINT.md`, the target architecture is expected to move toward:

- frontend deployment for the Next.js app
- production FastAPI deployment for the public backend
- environment-specific configuration and CI-backed release checks

## Production database

Neon Postgres is the production relational database target for the FastAPI API.
Apply migrations before routing production traffic:

```bash
cd apps/api
uv run python -m app.persistence.migrations
```

Required production API values:

- `DATABASE_URL`: Neon pooled connection string with SSL, for example `?sslmode=require`
- `API_PERSISTENCE_ENABLED=true`
- `API_RATE_LIMIT_STORE=postgres`
- `API_RATE_LIMIT_HASH_SALT`: high-entropy secret used to hash anonymous rate-limit identifiers
- `DEEPSEEK_API_KEY`: backend-only model provider key
- `API_CORS_ORIGINS`: comma-separated production frontend origins
- `API_MAX_REQUEST_BODY_BYTES`: maximum accepted JSON request body size
- `API_TRUST_PROXY_HEADERS=false` by default; set true only behind a trusted
  reverse proxy that strips untrusted `x-forwarded-for` headers

The persistence layer stores summarized SOP review submissions, summarized
admissions prediction records, and hashed rate-limit buckets. It does not store
raw SOP text, uploaded files, phone numbers, or raw client IP addresses.

Use `API_RATE_LIMIT_STORE=postgres` for production. The in-memory limiter is
process-local and exists for development or single-process smoke tests only.

## SOP uploads and blob storage

First-release API persistence assumes SOP text is processed transiently and then
discarded after the response is generated. Original SOP uploads are not persisted,
so Vercel Blob is not required yet.

If product requirements later require retaining original uploaded files, store
the file in Vercel Blob and store only blob references plus minimal metadata in
Postgres. Do not store file bytes in Postgres.

Environment promotion, automated retention jobs, and the unified release pipeline
remain migration targets.
