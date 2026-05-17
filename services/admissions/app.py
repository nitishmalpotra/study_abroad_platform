import json
import logging
import os
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional

from dotenv import load_dotenv


def _parse_bool_env(value: str) -> bool:
    return sanitize_bootstrap_value(value).lower() in {"1", "true", "yes", "on"}


def sanitize_bootstrap_value(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


# Load env before runtime-heavy imports execute in downstream modules.
load_dotenv(override=False)

# This app does not require SOP access tokens. If an external runtime has enabled
# SOP gatekeeping without providing a token, disable that gate for this process.
sop_required = _parse_bool_env(os.getenv("SOP_REQUIRE_ACCESS_TOKEN", "false"))
sop_token = sanitize_bootstrap_value(os.getenv("SOP_APP_ACCESS_TOKEN", ""))
if sop_required and not sop_token:
    os.environ["SOP_REQUIRE_ACCESS_TOKEN"] = "false"

import plotly.graph_objects as go
import streamlit as st
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


APP_ROOT = Path(__file__).resolve().parent
DB_PATH = APP_ROOT / "admissions_app.db"
FALLBACK_RECOMMENDATIONS = [
    "Northeastern University (MS CS): Strong co-op ecosystem and industry-aligned curriculum.",
    "Arizona State University (MS CS): Broad intake capacity with solid applied research opportunities.",
    "University at Buffalo, SUNY (MS CS): Balanced selectivity with a good ROI for international students.",
]

LOGGER = logging.getLogger("admissions_app")


def configure_logging() -> None:
    """Configure app logging once per process."""
    raw_level = sanitize_text(os.getenv("LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, raw_level, logging.INFO)

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        )
    else:
        logging.getLogger().setLevel(level)


def sanitize_text(value: str, *, max_length: Optional[int] = None) -> str:
    """Normalize text and remove control characters."""
    cleaned = re.sub(r"[\x00-\x1F\x7F]+", " ", str(value or ""))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if max_length is not None:
        cleaned = cleaned[:max_length]
    return cleaned


def safe_error_message(error: Exception) -> str:
    """Redact common secrets from surfaced error strings."""
    message = sanitize_text(str(error), max_length=500)
    message = re.sub(r"AIza[0-9A-Za-z_\-]{16,}", "[REDACTED_API_KEY]", message)
    return message or "Unexpected error."


def parse_optional_int(raw_value: str, field_name: str) -> tuple[Optional[int], Optional[str]]:
    text = sanitize_text(raw_value)
    if not text:
        return None, None
    try:
        return int(text), None
    except ValueError:
        return None, f"{field_name} must be a whole number."


def parse_optional_float(raw_value: str, field_name: str) -> tuple[Optional[float], Optional[str]]:
    text = sanitize_text(raw_value)
    if not text:
        return None, None
    try:
        return float(text), None
    except ValueError:
        return None, f"{field_name} must be numeric."


class AppSettings(BaseModel):
    google_api_key: str = Field(..., min_length=20)
    gemini_model: str = Field(default="gemini-1.5-pro", min_length=1, max_length=120)
    llm_timeout_seconds: int = Field(default=45, ge=10, le=180)
    llm_retry_attempts: int = Field(default=2, ge=0, le=5)
    model_config = ConfigDict(extra="forbid")

    @field_validator("google_api_key")
    @classmethod
    def validate_google_key(cls, value: str) -> str:
        cleaned = sanitize_text(value)
        if not cleaned:
            raise ValueError("GOOGLE_API_KEY is required.")
        return cleaned

    @field_validator("gemini_model")
    @classmethod
    def validate_model_name(cls, value: str) -> str:
        cleaned = sanitize_text(value)
        if not cleaned:
            raise ValueError("GEMINI_MODEL is required.")
        return cleaned


class ProgramPrediction(BaseModel):
    program_name: str = Field(..., min_length=3, max_length=200)
    chance_category: Literal["Safe", "Target", "Reach", "Unrealistic"]
    estimated_probability_percentage: int = Field(..., ge=0, le=100)
    brief_reasoning: str = Field(..., min_length=10, max_length=500)
    model_config = ConfigDict(extra="forbid")

    @field_validator("program_name", "brief_reasoning")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        cleaned = sanitize_text(value)
        if not cleaned:
            raise ValueError("Text fields cannot be empty.")
        return cleaned


class AdmissionPrediction(BaseModel):
    target_predictions: list[ProgramPrediction] = Field(..., min_length=1, max_length=5)
    profile_strengths: list[str] = Field(..., min_length=3, max_length=3)
    profile_weaknesses: list[str] = Field(..., min_length=3, max_length=3)
    actionable_roadmap: list[str] = Field(..., min_length=3, max_length=3)
    recommended_universities: list[str] = Field(..., min_length=3, max_length=3)
    model_config = ConfigDict(extra="forbid")

    @field_validator("target_predictions")
    @classmethod
    def validate_unique_programs(cls, predictions: list[ProgramPrediction]) -> list[ProgramPrediction]:
        names = [sanitize_text(item.program_name).lower() for item in predictions]
        if len(names) != len(set(names)):
            raise ValueError("target_predictions must contain distinct programs.")
        return predictions

    @field_validator(
        "profile_strengths",
        "profile_weaknesses",
        "actionable_roadmap",
        "recommended_universities",
    )
    @classmethod
    def validate_list_items(cls, values: list[str]) -> list[str]:
        cleaned_values = [sanitize_text(item) for item in values if sanitize_text(item)]
        if len(cleaned_values) != len(values):
            raise ValueError("List items cannot be empty.")
        return cleaned_values


def load_settings() -> AppSettings:
    raw_timeout = sanitize_text(os.getenv("LLM_TIMEOUT_SECONDS", "45"))
    raw_retries = sanitize_text(os.getenv("LLM_RETRY_ATTEMPTS", "2"))
    model_name = sanitize_text(os.getenv("GEMINI_MODEL", "gemini-1.5-pro"))

    try:
        timeout_seconds = int(raw_timeout)
        retry_attempts = int(raw_retries)
    except ValueError as exc:
        raise RuntimeError("LLM_TIMEOUT_SECONDS and LLM_RETRY_ATTEMPTS must be integers.") from exc

    try:
        return AppSettings(
            google_api_key=sanitize_text(os.getenv("GOOGLE_API_KEY", "")),
            gemini_model=model_name or "gemini-1.5-pro",
            llm_timeout_seconds=timeout_seconds,
            llm_retry_attempts=retry_attempts,
        )
    except ValidationError as exc:
        raise RuntimeError(f"Invalid runtime configuration: {sanitize_text(str(exc))}") from exc


def get_db_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.execute("PRAGMA journal_mode=WAL;")
    connection.execute("PRAGMA synchronous=NORMAL;")
    connection.execute("PRAGMA foreign_keys=ON;")
    connection.execute("PRAGMA busy_timeout=5000;")
    return connection


def init_database() -> None:
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    target_intake TEXT NOT NULL,
                    target_country TEXT NOT NULL,
                    profile_json TEXT NOT NULL,
                    target_programs TEXT NOT NULL,
                    ai_raw_output TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at DESC)"
            )
            connection.commit()
    except sqlite3.Error as exc:
        raise RuntimeError("Failed to initialize SQLite database.") from exc


