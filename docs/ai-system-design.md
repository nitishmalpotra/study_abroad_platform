# AI system design

## Current implementation

Both Python services call DeepSeek through the shared `packages/ai_runtime` package today.

- SOP review performs a validity check and grading pass, then parses structured feedback.
- Admissions prediction builds a structured recommendation payload and includes one repair pass for malformed model output.
- `apps/api` exposes live SOP and admissions endpoints through the shared runtime, plus deterministic mock endpoints that do not call DeepSeek.
- The frontend SOP experience is a hard-coded mock UI rather than an API-backed AI flow.

## Target direction

The migration blueprint proposes:

- one shared AI runtime for provider clients, retries, response parsing/repair, logging, and redaction
- separate task-specific modules for SOP review and admissions prediction
- DeepSeek for real production requests
- mock providers for demo mode
- shared domain logic outside UI frameworks
- common API contracts for SOP and admissions responses

The service extraction, shared runtime, DeepSeek wiring, FastAPI surface, and shared contracts are now implemented. Frontend API integration, production persistence, and release hardening remain future migration work.

## Design guardrails

- Preserve structured validation rather than trusting raw model text.
- Keep mock/demo execution explicit so it is not confused with real inference.
- Treat provider migration as a parity exercise; behavior should be validated before any future provider replacement.
