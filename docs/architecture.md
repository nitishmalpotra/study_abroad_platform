# Architecture

## Current state

The repository is a transitional monorepo:

- `apps/web`: Vite + React marketing frontend with Supabase-backed lead capture and a mock-only SOP page
- `services/sop_review`: Streamlit SOP review tool using Gemini, local SQLite persistence, file uploads, and runtime logs
- `services/admissions`: Streamlit admissions predictor using Gemini and local SQLite persistence
- `docs/MIGRATION_BLUEPRINT.md`: approved migration target and phase plan

There is no shared public API, no FastAPI app, no shared AI runtime, and no unified mock/demo mode yet. Both extracted services now expose provider protocols so orchestration is no longer tied to Streamlit, but vendor-specific provider implementations are still duplicated per service.

## Migration target

The migration blueprint targets:

- a Next.js frontend that preserves the current KlassFin visual theme
- a FastAPI backend as the only public backend entry point
- a shared AI runtime for provider clients, retries, response parsing/repair, logging, and redaction
- separate task-specific domain modules for SOP review and admissions prediction
- DeepSeek for real requests and mock providers for demo mode
- shared contracts, centralized persistence, stronger rate limiting, and explicit retention workflows

Those target components are planned, not present in the current codebase.

## Data flow today

```mermaid
flowchart LR
  A["Vite frontend"] --> B["Supabase lead table"]
  C["SOP Streamlit app"] --> D["Gemini"]
  C --> E["Local SQLite"]
  F["Admissions Streamlit app"] --> D
  F --> G["Local SQLite"]
```

## Key constraints

- Preserve the current frontend theme during migration.
- Keep docs aligned to shipped behavior.
- Treat local SQLite databases, uploaded SOPs, and runtime logs as local-only artifacts that must never be committed.
