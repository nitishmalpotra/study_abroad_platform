# Deployment

> New to Vercel? Follow the beginner-friendly, click-by-click walkthrough in
> [`vercel-deploy-step-by-step.md`](vercel-deploy-step-by-step.md). This page is
> the full technical reference.

Deploy the public platform as two Vercel projects from the same Git repository:

- `apps/web`: Next.js frontend.
- `apps/api`: FastAPI backend.

The internal Streamlit apps under `services/` are not public deployment targets.

## Vercel project setup

Create two separate Vercel projects that point at this monorepo.

### Web project

Use these Vercel settings:

```text
Root Directory: apps/web
Framework Preset: Next.js
Install Command: npm ci
Build Command: npm run build
Output Directory: .next
Development Command: npm run dev
```

Health/smoke URL:

```text
/
/tools/sop-review
/tools/admit-predictor
```

### API project

Use these Vercel settings:

```text
Root Directory: apps/api
Framework Preset: FastAPI (auto-detected)
Install Command: (leave default; Vercel installs from requirements.txt)
Build Command: (leave default; comes from pyproject.toml below)
```

Vercel discovers the ASGI app by looking for a `FastAPI` instance named `app` at a
supported entrypoint. The backend lives at `app/main.py` (a supported `app/`
location), and `apps/api/pyproject.toml` makes the entrypoint explicit:

```toml
[tool.vercel]
entrypoint = "app.main:app"

[tool.vercel.scripts]
build = "python -m py_compile app/main.py"
```

`[tool.vercel] entrypoint` points Vercel at the `app` instance in `app/main.py`, and
`[tool.vercel.scripts] build` defines the build step that runs after dependencies
install. A `vercel.json` is not required.

`apps/api/requirements.txt` installs the local monorepo packages with relative editable paths (`-e ../../packages/...` and `-e ../../services/...`), so the API project must be deployed from the full monorepo checkout, not from a copied `apps/api` folder.

Because those paths point outside `apps/api`, enable this on the API project:

```text
Settings → Build and Deployment → Root Directory →
Include source files outside of the Root Directory in the Build Step: ON
```

Without it, the build only sees files inside `apps/api`, and `pip install -r requirements.txt` fails to resolve the `../../packages` and `../../services` editable installs. The web project keeps this setting OFF; it installs only from inside `apps/web`.

The Streamlit, pandas, plotly, and file-ingestion dependencies live in each service's local-only `local` dependency group, not its core dependencies, so the API's pip install pulls only the runtime domain logic. This keeps the deployed function bundle small (~65 MB installed, well under the Vercel Functions 500 MB limit). Do not move those dependencies back into `[project] dependencies`.

Health check URL:

```text
/health
```

Expected response:

```json
{"status":"ok"}
```

## API environment variables

Set these on the API Vercel project.

Required for live AI:

```dotenv
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-v4-flash
```

Optional DeepSeek overrides:

