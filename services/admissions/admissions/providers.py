import json
import logging

from ai_runtime import AIRuntime, parse_model_json, redact_secrets, schema_instructions

from .prompts import prediction_messages, repair_messages
from .schemas import AdmissionPrediction, StudentProfile
from .utils import sanitize_text


LOGGER = logging.getLogger("admissions_app")


def safe_error_message(error: Exception) -> str:
    return sanitize_text(redact_secrets(error), max_length=500) or "Unexpected error."


def _render_messages(
    templates: list[tuple[str, str]], variables: dict[str, str]
) -> list[dict[str, str]]:
    return [
        {"role": role, "content": content.format(**variables)}
        for role, content in templates
    ]


class RuntimePredictionProvider:
    def __init__(self, runtime: AIRuntime) -> None:
        self.runtime = runtime

    def predict(
        self, profile: StudentProfile, target_programs: list[str]
    ) -> tuple[AdmissionPrediction, str]:
        variables = {
            "student_profile": json.dumps(
                profile.model_dump(), indent=2, ensure_ascii=True
            ),
            "target_programs": json.dumps(target_programs, indent=2, ensure_ascii=True),
            "format_instructions": schema_instructions(AdmissionPrediction),
        }
        response = self.runtime.complete(
            _render_messages(prediction_messages(), variables), "admissions"
        )
        try:
            return parse_model_json(AdmissionPrediction, response.text), response.text
        except Exception as parse_error:
            LOGGER.warning(
                "Initial parse failed, attempting one repair pass: %s",
                safe_error_message(parse_error),
            )

        repaired = self.runtime.complete(
            _render_messages(
                repair_messages(),
                {
                    "format_instructions": schema_instructions(AdmissionPrediction),
                    "raw_output": response.text,
                },
            ),
            "admissions-repair",
        )
        try:
            return parse_model_json(AdmissionPrediction, repaired.text), repaired.text
        except Exception as final_parse_error:
            raise RuntimeError(
                "Model response could not be parsed into the required schema after repair."
            ) from final_parse_error
