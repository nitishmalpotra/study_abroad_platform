# SOP Review & Grader

Streamlit-backed SOP review service with reusable backend modules, DeepSeek integration through the shared AI runtime, and SQLite persistence.

## Production Features

- Streamlit UI with sidebar applicant form and SOP input tabs.
- SOP input via paste or upload (`.pdf`, `.docx`, `.txt`) with upload-size guardrails.
- Two-step gatekeeper:
  - Word count validation (`100-2500` words by default).
  - Provider-backed SOP validity check in English (currently DeepSeek).
- Strict grading pipeline using structured Pydantic schemas.
- SQLite persistence of metadata + full raw SOP text + full AI feedback JSON.
- LLM resilience:
  - Model fallback across configurable DeepSeek model IDs.
  - Retry with backoff.
- Ops hardening:
  - Session rate limiting.
  - Rotating logs in `logs/app.log`.
  - DB WAL mode, busy timeout, and indexes.
- Results UX:
  - Overall score, criteria chart/table, detailed feedback, disclaimer.
  - Downloadable AI feedback JSON.

## Local Setup (uv + virtual environment)

1. Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install Python 3.11 via `uv`:

```bash
uv python install 3.11
```

3. Create a virtual environment:

```bash
uv venv --python 3.11 .venv
```

4. Activate the virtual environment:

```bash
source .venv/bin/activate
```

5. Install project dependencies from `pyproject.toml`:

```bash
uv sync
```

6. Create env file:

```bash
cp .env.example .env
```

7. Set your API key in `.env`:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

8. Run the app:

```bash
uv run streamlit run app.py
```

## Build Project

1. Generate/update lockfile:

```bash
uv lock
```

2. Build validation (syntax check):

```bash
uv run python -m py_compile app.py
```

3. Optional container build:

```bash
docker build -t sop-review-grader .
```

## Runtime Configuration

Supported environment variables:

- `DEEPSEEK_API_KEY` (required)
- `DEEPSEEK_MODEL` (default `deepseek-chat`)
- `DEEPSEEK_MODELS` (optional comma-separated fallback order)
- `DEEPSEEK_BASE_URL` (default `https://api.deepseek.com`)
- `APP_ENV` (`prod` or `dev`; default `prod`)
- `SOP_DB_PATH` (default `sop_app.db`)
- `SOP_MIN_WORDS` (default `100`)
- `SOP_MAX_WORDS` (default `2500`)
- `SOP_MAX_UPLOAD_MB` (default `10`)
- `SOP_MAX_CHARS` (default `30000`)
- `LLM_TIMEOUT_SECONDS` (default `45`)
- `LLM_RETRY_ATTEMPTS` (default `2`)
- `LLM_RETRY_BACKOFF_SECONDS` (default `1.0`)
- `SOP_RATE_LIMIT_COUNT` (default `6`)
- `SOP_RATE_LIMIT_WINDOW_MIN` (default `60`)

## Docker Deployment

```bash
docker build -t sop-review-grader .
docker run --rm -p 8501:8501 --env-file .env sop-review-grader
```

## Database

Local DB file: `sop_app.db` (or `SOP_DB_PATH`)

Table: `submissions`

- `id` (INTEGER, PK, AUTOINCREMENT)
- `timestamp` (DATETIME)
- `full_name` (TEXT)
- `university` (TEXT)
- `intake` (TEXT)
- `country` (TEXT)
- `sop_text` (TEXT) -> full raw SOP text
- `overall_score` (REAL)
- `ai_feedback_json` (TEXT) -> full JSON response from DeepSeek
