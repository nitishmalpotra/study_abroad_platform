import logging
import os
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler
from uuid import uuid4

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from pydantic import ValidationError

from sop_review.catalog import build_university_lookup, load_university_catalog
from sop_review.config import AppSettings, load_settings
from sop_review.ingestion import extract_text_from_bytes
from sop_review.persistence import SQLiteSubmissionRepository
from sop_review.providers import GeminiReviewProvider
from sop_review.schemas import EXPECTED_CRITERIA, SOPGrade
from sop_review.service import SOPReviewService
from sop_review.validation import validate_profile

UNIVERSITY_PLACEHOLDER = "Select University"
INTAKE_PLACEHOLDER = "Select Intake"


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("sop_app")
    if logger.handlers:
        return logger
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"), maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


@st.cache_data(show_spinner=False)
def cached_university_catalog() -> list[dict]:
    return load_university_catalog()


def read_uploaded_file(uploaded_file, settings: AppSettings) -> str:
    return extract_text_from_bytes(
        uploaded_file.name, uploaded_file.getvalue(), settings.max_upload_mb
    )


def get_sop_text(pasted_text: str, uploaded_file, settings: AppSettings) -> tuple[str, str]:
    if pasted_text.strip():
        return pasted_text.strip(), "paste"
    if uploaded_file is not None:
        return read_uploaded_file(uploaded_file, settings), "upload"
    return "", "none"


def render_results(grade: SOPGrade, model_name: str, submission_id: int, raw_json: str) -> None:
    st.success(f"SOP grading complete. Submission ID: {submission_id}")
    st.metric("Overall Score", f"{grade.overall_score:.1f}/10")
    st.caption(f"Model used: `{model_name}`")

    score_by_criteria = {item.name: item.score for item in grade.criteria_breakdown}
    breakdown_df = pd.DataFrame(
        [
            {"Criterion": criterion, "Score": score_by_criteria.get(criterion, 0.0)}
            for criterion in EXPECTED_CRITERIA
        ]
    )
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


def enforce_rate_limit(settings: AppSettings) -> None:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=settings.rate_limit_window_minutes)
    key = "sop_request_timestamps"
    history = st.session_state.get(key, [])
    pruned_history = []
    for item in history:
        try:
            if datetime.fromisoformat(item) >= cutoff:
                pruned_history.append(item)
        except ValueError:
            continue
    if len(pruned_history) >= settings.max_requests_per_window:
        raise ValueError("Rate limit reached for this session. Please wait before retrying.")
    pruned_history.append(now.isoformat())
    st.session_state[key] = pruned_history


def display_sidebar_health(settings: AppSettings) -> None:
    st.caption(f"Environment: `{settings.app_env}`")
    st.caption(f"DB Path: `{settings.db_path}`")
    st.caption(f"API Key Loaded: `{'yes' if os.getenv('GOOGLE_API_KEY') else 'no'}`")
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
    repository = SQLiteSubmissionRepository(settings)
    repository.init_db()
    service = SOPReviewService(settings, GeminiReviewProvider(settings, logger), repository)

    st.set_page_config(page_title="SOP Review & Grader", page_icon=":mortar_board:", layout="wide")
    st.title("SOP Review & Grader")
    st.caption("Designed for Indian students applying for Master's programs abroad.")
    university_lookup = build_university_lookup(cached_university_catalog())

    with st.sidebar:
        st.header("Applicant Details")
        full_name = st.text_input("Full Name *", max_chars=120)
        mobile = st.text_input("Mobile *", max_chars=20)
        if university_lookup:
            selected_university = st.selectbox(
                "Target University *", options=[UNIVERSITY_PLACEHOLDER] + sorted(university_lookup), index=0
            )
            selected_info = university_lookup.get(selected_university) if selected_university != UNIVERSITY_PLACEHOLDER else None
            university = selected_university if selected_info is not None else ""
            country = selected_info["country"] if selected_info is not None else ""
            selected_intake = st.selectbox(
                "Intake *",
                options=([INTAKE_PLACEHOLDER] + selected_info["intakes"]) if selected_info else [INTAKE_PLACEHOLDER],
                index=0,
                disabled=selected_info is None,
            )
            intake = selected_intake if selected_intake != INTAKE_PLACEHOLDER else ""
            st.text_input("Country *", value=country, disabled=True)
        else:
            st.warning("University catalog is unavailable. Falling back to manual input fields.")
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
        profile_ok, profile, profile_error = validate_profile(full_name, mobile, university, intake, country)
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
                if source == "upload":
                    status.write("File text extracted successfully.")
                status.write("Verifying content...")
                result = service.review(profile, sop_text, request_id)
                status.write(f"Gatekeeper model: {result.gatekeeper_model}")
                if not result.gatekeeper.is_valid:
                    logger.info("[%s] Gatekeeper rejected SOP: %s", request_id, result.gatekeeper.reason)
                    status.update(label="SOP rejected by gatekeeper", state="error")
                    st.error(f"Invalid SOP submission: {result.gatekeeper.reason}")
                    st.stop()
                status.write("Grading...")
                logger.info(
                    "[%s] Saved submission id=%s score=%.2f",
                    request_id,
                    result.submission_id,
                    result.grade.overall_score,
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
        render_results(result.grade, result.grading_model, result.submission_id, result.raw_json)


if __name__ == "__main__":
    main()
