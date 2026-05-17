# Evaluation strategy

## Current state

An initial automated evaluation suite now exists for SOP prompt behavior. It uses sanitized synthetic fixtures plus golden outputs to check schema validity, exact rubric ordering, concise output shape, and coarse qualitative tendencies across strong, average, weak/generic, and invalid non-SOP cases. Admissions, frontend flows, and cross-service contract evaluations are still not established.

## What should be evaluated during migration

- schema validity and parser resilience
- prompt parity when moving from Gemini to DeepSeek
- admissions post-processing and repair behavior
- SOP grading consistency against approved examples
- real versus mock/demo switching behavior
- frontend/backend contract compatibility
- rate-limit and error-handling behavior once the public API exists

## Practical next steps

1. Expand sanitized fixtures only when they add distinct failure modes.
2. Keep deterministic schema and parsing tests as the first regression layer.
3. Add provider-contract tests before changing vendors.
4. Add admissions regression examples once that target contract is fixed.
5. Add periodic human review of live model outputs for judgment quality, calibration, and factual restraint.

Raw user submissions must not be committed as fixtures.
