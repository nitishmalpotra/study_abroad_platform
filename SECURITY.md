# Security Policy

## Reporting a vulnerability

Please report suspected vulnerabilities privately to the maintainers rather than opening a public issue. Include the affected area, reproduction steps, impact, and any suggested remediation. A public disclosure timeline should be agreed only after maintainers have had a reasonable opportunity to investigate and patch.

## Repository hygiene

This repository must not contain:

- secrets or real API keys
- local databases such as SQLite files
- raw user documents or SOP uploads
- personal absolute paths from a contributor machine
- generated runtime logs

Use `.env.example` files for documentation and keep real `.env` files local. If sensitive material is committed accidentally, rotate the secret or remove the data at the source; deleting a later commit is not sufficient.

## Current security posture

The current repo contains a Next.js frontend, a FastAPI backend, and two
Streamlit service adapters. Live AI calls use DeepSeek through the backend and
shared AI runtime; the frontend only receives public API URLs and must never
expose the DeepSeek key. Public live AI endpoints do not require sign-in, so the
API enforces live-only backend rate limits, JSON/body-size guards, request
validation, restricted CORS, safe structured errors, and secret-redacted
structured logs. Mock endpoints are separate from live endpoints and do not call
DeepSeek.

Production should use `API_RATE_LIMIT_STORE=postgres` with
`API_RATE_LIMIT_HASH_SALT` so anonymous rate-limit buckets are stored as salted
hashes rather than raw client identifiers. In-memory rate limiting is only for
local development or single-process smoke tests. Blob storage and automated
retention jobs remain planned in the migration blueprint; current public API SOP
uploads are not accepted or retained.
