# Evaluation strategy

## Current automated coverage

Prompt-heavy services have synthetic regression coverage:

- SOP fixtures check schema validity, prompt version metadata, exact rubric ordering, concise output shape, and broad qualitative tendencies across strong, average, weak/generic, and invalid non-SOP cases.
- Admissions fixtures check stable schema usage, prompt version metadata, concise profile-grounded reasons, and broad calibration across strong, borderline, weak, and unrealistic-target profiles.

Contract tests in `packages/contracts` verify that committed mock payloads conform to the same response models as live API responses. API tests cover mock endpoints, validation errors, live rate-limit behavior with fakes, provider failure handling, and redaction behavior. Frontend tests cover rendered contract assumptions for the SOP and admissions mock payloads.

## What to run

```bash
cd services/sop_review
uv run python -m unittest discover -s tests

cd ../admissions
uv run pytest

cd ../../packages/contracts
uv run pytest

cd ../ai_runtime
uv run pytest

cd ../../apps/api
uv run pytest

cd ../web
npm run test
```

## Evaluation principles

- Use sanitized synthetic fixtures only; never commit raw user submissions.
- Prefer small fixtures that represent distinct failure modes over large fixture volume.
- Keep schema and parser tests deterministic.
- Evaluate model/provider changes as behavior changes, not dependency swaps.
- Mock and live response shapes must remain contract-compatible.
- Human judgment remains required for admissions counseling and SOP quality assessment.

## Gaps

- No large human-labeled benchmark exists.
- No periodic production-quality review workflow is implemented.
- No end-to-end browser test suite exists yet.
- CI runs package-level API, contract, shared runtime, service, and web checks,
  but it does not yet run browser-level end-to-end mock-flow checks.

## Roadmap

1. Add end-to-end mock-flow coverage for SOP Review and Admit Predictor.
2. Expand fixtures only for new failure modes.
3. Add human review of sampled live outputs for quality, calibration, factual restraint, and usefulness.
4. Track prompt changes by prompt version and fixture diffs.
5. Add provider-contract tests before any future vendor replacement.
