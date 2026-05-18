# API contracts

`packages/contracts` is the contract boundary between the FastAPI surface and frontend consumers.

- Python `pydantic` models in `study_abroad_contracts.api` are the canonical runtime contracts used by the backend.
- Committed JSON Schemas in `packages/contracts/schemas` are generated from those models and tested for drift.
- Frontend TypeScript types in `packages/contracts/ts/api.ts` mirror the same public payloads and are re-exported into `apps/web`.
- SOP review and admissions prediction stay as separate contracts because they are separate user workflows, even though both use the shared AI runtime underneath.
- Mock responses are maintained inside `study_abroad_contracts.examples` and must validate against the same response models as live responses.

Contract names follow backend domain language: `SOPReview*`, `AdmissionsPrediction*`, `AdmissionPrediction`, `SOPGrade`, and `ApiError`.

## Versioning strategy

The public API currently lives under `/api/v1`. Additive, backward-compatible changes may ship within `v1` when both the Python contracts and TypeScript types are updated together. Breaking changes require:

1. a new route version or an explicitly coordinated migration,
2. updated contract models and JSON Schemas,
3. updated TypeScript types,
4. contract-test updates that make the change visible in review.

The committed JSON Schemas are intentional review artifacts: if a schema changes, the diff should show exactly which fields or constraints moved.
