# AI system design

## Current implementation

Both Python services call Gemini through LangChain today.

- SOP review performs a validity check and grading pass, then parses structured feedback.
- Admissions prediction builds a structured recommendation payload and includes one repair pass for malformed model output.
- The frontend SOP experience is a hard-coded mock UI rather than an API-backed AI flow.

## Target direction

The migration blueprint proposes:

- a provider abstraction
- DeepSeek for real production requests
- mock providers for demo mode
- shared domain logic outside UI frameworks
- common API contracts for SOP and admissions responses

These are planned architecture changes; DeepSeek is not wired into the current repo yet.

## Design guardrails

- Preserve structured validation rather than trusting raw model text.
- Keep mock/demo execution explicit so it is not confused with real inference.
- Treat provider migration as a parity exercise; current Gemini behavior should be validated before replacement.
