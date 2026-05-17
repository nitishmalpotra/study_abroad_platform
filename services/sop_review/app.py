import logging
import os
import re
import sqlite3
import time
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from io import BytesIO
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, List, Sequence, Tuple
from uuid import uuid4

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from docx import Document
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field, ValidationError, field_validator
from pypdf import PdfReader


DEFAULT_MODEL_CANDIDATES: Tuple[str, ...] = (
    "gemini-2.5-flash", 
    "gemini-3-flash-preview",
)
EXPECTED_CRITERIA: List[str] = [
    "Academic Fit",
    "University Specificity",
    "Career Clarity",
    "Narrative Flow",
    "Language & Tone",
]
UNIVERSITY_PLACEHOLDER = "Select University"
INTAKE_PLACEHOLDER = "Select Intake"


@dataclass(frozen=True)
class AppSettings:
    db_path: Path
    min_words: int
    max_words: int
    max_upload_mb: int
    max_sop_chars: int
    llm_retries: int
    llm_retry_backoff_sec: float
    max_requests_per_window: int
    rate_limit_window_minutes: int
    app_env: str
    model_candidates: Tuple[str, ...]


@dataclass
class StudentProfile:
    full_name: str
    mobile: str
    university: str
    intake: str
    country: str


class GatekeeperResponse(BaseModel):
    is_valid: bool = Field(description="True only if input is a valid SOP in English.")
    reason: str = Field(description="One concise reason for the decision.")


class CriterionFeedback(BaseModel):
    name: str
    score: float
    feedback: str

    @field_validator("score")
    @classmethod
    def validate_score(cls, value: float) -> float:
        if not 1 <= value <= 10:
            raise ValueError("Criterion score must be between 1 and 10.")
        return round(float(value), 2)


class SOPGrade(BaseModel):
    overall_score: float
    criteria_breakdown: List[CriterionFeedback]
    summary: str

    @field_validator("overall_score")
    @classmethod
    def validate_overall_score(cls, value: float) -> float:
        if not 1 <= value <= 10:
            raise ValueError("overall_score must be between 1 and 10.")
        return round(float(value), 2)

    @field_validator("criteria_breakdown")
    @classmethod
    def validate_criteria_breakdown(
        cls, value: List[CriterionFeedback]
    ) -> List[CriterionFeedback]:
        names = [item.name for item in value]
        missing = [name for name in EXPECTED_CRITERIA if name not in names]
        if missing:
            raise ValueError(
                f"Missing required criteria in criteria_breakdown: {', '.join(missing)}"
            )
        return value


