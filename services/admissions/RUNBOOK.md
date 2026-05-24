# RUNBOOK: College Admission Predictor

## Goal
Validate that:
1. Input sanitization and logical bounds are enforced.
2. Nested JSON output is generated and parsed correctly.
3. Data is persisted in SQLite.

## 1. Pre-Run Checks
1. Confirm `.env` has `DEEPSEEK_API_KEY`.
2. Create venv and install deps:
   ```bash
   uv python install 3.11
   uv venv .venv --python 3.11
   source .venv/bin/activate
   uv sync
   ```
3. Start app:
   ```bash
   uv run streamlit run app.py
   ```

## 2. Bounds Testing (Manual)

### Test Case A: CGPA exceeds selected scale
1. Select CGPA scale `4`.
2. Enter CGPA `8.1`.
3. Submit.
Expected:
- Error: `CGPA cannot exceed 4 for the selected scale.`
- No prediction is generated.

### Test Case B: IELTS out of range
1. Select `IELTS`.
2. Enter English score `9.5`.
3. Submit.
Expected:
- Error: `IELTS score must be between 0 and 9.`

### Test Case C: TOEFL out of range
1. Select `TOEFL`.
2. Enter English score `130`.
3. Submit.
Expected:
- Error: `TOEFL score must be between 0 and 120.`

### Test Case D: GRE invalid bounds
1. Enter GRE `350`.
2. Submit.
Expected:
- Error: `GRE score must be between 260 and 340.`

### Test Case E: Mandatory target program missing
1. Leave `Target Program 1` blank.
2. Submit.
Expected:
- Error: `Target Program 1 is mandatory.`

### Test Case F: Duplicate target programs
1. Enter same value in Program 1 and Program 2.
2. Submit.
Expected:
- Error: `Target programs must be distinct.`

## 3. Nested JSON Output Validation
Use a valid profile and 3-5 target programs, then submit.

Expected:
1. UI renders:
   - one prediction card per target program
   - strengths (3 items)
   - weaknesses (3 items)
   - roadmap (3 items)
   - alternatives (3 items)
2. `Raw AI JSON Output` expander shows valid JSON.
3. Schema fields exist:
   - `target_predictions[].program_name`
   - `target_predictions[].chance_category`
   - `target_predictions[].estimated_probability_percentage`
   - `target_predictions[].brief_reasoning`
   - `profile_strengths`
   - `profile_weaknesses`
   - `actionable_roadmap`
   - `recommended_universities`

## 4. Database Persistence Verification
After a successful submission:

```bash
sqlite3 admissions_app.db "SELECT id, created_at, full_name, target_programs FROM predictions ORDER BY id DESC LIMIT 5;"
```

Expected:
- New row inserted for each successful prediction.

To inspect raw output:

```bash
sqlite3 admissions_app.db "SELECT ai_raw_output FROM predictions ORDER BY id DESC LIMIT 1;"
```

## 5. Failure Handling Test
Temporarily remove `DEEPSEEK_API_KEY` from `.env` and restart app.

Expected:
- Submission fails with a clear error indicating missing API key.
- App remains responsive.

## 6. Operational Notes
- Default model: `deepseek-v4-flash`.
- Override model using `.env` with any model your API key can access:
  - `DEEPSEEK_MODEL=deepseek-v4-pro`
- SQLite DB is local and suitable for single-instance deployment.