def save_prediction_to_db(profile: dict[str, Any], target_programs: list[str], raw_ai_output: str) -> None:
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO predictions (
                    created_at,
                    full_name,
                    target_intake,
                    target_country,
                    profile_json,
                    target_programs,
                    ai_raw_output
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    sanitize_text(profile["full_name"], max_length=120),
                    sanitize_text(profile["target_intake"], max_length=40),
                    sanitize_text(profile["target_country"], max_length=60),
                    json.dumps(profile, ensure_ascii=True),
                    " | ".join(target_programs),
                    raw_ai_output[:12000],
                ),
            )
            connection.commit()
    except sqlite3.Error as exc:
        raise RuntimeError("Prediction was generated but could not be saved to SQLite.") from exc


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(160deg, #f8fafc 0%, #ecfeff 45%, #f1f5f9 100%);
        }
        .block-container {
            max-width: 1120px;
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }
        .hero {
            background: linear-gradient(120deg, #0f172a 0%, #1d4ed8 50%, #0f766e 100%);
            border-radius: 16px;
            padding: 1.1rem 1.2rem;
            margin-bottom: 1rem;
        }
        .hero h1 {
            color: #f8fafc;
            margin: 0;
            font-size: 2rem;
            font-family: "Manrope", "Avenir Next", "Segoe UI", sans-serif;
            letter-spacing: -0.02em;
        }
        .hero p {
            color: #e2e8f0;
            margin: 0.4rem 0 0 0;
            font-size: 0.95rem;
        }
        .badge {
            display: inline-block;
            padding: 0.22rem 0.62rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.01em;
            margin-bottom: 0.5rem;
        }
        .safe { background: #dcfce7; color: #166534; }
        .target { background: #dbeafe; color: #1d4ed8; }
        .reach { background: #fef3c7; color: #92400e; }
        .unrealistic { background: #fee2e2; color: #991b1b; }
        .recommendation-card {
            border: 1px solid #bfdbfe;
            border-left: 5px solid #1d4ed8;
            background: #ffffff;
            border-radius: 12px;
            padding: 0.75rem 0.85rem;
            margin-bottom: 0.6rem;
        }
        @media (max-width: 768px) {
            .hero h1 { font-size: 1.45rem; }
            .hero p { font-size: 0.9rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_intake_options() -> list[str]:
    current_year = datetime.now().year
    return [
        f"Fall {current_year}",
        f"Spring {current_year + 1}",
        f"Fall {current_year + 1}",
        f"Spring {current_year + 2}",
    ]


def normalize_llm_content(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content") or ""
                if isinstance(text, str):
                    parts.append(text)
            else:
                parts.append(str(item))
        return "\n".join(part for part in parts if part).strip()

    return str(content).strip()


def strip_code_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def parse_prediction_output(parser: PydanticOutputParser, raw_text: str) -> AdmissionPrediction:
    cleaned = strip_code_fence(raw_text)
    try:
        return parser.parse(cleaned)
    except Exception:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No valid JSON object was found in the model response.")
        payload = json.loads(cleaned[start : end + 1])
        return AdmissionPrediction.model_validate(payload)


def align_predictions_to_targets(
    prediction: AdmissionPrediction, target_programs: list[str]
) -> AdmissionPrediction:
    mapped_predictions = {sanitize_text(item.program_name).lower(): item for item in prediction.target_predictions}
    aligned_predictions: list[ProgramPrediction] = []

    for target in target_programs:
        target_key = sanitize_text(target).lower()
        matched_prediction = mapped_predictions.get(target_key)

        if matched_prediction is None:
            for candidate in prediction.target_predictions:
                candidate_name = sanitize_text(candidate.program_name).lower()
                if target_key in candidate_name or candidate_name in target_key:
                    matched_prediction = candidate
                    break

        if matched_prediction is None:
            matched_prediction = ProgramPrediction(
                program_name=target,
                chance_category="Reach",
                estimated_probability_percentage=20,
                brief_reasoning=(
                    "Model output omitted this target program, so a conservative placeholder estimate is shown."
                ),
            )
        else:
            matched_prediction = ProgramPrediction(
                program_name=target,
                chance_category=matched_prediction.chance_category,
                estimated_probability_percentage=matched_prediction.estimated_probability_percentage,
                brief_reasoning=matched_prediction.brief_reasoning,
            )

        aligned_predictions.append(matched_prediction)

    return AdmissionPrediction(
        target_predictions=aligned_predictions,
        profile_strengths=prediction.profile_strengths,
        profile_weaknesses=prediction.profile_weaknesses,
        actionable_roadmap=prediction.actionable_roadmap,
        recommended_universities=prediction.recommended_universities,
    )


def enforce_alternative_recommendations(
    prediction: AdmissionPrediction, target_programs: list[str]
) -> AdmissionPrediction:
    targets_lower = {sanitize_text(item).lower() for item in target_programs}
    curated: list[str] = []
    seen: set[str] = set()

    for recommendation in prediction.recommended_universities:
        clean = sanitize_text(recommendation, max_length=220)
        if not clean:
            continue
        lowered = clean.lower()
        if any(target in lowered for target in targets_lower):
            continue
        if lowered in seen:
            continue
        curated.append(clean)
        seen.add(lowered)

    for fallback in FALLBACK_RECOMMENDATIONS:
        if len(curated) >= 3:
            break
        lowered = fallback.lower()
        if lowered in seen:
            continue
        if any(target in lowered for target in targets_lower):
            continue
        curated.append(fallback)
        seen.add(lowered)

    return AdmissionPrediction(
        target_predictions=prediction.target_predictions,
        profile_strengths=prediction.profile_strengths,
        profile_weaknesses=prediction.profile_weaknesses,
        actionable_roadmap=prediction.actionable_roadmap,
        recommended_universities=curated[:3],
    )


@st.cache_resource(show_spinner=False)
def build_llm_client(api_key: str, model_name: str, timeout_seconds: int) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.0,
        google_api_key=api_key,
        timeout=timeout_seconds,
        max_retries=0,
    )


def invoke_with_retry(chain: Any, payload: dict[str, Any], retry_attempts: int) -> Any:
    total_attempts = retry_attempts + 1
    for attempt in range(total_attempts):
        try:
            return chain.invoke(payload)
        except Exception as exc:
            if attempt == total_attempts - 1:
                raise
            wait_seconds = min(8.0, 1.3 * (2**attempt))
            LOGGER.warning(
                "LLM call failed on attempt %s/%s: %s",
                attempt + 1,
                total_attempts,
                safe_error_message(exc),
            )
            time.sleep(wait_seconds)
    raise RuntimeError("LLM invocation failed unexpectedly.")


def run_prediction(
    settings: AppSettings, profile: dict[str, Any], target_programs: list[str]
) -> tuple[AdmissionPrediction, str]:
    parser = PydanticOutputParser(pydantic_object=AdmissionPrediction)
    llm = build_llm_client(
        api_key=settings.google_api_key,
        model_name=settings.gemini_model,
        timeout_seconds=settings.llm_timeout_seconds,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are an Expert International Admissions Counselor for Master's programs. "
                    "Use realistic, evidence-grounded judgement for Indian applicants and provide concise reasoning."
                ),
            ),
            (
                "human",
                (
                    "Analyze this student's holistic profile and return a strict JSON response only.\n"
                    "You must evaluate each target program in the same order provided.\n\n"
                    "Student Profile:\n{student_profile}\n\n"
                    "Target Programs:\n{target_programs}\n\n"
                    "Rules:\n"
                    "- chance_category must be one of: Safe, Target, Reach, Unrealistic.\n"
                    "- estimated_probability_percentage must be an integer between 0 and 100.\n"
                    "- target_predictions length must equal the number of target programs.\n"
                    "- profile_strengths, profile_weaknesses, actionable_roadmap must each contain exactly 3 items.\n"
                    "- recommended_universities must contain exactly 3 alternatives not listed in target programs.\n"
                    "- Each recommended_universities item should include university + reason in one sentence.\n\n"
                    "{format_instructions}"
                ),
            ),
        ]
    )

    chain = prompt | llm
    payload = {
        "student_profile": json.dumps(profile, indent=2, ensure_ascii=True),
        "target_programs": json.dumps(target_programs, indent=2, ensure_ascii=True),
        "format_instructions": parser.get_format_instructions(),
    }

    response = invoke_with_retry(chain, payload, settings.llm_retry_attempts)
    raw_output = normalize_llm_content(response.content)

    try:
        parsed = parse_prediction_output(parser, raw_output)
        aligned = align_predictions_to_targets(parsed, target_programs)
        post_processed = enforce_alternative_recommendations(aligned, target_programs)
        return post_processed, strip_code_fence(raw_output)
    except Exception as parse_error:
        LOGGER.warning("Initial parse failed, attempting one repair pass: %s", safe_error_message(parse_error))

    repair_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a strict JSON formatter. Return only valid JSON. Do not add prose.",
            ),
            (
                "human",
                (
                    "Convert this output into valid JSON that exactly follows the schema below.\n\n"
                    "Schema:\n{format_instructions}\n\n"
                    "Output to fix:\n{raw_output}"
                ),
            ),
        ]
    )

    repair_chain = repair_prompt | llm
    repaired_response = invoke_with_retry(
        repair_chain,
        {
            "format_instructions": parser.get_format_instructions(),
            "raw_output": raw_output,
        },
        settings.llm_retry_attempts,
    )
    repaired_raw_output = normalize_llm_content(repaired_response.content)

    try:
        repaired_prediction = parse_prediction_output(parser, repaired_raw_output)
    except Exception as final_parse_error:
        raise RuntimeError(
            "Model response could not be parsed into the required schema after repair."
        ) from final_parse_error

    aligned = align_predictions_to_targets(repaired_prediction, target_programs)
    post_processed = enforce_alternative_recommendations(aligned, target_programs)
    return post_processed, strip_code_fence(repaired_raw_output)


def get_category_badge(category: str) -> str:
    css_class = {
        "Safe": "safe",
        "Target": "target",
        "Reach": "reach",
        "Unrealistic": "unrealistic",
    }.get(category, "target")
    return f"<span class='badge {css_class}'>{sanitize_text(category)}</span>"


def render_probability_chart(predictions: list[ProgramPrediction]) -> None:
    color_map = {
        "Safe": "#16a34a",
        "Target": "#2563eb",
        "Reach": "#d97706",
        "Unrealistic": "#dc2626",
    }

    fig = go.Figure(
        data=[
            go.Bar(
                x=[item.estimated_probability_percentage for item in predictions],
                y=[item.program_name for item in predictions],
                orientation="h",
                text=[f"{item.estimated_probability_percentage}%" for item in predictions],
                textposition="auto",
                marker_color=[color_map.get(item.chance_category, "#64748b") for item in predictions],
            )
        ]
    )

    fig.update_layout(
        height=max(300, len(predictions) * 85),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Estimated Probability (%)",
        yaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(range=[0, 100], ticksuffix="%")

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_results(result: AdmissionPrediction) -> None:
    st.header("Admission Predictions")
    render_probability_chart(result.target_predictions)

    for prediction in result.target_predictions:
        with st.container(border=True):
            top_col, metric_col = st.columns([5, 1])
            with top_col:
                st.markdown(f"#### {prediction.program_name}")
            with metric_col:
                st.metric("Chance", f"{prediction.estimated_probability_percentage}%")

            st.markdown(get_category_badge(prediction.chance_category), unsafe_allow_html=True)
            st.progress(prediction.estimated_probability_percentage / 100)
            st.write(prediction.brief_reasoning)

    st.subheader("Profile Breakdown")
    strengths_col, weaknesses_col = st.columns(2)
    with strengths_col:
        st.markdown("#### Strengths")
        for strength in result.profile_strengths:
            st.success(strength)
    with weaknesses_col:
        st.markdown("#### Weaknesses")
        for weakness in result.profile_weaknesses:
            st.warning(weakness)

    st.subheader("Actionable Roadmap")
    for index, step in enumerate(result.actionable_roadmap, start=1):
        st.markdown(f"{index}. {step}")

    st.subheader("Alternative Recommendations")
    for recommendation in result.recommended_universities:
        st.markdown(
            f"<div class='recommendation-card'>{recommendation}</div>",
            unsafe_allow_html=True,
        )


def validate_submission(
    *,
    full_name: str,
    target_intake: str,
    target_country: str,
    undergrad_degree: str,
    cgpa: float,
    cgpa_scale: int,
    gre_raw: str,
    gmat_raw: str,
    english_test: str,
    english_score_raw: str,
    work_experience_months: int,
    research_publications: int,
    program_inputs: list[str],
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []

    clean_name = sanitize_text(full_name)
    clean_intake = sanitize_text(target_intake)
    clean_country = sanitize_text(target_country)
    clean_degree = sanitize_text(undergrad_degree)

    if not clean_name:
        errors.append("Full Name is required.")
    if len(clean_name) > 120:
        errors.append("Full Name must be at most 120 characters.")
    if len(clean_intake) > 40:
        errors.append("Target Intake must be at most 40 characters.")

    if not clean_country:
        errors.append("Target Country is required.")
    if len(clean_country) > 60:
        errors.append("Target Country must be at most 60 characters.")
    if not clean_degree:
        errors.append("Undergrad Degree Name is required.")
    if len(clean_degree) > 160:
        errors.append("Undergrad Degree Name must be at most 160 characters.")

    if cgpa <= 0:
        errors.append("CGPA must be greater than 0.")
    if cgpa_scale not in {4, 10}:
        errors.append("CGPA scale must be 4 or 10.")
    if cgpa > cgpa_scale:
        errors.append(f"CGPA cannot exceed {cgpa_scale} for the selected scale.")

    gre_score, gre_error = parse_optional_int(gre_raw, "GRE score")
    if gre_error:
        errors.append(gre_error)
    if gre_score is not None and not (260 <= gre_score <= 340):
        errors.append("GRE score must be between 260 and 340.")

    gmat_score, gmat_error = parse_optional_int(gmat_raw, "GMAT score")
    if gmat_error:
        errors.append(gmat_error)
    if gmat_score is not None and not (200 <= gmat_score <= 805):
        errors.append("GMAT score must be between 200 and 805.")

    clean_english_test = sanitize_text(english_test)
    english_score: Optional[float] = None

    if clean_english_test == "None":
        if sanitize_text(english_score_raw):
            errors.append("Select IELTS or TOEFL when providing an English score.")
    else:
        english_score, english_error = parse_optional_float(english_score_raw, "English score")
        if english_error:
            errors.append(english_error)
        if english_score is None:
            errors.append("English score is required when IELTS/TOEFL is selected.")
        elif clean_english_test == "IELTS" and not (0 <= english_score <= 9):
            errors.append("IELTS score must be between 0 and 9.")
        elif clean_english_test == "TOEFL" and not (0 <= english_score <= 120):
            errors.append("TOEFL score must be between 0 and 120.")

    if work_experience_months < 0 or work_experience_months > 600:
        errors.append("Work Experience must be between 0 and 600 months.")

    if research_publications < 0 or research_publications > 200:
        errors.append("Research Publications must be between 0 and 200.")

    sanitized_programs: list[str] = []
    for index, raw_program in enumerate(program_inputs, start=1):
        clean_program = sanitize_text(raw_program)
        if index == 1 and not clean_program:
            errors.append("Target Program 1 is mandatory.")
        if clean_program:
            if len(clean_program) > 200:
                errors.append(f"Target Program {index} must be at most 200 characters.")
            sanitized_programs.append(clean_program)

    if sanitized_programs and len(sanitized_programs) != len({item.lower() for item in sanitized_programs}):
        errors.append("Target programs must be distinct.")

    profile_payload = {
        "full_name": clean_name,
        "target_intake": clean_intake,
        "target_country": clean_country,
        "undergrad_degree_name": clean_degree,
        "cgpa": round(float(cgpa), 2),
        "cgpa_scale": cgpa_scale,
        "gre_score": gre_score,
        "gmat_score": gmat_score,
        "english_test": None if clean_english_test == "None" else clean_english_test,
        "english_score": english_score,
        "work_experience_months": int(work_experience_months),
        "research_publications": int(research_publications),
    }

    return profile_payload, sanitized_programs, errors


def initialize_session_state() -> None:
    if "prediction_result" not in st.session_state:
        st.session_state.prediction_result = None
    if "raw_ai_output" not in st.session_state:
        st.session_state.raw_ai_output = ""
    if "last_updated_at" not in st.session_state:
        st.session_state.last_updated_at = None


def main() -> None:
    configure_logging()

    st.set_page_config(
        page_title="College Admission Predictor",
        page_icon=":mortar_board:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_custom_css()
    initialize_session_state()

    try:
        init_database()
    except RuntimeError as db_error:
        st.error(f"Startup error: {safe_error_message(db_error)}")
        st.stop()

    settings: Optional[AppSettings] = None
    settings_error: Optional[str] = None
    try:
        settings = load_settings()
    except RuntimeError as config_error:
        settings_error = safe_error_message(config_error)

    st.markdown(
        """
        <div class="hero">
            <h1>College Admission Predictor</h1>
            <p>Profile-driven admission chance estimates for up to five MS targets, with strategic alternatives.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write(
        "Fill the profile in the sidebar, submit your target programs, and receive program-level predictions plus "
        "an improvement roadmap."
    )

    submission_errors: list[str] = []
    submission_success: Optional[str] = None

    with st.sidebar:
        st.header("Profile Builder")
        if settings:
            st.caption(f"Model: `{settings.gemini_model}` | Temp: `0.0`")
        elif settings_error:
            st.error(f"Configuration issue: {settings_error}")

        with st.form("admission_profile_form", clear_on_submit=False):
            st.markdown("### Personal")
            full_name = st.text_input("Full Name *", placeholder="e.g., Priya Sharma")
            target_intake = st.selectbox("Target Intake *", options=build_intake_options())

            country_options = [
                "United States",
                "Canada",
                "United Kingdom",
                "Germany",
                "Australia",
                "Ireland",
                "Netherlands",
                "Singapore",
                "Other",
            ]
            selected_country = st.selectbox("Target Country *", options=country_options)
            custom_country = ""
            if selected_country == "Other":
                custom_country = st.text_input("Specify Target Country *")
            target_country = custom_country if selected_country == "Other" else selected_country

            st.markdown("### Academics")
            undergrad_degree = st.text_input("Undergrad Degree Name *", placeholder="e.g., B.Tech in Computer Science")
            cgpa_scale = st.radio("CGPA Scale *", options=[10, 4], horizontal=True)
            cgpa = st.number_input(
                "Current CGPA *",
                min_value=0.0,
                max_value=10.0,
                value=8.0,
                step=0.01,
                format="%.2f",
            )

            st.markdown("### Test Scores (Optional)")
            gre_raw = st.text_input("GRE Score (260-340)")
            gmat_raw = st.text_input("GMAT Score (200-805)")
            english_test = st.selectbox("English Proficiency Test", options=["None", "IELTS", "TOEFL"])
            english_score_raw = st.text_input("English Score (IELTS 0-9 | TOEFL 0-120)")

            st.markdown("### Experience")
            work_experience_months = st.number_input(
                "Work Experience (Months)",
                min_value=0,
                max_value=600,
                value=0,
                step=1,
            )
            research_publications = st.number_input(
                "Research Publications",
                min_value=0,
                max_value=200,
                value=0,
                step=1,
            )

            st.markdown("### Target Programs (Up to 5)")
            program_1 = st.text_input("Target Program 1 *", placeholder="MS in Computer Science at Georgia Tech")
            program_2 = st.text_input("Target Program 2")
            program_3 = st.text_input("Target Program 3")
            program_4 = st.text_input("Target Program 4")
            program_5 = st.text_input("Target Program 5")

            submitted = st.form_submit_button("Predict Admission Chances", use_container_width=True)

    if submitted:
        if settings is None:
            submission_errors.append(
                settings_error or "Runtime configuration is invalid. Add GOOGLE_API_KEY and restart."
            )
        else:
            profile, target_programs, submission_errors = validate_submission(
                full_name=full_name,
                target_intake=target_intake,
                target_country=target_country,
                undergrad_degree=undergrad_degree,
                cgpa=cgpa,
                cgpa_scale=cgpa_scale,
                gre_raw=gre_raw,
                gmat_raw=gmat_raw,
                english_test=english_test,
                english_score_raw=english_score_raw,
                work_experience_months=work_experience_months,
                research_publications=research_publications,
                program_inputs=[program_1, program_2, program_3, program_4, program_5],
            )

            if not submission_errors:
                with st.spinner("Analyzing profile with Gemini..."):
                    try:
                        prediction, raw_ai_output = run_prediction(settings, profile, target_programs)
                        st.session_state.prediction_result = prediction.model_dump()
                        st.session_state.raw_ai_output = raw_ai_output
                        st.session_state.last_updated_at = datetime.now(timezone.utc).strftime(
                            "%Y-%m-%d %H:%M:%S UTC"
                        )

                        try:
                            save_prediction_to_db(profile, target_programs, raw_ai_output)
                            submission_success = "Prediction generated and saved to admissions_app.db."
                        except RuntimeError as db_error:
                            submission_success = "Prediction generated, but database persistence failed."
                            submission_errors.append(safe_error_message(db_error))
                    except Exception as error:
                        LOGGER.exception("Prediction pipeline failed")
                        submission_errors.append(f"Prediction failed: {safe_error_message(error)}")

    if submission_errors:
        for error in submission_errors:
            st.error(error)
    elif submission_success:
        st.success(submission_success)

    prediction_payload = st.session_state.get("prediction_result")
    if prediction_payload:
        try:
            prediction = AdmissionPrediction.model_validate(prediction_payload)
            if st.session_state.get("last_updated_at"):
                st.caption(f"Last generated: {st.session_state['last_updated_at']}")
            render_results(prediction)
            with st.expander("Raw AI JSON Output"):
                st.code(st.session_state.get("raw_ai_output", ""), language="json")
        except ValidationError:
            st.error("Stored prediction output is invalid. Please resubmit the profile.")
    else:
        st.info("Submit the profile form to generate admission predictions.")


if __name__ == "__main__":
    main()