def _env_int(name: str, default: int, min_value: int, max_value: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        parsed = int(raw)
    except ValueError:
        return default
    return max(min_value, min(parsed, max_value))


def _env_float(name: str, default: float, min_value: float, max_value: float) -> float:
    raw = os.getenv(name, str(default))
    try:
        parsed = float(raw)
    except ValueError:
        return default
    return max(min_value, min(parsed, max_value))


def load_settings() -> AppSettings:
    models = parse_model_candidates(
        os.getenv("SOP_GEMINI_MODELS", ",".join(DEFAULT_MODEL_CANDIDATES))
    )
    return AppSettings(
        db_path=Path(os.getenv("SOP_DB_PATH", "sop_app.db")),
        min_words=_env_int("SOP_MIN_WORDS", 100, 50, 1000),
        max_words=_env_int("SOP_MAX_WORDS", 2500, 500, 10000),
        max_upload_mb=_env_int("SOP_MAX_UPLOAD_MB", 10, 1, 50),
        max_sop_chars=_env_int("SOP_MAX_CHARS", 30000, 1000, 200000),
        llm_retries=_env_int("SOP_LLM_RETRIES", 2, 1, 5),
        llm_retry_backoff_sec=_env_float("SOP_LLM_RETRY_BACKOFF_SEC", 1.5, 0.5, 10.0),
        max_requests_per_window=_env_int("SOP_RATE_LIMIT_COUNT", 6, 1, 200),
        rate_limit_window_minutes=_env_int("SOP_RATE_LIMIT_WINDOW_MIN", 60, 1, 1440),
        app_env=os.getenv("APP_ENV", "prod").strip().lower(),
        model_candidates=models,
    )


def parse_model_candidates(raw_value: str) -> Tuple[str, ...]:
    parts = [item.strip() for item in (raw_value or "").split(",")]
    models = tuple(item for item in parts if item and "gemini" in item.lower())
    if not models:
        return DEFAULT_MODEL_CANDIDATES
    return models


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("sop_app")
    if logger.handlers:
        return logger

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        log_dir / "app.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def get_db_connection(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path, timeout=30)
    connection.execute("PRAGMA journal_mode=WAL;")
    connection.execute("PRAGMA synchronous=NORMAL;")
    connection.execute("PRAGMA busy_timeout=5000;")
    return connection


def init_db(settings: AppSettings) -> None:
    with get_db_connection(settings.db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                full_name TEXT NOT NULL,
                university TEXT NOT NULL,
                intake TEXT NOT NULL,
                country TEXT NOT NULL,
                sop_text TEXT NOT NULL,
                overall_score REAL NOT NULL CHECK (overall_score >= 1 AND overall_score <= 10),
                ai_feedback_json TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_submissions_timestamp
            ON submissions(timestamp DESC)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_submissions_university
            ON submissions(university)
            """
        )
        connection.commit()


def sanitize_text(value: str, max_length: int = 200) -> str:
    value = (value or "").replace("\x00", " ")
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"[^a-zA-Z0-9\s.,'&()\-+/]", "", value)
    return value[:max_length]


@st.cache_data(show_spinner=False)
def load_university_catalog(path: str = "data/universities.json") -> List[dict]:
    data_path = Path(path)
    if not data_path.is_absolute():
        data_path = Path(__file__).resolve().parent / data_path
    if not data_path.exists():
        return []

    try:
        with data_path.open("r", encoding="utf-8") as handle:
            raw_catalog = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(raw_catalog, list):
        return []

    catalog: List[dict] = []
    for item in raw_catalog:
        if not isinstance(item, dict):
            continue

        name = sanitize_text(str(item.get("name", "")), max_length=160)
        country = sanitize_text(str(item.get("country", "")), max_length=80)
        raw_intakes = item.get("intakes", [])
        if not isinstance(raw_intakes, list):
            continue

        intakes: List[str] = []
        for intake_value in raw_intakes:
            intake = sanitize_text(str(intake_value), max_length=80)
            if intake and intake not in intakes:
                intakes.append(intake)

        if name and country and intakes:
            catalog.append({"name": name, "country": country, "intakes": intakes})

    return catalog


def build_university_lookup(
    catalog: Sequence[dict],
) -> Dict[str, dict]:
    lookup: Dict[str, dict] = {}
    for item in catalog:
        name = item["name"]
        if name not in lookup:
            lookup[name] = item
    return lookup


def sanitize_mobile(value: str) -> str:
    value = (value or "").strip()
    digits = re.sub(r"\D", "", value)
    if not 10 <= len(digits) <= 15:
        return ""
    return digits


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def validate_file_size(file_bytes: bytes, settings: AppSettings) -> None:
    max_size = settings.max_upload_mb * 1024 * 1024
    if len(file_bytes) > max_size:
        raise ValueError(
            f"File is too large. Maximum allowed size is {settings.max_upload_mb} MB."
        )


def read_uploaded_file(uploaded_file, settings: AppSettings) -> str:
    suffix = Path(uploaded_file.name).suffix.lower()
    file_bytes = uploaded_file.getvalue()
    validate_file_size(file_bytes, settings)

    if suffix == ".pdf":
        pages: List[str] = []
        reader = PdfReader(BytesIO(file_bytes))
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        content = "\n".join(pages).strip()
    elif suffix == ".docx":
        document = Document(BytesIO(file_bytes))
        content = "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
    elif suffix == ".txt":
        content = ""
        for encoding in ("utf-8", "utf-16", "latin-1"):
            try:
                content = file_bytes.decode(encoding).strip()
                break
            except UnicodeDecodeError:
                continue
        if not content:
            content = file_bytes.decode("utf-8", errors="ignore").strip()
    else:
        raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")

    if not content:
        raise ValueError("The uploaded file does not contain readable text.")
    return content


def normalize_llm_content(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, Sequence):
        chunks = []
        for item in content:
            if isinstance(item, str):
                chunks.append(item)
            elif isinstance(item, dict) and "text" in item:
                chunks.append(str(item["text"]))
            else:
                chunks.append(str(item))
        return "\n".join(chunks)
    return str(content)


def extract_json_payload(raw_text: str) -> str:
    cleaned = raw_text.strip()
    fenced_match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()
    return cleaned


@st.cache_resource(show_spinner=False)
def get_llm_client(model_name: str, api_key: str) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.0,
        google_api_key=api_key,
        # Keep SDK retries minimal; app-level fallback/retries are handled below.
        max_retries=1,
    )


def invoke_with_model_fallback(
    prompt: ChatPromptTemplate,
    parser: PydanticOutputParser,
    variables: dict,
    settings: AppSettings,
    logger: logging.Logger,
    request_id: str,
) -> Tuple[BaseModel, str, str]:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is missing. Add it to your .env file.")

    parser_instructions = parser.get_format_instructions()
    formatted_messages = prompt.format_messages(
        format_instructions=parser_instructions, **variables
    )
    errors: List[str] = []

    for model_name in settings.model_candidates:
        for attempt in range(1, settings.llm_retries + 1):
            try:
                llm = get_llm_client(model_name, api_key)
                response = llm.invoke(formatted_messages)
                raw_content = normalize_llm_content(response.content).strip()
                parsed = parser.parse(extract_json_payload(raw_content))
                return parsed, raw_content, model_name
            except Exception as exc:  # noqa: BLE001
                error_message = f"{model_name} attempt {attempt}: {exc}"
                errors.append(error_message)
                logger.warning("[%s] LLM call failed: %s", request_id, error_message)
                # Invalid/deprecated model IDs should immediately fall through
                # to next model candidate instead of repeated retries.
                lowered = str(exc).lower()
                if "404 models/" in lowered or "not found for api version" in lowered:
                    break
                if attempt < settings.llm_retries:
                    sleep_time = settings.llm_retry_backoff_sec * attempt
                    time.sleep(sleep_time)

    raise RuntimeError(
        "Failed to get a valid response from Gemini models.\n" + "\n".join(errors)
    )


def run_gatekeeper(
    sop_text: str, settings: AppSettings, logger: logging.Logger, request_id: str
) -> Tuple[GatekeeperResponse, str]:
    word_count = count_words(sop_text)
    if word_count < settings.min_words or word_count > settings.max_words:
        return (
            GatekeeperResponse(
                is_valid=False,
                reason=(
                    f"Word count is {word_count}. SOP must be between "
                    f"{settings.min_words} and {settings.max_words} words."
                ),
            ),
            "local-word-count",
        )

    parser = PydanticOutputParser(pydantic_object=GatekeeperResponse)
    gate_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You validate whether text is a genuine Statement of Purpose (SOP) "
                    "written in English for university admissions. Reject recipes, code, "
                    "gibberish, random text, or non-SOP content."
                ),
            ),
            (
                "human",
                (
                    "Check if this is a valid SOP in English. Return strict JSON.\n"
                    "{format_instructions}\n\n"
                    "TEXT:\n{sop_text}"
                ),
            ),
        ]
    )

    response, _, model_name = invoke_with_model_fallback(
        prompt=gate_prompt,
        parser=parser,
        variables={"sop_text": sop_text},
        settings=settings,
        logger=logger,
        request_id=request_id,
    )
    return response, model_name


def run_grader(
    sop_text: str,
    university: str,
    country: str,
    settings: AppSettings,
    logger: logging.Logger,
    request_id: str,
) -> Tuple[SOPGrade, str, str]:
    parser = PydanticOutputParser(pydantic_object=SOPGrade)
    grading_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are a Strict Admissions Officer for Top Global Universities. "
                    "Grade SOPs conservatively and avoid score inflation. "
                    "Score each criterion from 1-10."
                ),
            ),
            (
                "human",
                (
                    "Evaluate this SOP for admissions quality.\n"
                    "Target university: {university}\n"
                    "Target country: {country}\n\n"
                    "Criteria (exact names required):\n"
                    "1. Academic Fit\n"
                    "2. University Specificity\n"
                    "3. Career Clarity\n"
                    "4. Narrative Flow\n"
                    "5. Language & Tone\n\n"
                    "Return strict JSON only:\n"
                    "{format_instructions}\n\n"
                    "SOP:\n{sop_text}"
                ),
            ),
        ]
    )

    grade, raw_json, model_name = invoke_with_model_fallback(
        prompt=grading_prompt,
        parser=parser,
        variables={
            "sop_text": sop_text,
            "university": university,
            "country": country,
        },
        settings=settings,
        logger=logger,
        request_id=request_id,
    )
    return grade, raw_json, model_name


def save_submission(
    settings: AppSettings, profile: StudentProfile, sop_text: str, grade: SOPGrade, raw_json: str
) -> int:
    timestamp = datetime.now(timezone.utc).isoformat()
    with get_db_connection(settings.db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO submissions (
                timestamp, full_name, university, intake, country,
                sop_text, overall_score, ai_feedback_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                profile.full_name,
                profile.university,
                profile.intake,
                profile.country,
                sop_text,
                grade.overall_score,
                raw_json,
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def render_results(grade: SOPGrade, model_name: str, submission_id: int, raw_json: str) -> None:
    st.success(f"SOP grading complete. Submission ID: {submission_id}")
    st.metric("Overall Score", f"{grade.overall_score:.1f}/10")
    st.caption(f"Model used: `{model_name}`")

    score_by_criteria = {item.name: item.score for item in grade.criteria_breakdown}
    ordered_breakdown = [
        {"Criterion": criterion, "Score": score_by_criteria.get(criterion, 0.0)}
        for criterion in EXPECTED_CRITERIA
    ]
    breakdown_df = pd.DataFrame(ordered_breakdown)

    fig = px.bar(
        breakdown_df,
        x="Score",
        y="Criterion",
        orientation="h",
        range_x=[0, 10],
        title="Criteria Breakdown",
        text="Score",
    )
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

    st.subheader("Detailed Feedback")
    for criterion in grade.criteria_breakdown:
        with st.expander(f"{criterion.name} ({criterion.score:.1f}/10)"):
            st.write(criterion.feedback)

    st.subheader("Summary")
    st.write(grade.summary)
    st.warning("Disclaimer: AI generated. Please review manually.")

    st.download_button(
        label="Download AI Feedback JSON",
        data=raw_json,
        file_name=f"sop_feedback_{submission_id}.json",
        mime="application/json",
    )


def get_sop_text(
    pasted_text: str, uploaded_file, settings: AppSettings
) -> Tuple[str, str]:
    if pasted_text.strip():
        return pasted_text.strip(), "paste"
    if uploaded_file is not None:
        return read_uploaded_file(uploaded_file, settings), "upload"
    return "", "none"


def validate_profile(
    full_name: str, mobile: str, university: str, intake: str, country: str
) -> Tuple[bool, StudentProfile | None, str]:
    full_name_clean = sanitize_text(full_name, max_length=120)
    university_clean = sanitize_text(university, max_length=160)
    intake_clean = sanitize_text(intake, max_length=80)
    country_clean = sanitize_text(country, max_length=80)
    mobile_clean = sanitize_mobile(mobile)

    if not full_name_clean:
        return False, None, "Full Name is required."
    if not mobile_clean:
        return False, None, "Mobile must be 10 to 15 digits."
    if not university_clean:
        return False, None, "Target University is required."
    if not intake_clean:
        return False, None, "Intake is required."
    if not country_clean:
        return False, None, "Country is required."

    profile = StudentProfile(
        full_name=full_name_clean,
        mobile=mobile_clean,
        university=university_clean,
        intake=intake_clean,
        country=country_clean,
    )
    return True, profile, ""


def enforce_rate_limit(settings: AppSettings) -> None:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=settings.rate_limit_window_minutes)
    key = "sop_request_timestamps"
    history = st.session_state.get(key, [])

    pruned_history = []
    for item in history:
        try:
            ts = datetime.fromisoformat(item)
            if ts >= cutoff:
                pruned_history.append(item)
        except ValueError:
            continue

    if len(pruned_history) >= settings.max_requests_per_window:
        raise ValueError(
            "Rate limit reached for this session. Please wait before retrying."
        )

    pruned_history.append(now.isoformat())
    st.session_state[key] = pruned_history


def display_sidebar_health(settings: AppSettings) -> None:
    api_key_present = bool(os.getenv("GOOGLE_API_KEY"))
    st.caption(f"Environment: `{settings.app_env}`")
    st.caption(f"DB Path: `{settings.db_path}`")
    st.caption(f"API Key Loaded: `{'yes' if api_key_present else 'no'}`")
    st.caption("Model Order: `" + " -> ".join(settings.model_candidates) + "`")


def safe_user_error(
    exception: Exception, logger: logging.Logger, request_id: str, settings: AppSettings
) -> None:
    logger.exception("[%s] Unhandled error", request_id, exc_info=exception)
    st.error(f"Something went wrong. Error ID: `{request_id}`")
    if settings.app_env in {"dev", "local"}:
        st.exception(exception)


def main() -> None:
    load_dotenv()
    settings = load_settings()
    logger = setup_logger()
    init_db(settings)

    st.set_page_config(
        page_title="SOP Review & Grader",
        page_icon=":mortar_board:",
        layout="wide",
    )
    st.title("SOP Review & Grader")
    st.caption("Designed for Indian students applying for Master's programs abroad.")
    university_catalog = load_university_catalog()
    university_lookup = build_university_lookup(university_catalog)

    with st.sidebar:
        st.header("Applicant Details")
        full_name = st.text_input("Full Name *", max_chars=120)
        mobile = st.text_input("Mobile *", max_chars=20)
        if university_lookup:
            university_options = [UNIVERSITY_PLACEHOLDER] + sorted(
                university_lookup.keys()
            )
            selected_university = st.selectbox(
                "Target University *", options=university_options, index=0
            )

            selected_university_info = (
                university_lookup.get(selected_university)
                if selected_university != UNIVERSITY_PLACEHOLDER
                else None
            )
            university = (
                selected_university
                if selected_university_info is not None
                else ""
            )
            country = (
                selected_university_info["country"]
                if selected_university_info is not None
                else ""
            )

            intake_options = (
                [INTAKE_PLACEHOLDER] + selected_university_info["intakes"]
                if selected_university_info is not None
                else [INTAKE_PLACEHOLDER]
            )
            selected_intake = st.selectbox(
                "Intake *",
                options=intake_options,
                index=0,
                disabled=selected_university_info is None,
            )
            intake = selected_intake if selected_intake != INTAKE_PLACEHOLDER else ""

            st.text_input("Country *", value=country, disabled=True)
        else:
            st.warning(
                "University catalog is unavailable. Falling back to manual input fields."
            )
            university = st.text_input("Target University *", max_chars=160)
            intake = st.text_input("Intake *", max_chars=80)
            country = st.text_input("Country *", max_chars=80)
        st.divider()
        display_sidebar_health(settings)

    tab_paste, tab_upload = st.tabs(["Paste Text", "Upload File"])
    with tab_paste:
        pasted_text = st.text_area(
            "Paste your SOP text here",
            height=360,
            placeholder="Paste complete SOP text...",
            max_chars=settings.max_sop_chars,
        )

    with tab_upload:
        uploaded_file = st.file_uploader(
            f"Upload SOP file (.pdf, .docx, .txt) up to {settings.max_upload_mb} MB",
            type=["pdf", "docx", "txt"],
        )
        if uploaded_file:
            st.info(f"Selected file: `{uploaded_file.name}`")

    if st.button("Review & Grade SOP", type="primary", use_container_width=True):
        request_id = uuid4().hex[:10]
        logger.info("[%s] Request accepted", request_id)

        profile_ok, profile, profile_error = validate_profile(
            full_name=full_name,
            mobile=mobile,
            university=university,
            intake=intake,
            country=country,
        )
        if not profile_ok:
            st.error(profile_error)
            st.stop()

        try:
            enforce_rate_limit(settings)
        except Exception as exc:  # noqa: BLE001
            st.error(str(exc))
            st.stop()

        with st.status("Running SOP pipeline...", expanded=True) as status:
            try:
                status.write("Reading file...")
                sop_text, source = get_sop_text(pasted_text, uploaded_file, settings)
                if not sop_text.strip():
                    raise ValueError(
                        "Provide SOP text using either 'Paste Text' or 'Upload File'."
                    )
                if len(sop_text) > settings.max_sop_chars:
                    raise ValueError(
                        f"SOP text is too long. Maximum allowed length is {settings.max_sop_chars} characters."
                    )
                if source == "upload":
                    status.write("File text extracted successfully.")

                status.write("Verifying content...")
                gatekeeper_result, gate_model = run_gatekeeper(
                    sop_text=sop_text,
                    settings=settings,
                    logger=logger,
                    request_id=request_id,
                )
                status.write(f"Gatekeeper model: {gate_model}")
                if not gatekeeper_result.is_valid:
                    logger.info(
                        "[%s] Gatekeeper rejected SOP: %s",
                        request_id,
                        gatekeeper_result.reason,
                    )
                    status.update(label="SOP rejected by gatekeeper", state="error")
                    st.error(f"Invalid SOP submission: {gatekeeper_result.reason}")
                    st.stop()

                status.write("Grading...")
                grade, raw_json, model_used = run_grader(
                    sop_text=sop_text,
                    university=profile.university,
                    country=profile.country,
                    settings=settings,
                    logger=logger,
                    request_id=request_id,
                )

                status.write("Saving to database...")
                submission_id = save_submission(
                    settings=settings,
                    profile=profile,
                    sop_text=sop_text,
                    grade=grade,
                    raw_json=raw_json,
                )
                logger.info(
                    "[%s] Saved submission id=%s score=%.2f",
                    request_id,
                    submission_id,
                    grade.overall_score,
                )
                status.update(label="Completed", state="complete")

            except ValidationError as exc:
                status.update(label="Parsing error", state="error")
                safe_user_error(exc, logger, request_id, settings)
                st.stop()
            except Exception as exc:  # noqa: BLE001
                status.update(label="Execution failed", state="error")
                safe_user_error(exc, logger, request_id, settings)
                st.stop()

        render_results(
            grade=grade,
            model_name=model_used,
            submission_id=submission_id,
            raw_json=raw_json,
        )


if __name__ == "__main__":
    main()
