# College Admission Predictor

Production-grade Streamlit application that predicts admission chances for up to five target Master's programs using DeepSeek through the shared AI runtime, with SQLite persistence.

## Tech Stack
- Frontend: Streamlit
- LLM: DeepSeek via shared AI runtime
- Validation: Pydantic strict nested schema
- Storage: SQLite (`admissions_app.db`)
- Config: `.env` with `python-dotenv`
- Visualization: Plotly + Streamlit components
- Dependency Management: `uv` + `pyproject.toml`

## Prerequisites
- Python 3.10 to 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- DeepSeek API key (`DEEPSEEK_API_KEY`)

## Install With uv (Recommended)

1. Install `uv`:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install Python (example: 3.11) and create a virtual environment:
   ```bash
   uv python install 3.11
   uv venv .venv --python 3.11
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

4. Sync dependencies from `pyproject.toml`:
   ```bash
   uv sync
   ```

## Environment Configuration

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Notes:
- `.env` is intentionally gitignored. Do not commit real API keys.
- `DEEPSEEK_MODEL` selects the primary model.
- `DEEPSEEK_MODELS` optionally defines a comma-separated fallback order.
- `DEEPSEEK_BASE_URL` defaults to `https://api.deepseek.com`.
- Keep `temperature=0.0` for deterministic outputs.

## Run The App

```bash
uv run streamlit run app.py
```

Then open the URL shown by Streamlit (typically `http://localhost:8501`).

## Build The Project

Build source and wheel distributions:

```bash
uv build
```

Artifacts are generated in `dist/`.

## Troubleshooting
- Error: `Missing SOP_APP_ACCESS_TOKEN while SOP_REQUIRE_ACCESS_TOKEN is enabled`
  - This is external runtime policy, not an app requirement.
  - Disable it for this run:
    ```bash
    SOP_REQUIRE_ACCESS_TOKEN=false uv run streamlit run app.py
    ```

## What Is Production-Ready Here
- Strict output schema enforcement with nested Pydantic models.
- One repair pass for malformed model output before failing safely.
- Input sanitization and logical bounds validation.
- SQLite hardened with WAL mode and busy timeout.
- Runtime configuration validation from environment variables.
- LLM invocation retry policy with controlled backoff.
- Error sanitization to avoid exposing sensitive values.

## Database
- File: `admissions_app.db`
- Table: `predictions`
- Created automatically on first run; keep it local and out of git.
- Stored:
  - profile payload (`profile_json`)
  - target programs (`target_programs`)
  - raw model JSON (`ai_raw_output`)
  - metadata (`created_at`, `full_name`, `target_intake`, `target_country`)
