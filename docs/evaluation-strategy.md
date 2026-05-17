# Evaluation strategy

## Current state

There is no established automated evaluation suite yet for model quality, frontend flows, or cross-service contracts.

## What should be evaluated during migration

- schema validity and parser resilience
- prompt parity when moving from Gemini to DeepSeek
- admissions post-processing and repair behavior
- SOP grading consistency against approved examples
- real versus mock/demo switching behavior
- frontend/backend contract compatibility
- rate-limit and error-handling behavior once the public API exists

## Practical next steps

1. Capture representative, sanitized fixtures.
2. Add deterministic schema and parsing tests first.
3. Add provider-contract tests before changing vendors.
4. Add regression examples for SOP and admissions outputs once target contracts are fixed.

Raw user submissions must not be committed as fixtures.
