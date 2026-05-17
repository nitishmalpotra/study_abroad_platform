# Evaluation strategy

## Current state

Initial automated evaluation suites now exist for both prompt-heavy services:

- SOP prompt behavior: sanitized synthetic fixtures plus golden outputs check schema validity, exact rubric ordering, concise output shape, and coarse qualitative tendencies across strong, average, weak/generic, and invalid non-SOP cases.
- Admissions prompt behavior: sanitized synthetic fixtures plus golden outputs check stable schema usage, prompt version metadata, concise profile-grounded reasons, and broad calibration across strong, borderline, weak, and unrealistic-target profiles.

Frontend flows and cross-service contract evaluations are still not established.

## What should be evaluated during migration

- schema validity and parser resilience
- prompt parity when moving from Gemini to DeepSeek
- admissions post-processing, prompt calibration, and repair behavior
- SOP grading consistency against approved examples
- real versus mock/demo switching behavior
- frontend/backend contract compatibility
- rate-limit and error-handling behavior once the public API exists

## Practical next steps

1. Expand sanitized fixtures only when they add distinct failure modes.
2. Keep deterministic schema and parsing tests as the first regression layer.
3. Add provider-contract tests before changing vendors.
4. Expand admissions fixtures only for distinct failure modes rather than fixture volume.
5. Add periodic human review of live model outputs for judgment quality, calibration, factual restraint, and recommendation usefulness.

Raw user submissions must not be committed as fixtures.
