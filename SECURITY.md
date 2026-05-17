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

The current repo contains a Vite frontend plus two Streamlit services. The services still use Gemini and local SQLite storage, and the frontend SOP experience is still mock-only. Planned controls such as a shared API layer, DeepSeek provider abstraction, centralized rate limiting, production Postgres storage, blob storage, and retention automation are described in the migration blueprint but are not implemented yet.
