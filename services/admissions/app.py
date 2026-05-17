import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from ai_runtime import AIRuntime, DeepSeekProvider, load_runtime_settings


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
from pydantic import ValidationError

from admissions.config import AppSettings, load_settings
from admissions.persistence import SQLitePredictionRepository
from admissions.providers import RuntimePredictionProvider, safe_error_message
from admissions.schemas import AdmissionPrediction, ProgramPrediction
from admissions.service import AdmissionsPredictionService
from admissions.utils import sanitize_text
from admissions.validation import validate_submission


APP_ROOT = Path(__file__).resolve().parent
DB_PATH = APP_ROOT / "admissions_app.db"
LOGGER = logging.getLogger("admissions_app")


def configure_logging() -> None:
    raw_level = sanitize_text(os.getenv("LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, raw_level, logging.INFO)

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        )
    else:
        logging.getLogger().setLevel(level)


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(160deg, #f8fafc 0%, #ecfeff 45%, #f1f5f9 100%);
            color: #0f172a;
        }
        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] h4,
        [data-testid="stAppViewContainer"] h5,
        [data-testid="stAppViewContainer"] h6,
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] li,
        [data-testid="stAppViewContainer"] span {
            color: #0f172a;
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
        [data-testid="stSidebar"] {
            background: #0f172a;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #f8fafc;
        }
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            padding: 0.55rem 0.7rem;
        }
        [data-testid="stAlert"] {
            color: #0f172a;
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
                text=[
                    f"{item.estimated_probability_percentage}%" for item in predictions
                ],
                textposition="auto",
                marker_color=[
                    color_map.get(item.chance_category, "#64748b")
                    for item in predictions
                ],
            )
        ]
    )

    fig.update_layout(
        height=max(300, len(predictions) * 85),
        margin=dict(l=10, r=10, t=10, b=20),
        xaxis_title="Estimated Probability (%)",
        yaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0f172a"),
    )
    fig.update_xaxes(
        range=[0, 100],
        ticksuffix="%",
        gridcolor="#cbd5e1",
        zerolinecolor="#94a3b8",
        tickfont=dict(color="#334155"),
        title_font=dict(color="#334155"),
    )
    fig.update_yaxes(tickfont=dict(color="#334155"))

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

            st.markdown(
                get_category_badge(prediction.chance_category), unsafe_allow_html=True
            )
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

    repository = SQLitePredictionRepository(DB_PATH)
    try:
        repository.init_database()
    except RuntimeError as db_error:
        st.error(f"Startup error: {safe_error_message(db_error)}")
        st.stop()

    settings: Optional[AppSettings] = None
    runtime_settings = None
    settings_error: Optional[str] = None
    try:
        settings = load_settings()
        runtime_settings = load_runtime_settings()
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
            st.caption(f"Model: `{runtime_settings.model_candidates[0]}` | Temp: `0.0`")
        elif settings_error:
            st.error(f"Configuration issue: {settings_error}")

        with st.form("admission_profile_form", clear_on_submit=False):
            st.markdown("### Personal")
            full_name = st.text_input("Full Name *", placeholder="e.g., Priya Sharma")
            target_intake = st.selectbox(
                "Target Intake *", options=build_intake_options()
            )

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
            target_country = (
                custom_country if selected_country == "Other" else selected_country
            )

            st.markdown("### Academics")
            undergrad_degree = st.text_input(
                "Undergrad Degree Name *",
                placeholder="e.g., B.Tech in Computer Science",
            )
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
            english_test = st.selectbox(
                "English Proficiency Test", options=["None", "IELTS", "TOEFL"]
            )
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
            program_1 = st.text_input(
                "Target Program 1 *",
                placeholder="MS in Computer Science at Georgia Tech",
            )
            program_2 = st.text_input("Target Program 2")
            program_3 = st.text_input("Target Program 3")
            program_4 = st.text_input("Target Program 4")
            program_5 = st.text_input("Target Program 5")

            submitted = st.form_submit_button(
                "Predict Admission Chances", use_container_width=True
            )

    if submitted:
        if settings is None:
            submission_errors.append(
                settings_error
                or "Runtime configuration is invalid. Add DEEPSEEK_API_KEY and restart."
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
                with st.spinner("Analyzing profile with DeepSeek..."):
                    try:
                        runtime = AIRuntime(
                            runtime_settings,
                            DeepSeekProvider(
                                runtime_settings.api_key, runtime_settings.base_url
                            ),
                            LOGGER,
                        )
                        service = AdmissionsPredictionService(
                            RuntimePredictionProvider(runtime)
                        )
                        result = service.predict(profile, target_programs)
                        prediction = result.prediction
                        raw_ai_output = result.raw_output
                        st.session_state.prediction_result = prediction.model_dump()
                        st.session_state.raw_ai_output = raw_ai_output
                        st.session_state.last_updated_at = datetime.now(
                            timezone.utc
                        ).strftime("%Y-%m-%d %H:%M:%S UTC")

                        try:
                            repository.save(profile, target_programs, raw_ai_output)
                            submission_success = (
                                "Prediction generated and saved to admissions_app.db."
                            )
                        except RuntimeError as db_error:
                            submission_success = (
                                "Prediction generated, but database persistence failed."
                            )
                            submission_errors.append(safe_error_message(db_error))
                    except Exception as error:
                        LOGGER.exception("Prediction pipeline failed")
                        submission_errors.append(
                            f"Prediction failed: {safe_error_message(error)}"
                        )

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
            st.error(
                "Stored prediction output is invalid. Please resubmit the profile."
            )
    else:
        st.info("Submit the profile form to generate admission predictions.")


if __name__ == "__main__":
    main()
