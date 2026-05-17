# RUNBOOK

## Health Check

1. Install dependencies:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

2. Ensure `.env` contains a valid Gemini API key:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

3. Start app:

```bash
uv run streamlit run app.py
```

4. Open the local Streamlit URL (usually `http://localhost:8501`) and verify:
- Sidebar fields accept values.
- SOP input accepts pasted text or uploaded file.
- Pipeline status shows:
  - `Reading file...`
  - `Verifying content...`
  - `Grading...`
- Valid submission creates a record in `sop_app.db`.

5. Verify operational controls:
- `logs/app.log` is created and receives entries.
- Rate limiting triggers after repeated requests in one session.
- Invalid content is blocked by gatekeeper and not inserted in DB.

## Container Health Check

```bash
docker build -t sop-review-grader .
docker run --rm -p 8501:8501 --env-file .env sop-review-grader
```

Then verify app availability:

```bash
curl -I http://localhost:8501/
```

Expected: HTTP response headers are returned.

## Backup / Restore

Backup:

```bash
cp sop_app.db sop_app_$(date +%Y%m%d_%H%M%S).db
```

Restore:

```bash
cp sop_app_backup.db sop_app.db
```

## Data Access

Use this Python snippet to export saved SOP submissions to CSV:

```python
import sqlite3
import pandas as pd

DB_PATH = "sop_app.db"
OUT_CSV = "sop_submissions_export.csv"

with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query(
        """
        SELECT
            id,
            timestamp,
            full_name,
            university,
            intake,
            country,
            overall_score,
            sop_text,
            ai_feedback_json
        FROM submissions
        ORDER BY id DESC
        """,
        conn,
    )

df.to_csv(OUT_CSV, index=False)
print(f"Exported {len(df)} rows to {OUT_CSV}")
```
