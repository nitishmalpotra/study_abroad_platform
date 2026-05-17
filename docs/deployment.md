# Deployment

## Current deployment reality

No single production deployment path is implemented in this monorepo yet.

Today:

- the frontend can be built as a Vite static app
- each Python tool can be run independently as a Streamlit app
- the SOP service includes a Dockerfile
- the repo does not yet include the planned FastAPI backend, production database layer, or unified deploy pipeline

## Current build commands

```bash
cd apps/web && npm run build
cd services/sop_review && docker build -t sop-review-grader .
cd services/admissions && uv build
```

## Planned deployment direction

Per `docs/MIGRATION_BLUEPRINT.md`, the target architecture is expected to move toward:

- frontend deployment for the future Next.js app
- FastAPI deployment for the public backend
- Neon Postgres for production relational storage
- Vercel Blob for persisted SOP uploads
- environment-specific configuration and CI-backed release checks

These are migration targets, not current capabilities.
