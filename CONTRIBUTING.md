# Contributing

Thanks for contributing to Study Abroad Platform. This repository is public-facing and still mid-migration, so changes should keep current behavior honest while moving toward the target architecture in `docs/MIGRATION_BLUEPRINT.md`.

## Development principles

- Keep the current frontend theme intact unless a change explicitly targets design.
- Do not commit secrets, local databases, raw user documents, generated runtime logs, or personal absolute paths.
- Prefer small, reviewable changes that preserve the existing app behavior.
- Update documentation when behavior or setup changes.
- Label planned work as planned; do not document future architecture as already implemented.

## Local checks

Run only the checks that apply to the area you changed:

```bash
# Frontend
cd apps/web
npm ci
npm run lint
npm run typecheck
npm run build

# Admissions service
cd services/admissions
uv sync --locked
uv run ruff check app.py
uv run pytest
uv run python -m py_compile app.py

# SOP review service
cd services/sop_review
uv sync --locked
uv run python -m unittest discover -s tests
uv run python -m py_compile app.py
```

Automated service tests now exist for both Python tools. API, frontend, contract, and end-to-end coverage are still planned later in the migration.

## Pull requests

- Explain what changed and why.
- Call out any migration assumptions or follow-up work.
- Include verification commands and results.
- Never include `.env` files, exported data, screenshots containing user data, or local database files.
