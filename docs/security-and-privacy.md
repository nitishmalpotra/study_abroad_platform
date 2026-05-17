# Security and privacy

## Public repository hygiene

Do not commit:

- secrets or real API keys
- local databases
- raw user documents or uploaded SOP files
- personal absolute paths
- generated runtime logs

The root `.gitignore` intentionally excludes these categories. Example configuration files are safe placeholders only.

## Current data handling

- `services/sop_review` stores submission metadata, raw SOP text, and AI feedback JSON in a local SQLite database.
- `services/admissions` stores submitted profile data and model output in a local SQLite database.
- `apps/web` uses Supabase for lead capture.

The current implementation does not yet provide the planned centralized retention job, production Postgres path, or blob-storage-backed upload lifecycle.

## Planned posture

The migration blueprint targets:

- explicit retention and deletion workflows
- production persistence outside local SQLite
- real/mock AI mode separation
- safer public API boundaries and shared validation
- stronger rate limiting and operational observability

Until those phases land, contributors should treat local data artifacts as sensitive and keep them outside version control.