```dotenv
DEEPSEEK_MODELS=deepseek-chat,deepseek-reasoner
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

Required for production persistence and production rate limits:

```dotenv
DATABASE_URL=your_neon_postgres_connection_string_with_sslmode_require
API_PERSISTENCE_ENABLED=true
API_RATE_LIMIT_STORE=postgres
API_RATE_LIMIT_HASH_SALT=replace_with_high_entropy_secret
```

Required CORS setting:

```dotenv
API_CORS_ORIGINS=https://your-web-production-domain.vercel.app
```

If the web project has preview deployments, include the exact preview origins you intend to test against:

```dotenv
API_CORS_ORIGINS=https://your-web-production-domain.vercel.app,https://your-web-git-branch-team.vercel.app
```

Other API settings:

```dotenv
API_LIVE_RATE_LIMIT_COUNT=6
API_LIVE_RATE_LIMIT_WINDOW_SECONDS=3600
API_MAX_REQUEST_BODY_BYTES=64000
API_TRUST_PROXY_HEADERS=false
```

Keep `API_TRUST_PROXY_HEADERS=false` unless the deployment sits behind a trusted proxy that strips untrusted forwarding headers.

Optional future Vercel Blob setting:

```dotenv
BLOB_READ_WRITE_TOKEN=your_vercel_blob_token_here
```

The current public API accepts pasted SOP text only and does not store original SOP uploads, so Vercel Blob is not required today.

## Web environment variables

Set these on the web Vercel project.

Required for frontend-to-backend calls:

```dotenv
NEXT_PUBLIC_STUDY_ABROAD_API_URL=https://your-api-production-domain.vercel.app
```

That is the only variable the web project needs. Lead capture is handled by the backend (`POST /api/v1/leads` → Neon `tool_leads`), so the web project requires no database credentials.

Do not set `DEEPSEEK_API_KEY`, `DATABASE_URL`, `API_RATE_LIMIT_HASH_SALT`, or `BLOB_READ_WRITE_TOKEN` on the web project. All `NEXT_PUBLIC_` values are browser-visible.

## Preview vs production setup

Use separate Vercel environment scopes.

Preview API:

```dotenv
DEEPSEEK_API_KEY=preview_or_low_quota_deepseek_key
DATABASE_URL=preview_neon_branch_or_database_url_with_sslmode_require
API_PERSISTENCE_ENABLED=true
API_RATE_LIMIT_STORE=postgres
API_RATE_LIMIT_HASH_SALT=preview_only_random_secret
API_CORS_ORIGINS=https://your-web-preview-domain.vercel.app
```

Preview web:

```dotenv
NEXT_PUBLIC_STUDY_ABROAD_API_URL=https://your-api-preview-domain.vercel.app
```

Production API:

```dotenv
DEEPSEEK_API_KEY=production_deepseek_key
DATABASE_URL=production_neon_database_url_with_sslmode_require
API_PERSISTENCE_ENABLED=true
API_RATE_LIMIT_STORE=postgres
API_RATE_LIMIT_HASH_SALT=production_random_secret
API_CORS_ORIGINS=https://your-production-web-domain
```

Production web:

```dotenv
NEXT_PUBLIC_STUDY_ABROAD_API_URL=https://your-production-api-domain
```

Use separate Neon branches or databases for preview and production. Do not reuse `API_RATE_LIMIT_HASH_SALT` between environments.

## Database migrations

Run migrations before routing traffic to a new API database:

```bash
cd apps/api
DATABASE_URL=your_neon_postgres_connection_string_with_sslmode_require uv run python -m app.persistence.migrations
```

Vercel builds should not run migrations automatically because builds can run more than once and against preview environments.

## Local production-like verification

Run the same checks that deployment relies on:

```bash
cd apps/web
npm ci
npm run build
```

```bash
cd apps/api
uv sync --locked
uv run python -m py_compile app/main.py
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
curl http://127.0.0.1:8000/health
```

For API tests:

```bash
cd apps/api
uv run pytest
```

For a frontend smoke test against the local API:

```bash
cd apps/web
NEXT_PUBLIC_STUDY_ABROAD_API_URL=http://127.0.0.1:8000 npm run build
```

Then start the API and web app locally and exercise demo mode on `/tools/sop-review` and `/tools/admit-predictor`.

## Post-deploy smoke checks

After each API deploy:

```bash
curl https://your-api-domain.vercel.app/health
```

After each web deploy:

- Open `/tools/sop-review`.
- Open `/tools/admit-predictor`.
- Submit demo-mode requests for both tools.
- Submit live-mode requests only when `DEEPSEEK_API_KEY`, `DATABASE_URL`, rate-limit salt, and CORS are configured for that environment.

## Public-repo safety

- Commit only placeholders and variable names.
- Keep DeepSeek keys, Neon URLs, rate-limit salts, and Blob tokens in Vercel environment settings.
- Keep DeepSeek and database credentials backend-only.
- Keep `NEXT_PUBLIC_STUDY_ABROAD_API_URL` pointed at the matching API environment so deployed frontend requests reach the deployed backend.
