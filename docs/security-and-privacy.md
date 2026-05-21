# Security and privacy

## Public repository hygiene

Do not commit:

- secrets or real API keys
- local databases
- raw user documents or uploaded SOP files
- personal absolute paths
- generated runtime logs

The root `.gitignore` intentionally excludes these categories. Example configuration files are safe placeholders only.

DeepSeek keys belong only in backend or standalone-service environments:

- `apps/api/.env` for the public FastAPI-backed tools
- `services/sop_review/.env` for the standalone SOP Streamlit app
- `services/admissions/.env` for the standalone admissions Streamlit app

Never put `DEEPSEEK_API_KEY` in `apps/web/.env`; `NEXT_PUBLIC_` values are browser-visible.

## Current data handling

- `services/sop_review` stores submission metadata, raw SOP text, and AI feedback JSON in a local SQLite database.
- `services/admissions` stores submitted profile data and model output in a local SQLite database.
- `apps/web` uses Supabase for lead capture.
- `apps/api` can persist production tool records to Neon Postgres when
  `DATABASE_URL` and `API_PERSISTENCE_ENABLED=true` are set.
- API SOP review persistence stores university, intake, country, SOP word count,
  overall score, and structured grade JSON. It does not store full name, phone
  number, raw SOP text, uploaded file bytes, or raw provider output.
- API admissions persistence stores target intake/country, academic profile
  summary fields, target programs, and structured prediction JSON. It does not
  store the applicant full name or raw provider output.
- API Postgres rate limiting stores only salted hashes of anonymous client
  identifiers, rate-limit scope, window start, window length, and hit count.
- Live SOP review and admissions prediction endpoints are public and do not
  require sign-in. Mock endpoints remain separate and deterministic.

The current implementation does not yet provide a centralized retention job or
blob-storage-backed upload lifecycle.

## Retention posture

Default retention should favor minimization:

- SOP text and uploaded files: transient processing only for the first public API
  release; discard after response generation.
- SOP review records: retain summarized review records only as long as needed for
  product analytics, quality monitoring, and abuse investigation.
- Admissions prediction records: retain summarized prediction records only as
  long as needed for product analytics, quality monitoring, and abuse
  investigation.
- Rate-limit buckets: retain briefly, enough to enforce the configured window and
  investigate abuse. They contain salted hashes, not raw IP addresses.

Before launch, define an operational deletion schedule for Neon tables and document
the exact retention windows. Until then, avoid expanding stored fields.

## Public API threat model

The first public release assumes anonymous users can call API endpoints directly,
hide frontend UI, send malformed JSON, submit oversized payloads, retry provider
failures, and attempt to trigger logs or error messages containing sensitive
data. The API does not treat frontend controls as a security boundary.

Current controls:

- backend-enforced live AI rate limits apply before model calls and exclude mock
  endpoints
- Postgres-backed rate limits are available for production and store salted
  identifier hashes instead of raw IP addresses
- `x-forwarded-for` is ignored by default; set `API_TRUST_PROXY_HEADERS=true`
  only behind a trusted proxy that strips untrusted forwarding headers
- mock endpoints are separate paths and do not instantiate live model providers
- requests must use `application/json`
- API request bodies are capped by `API_MAX_REQUEST_BODY_BYTES`
- SOP text is additionally capped by the shared contract and SOP service
  settings; SOP uploads are not accepted by the API in this release
- Pydantic contracts reject unknown fields and invalid scalar ranges
- unhandled errors return generic structured payloads, while provider failures
  return a safe `503` response
- structured API logs include request metadata and redacted exception text, not
  raw request bodies or provider keys
- CORS is restricted to `API_CORS_ORIGINS`; CORS is not considered an abuse
  prevention control because non-browser clients can call the API directly
- frontend live tool pages disclose that AI output is informational and not a
  human review or admissions guarantee

Known residual risks:

- in-memory rate limiting is suitable only for local development or a single
  process; production should use `API_RATE_LIMIT_STORE=postgres`
- anonymous IP-based limits can affect users behind shared networks and are not
  a complete bot mitigation strategy
- no CAPTCHA, WAF, queueing layer, automated retention job, or centralized abuse
  workflow is implemented yet
- lead-capture OTP is a UI flow only and does not currently send or verify a
  real OTP
- API, contract, and shared runtime checks are documented but not yet included
  in GitHub Actions CI

## Planned posture

The migration blueprint targets:

- explicit retention and deletion workflows
- stronger bot mitigation for anonymous public use
- centralized operational dashboards and alerts

Until those phases land, contributors should treat local data artifacts as sensitive and keep them outside version control.
