import json
import logging
import re
import time
from typing import Any

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from .config import AppSettings
from .prompts import prediction_messages, repair_messages
from .schemas import AdmissionPrediction, StudentProfile
from .utils import sanitize_text


LOGGER = logging.getLogger("admissions_app")


def safe_error_message(error: Exception) -> str:
    message = sanitize_text(str(error), max_length=500)
    message = re.sub(r"AIza[0-9A-Za-z_\-]{16,}", "[REDACTED_API_KEY]", message)
    return message or "Unexpected error."


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


class GeminiPredictionProvider:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            temperature=0.0,
            google_api_key=settings.google_api_key,
            timeout=settings.llm_timeout_seconds,
            max_retries=0,
        )

    def invoke_with_retry(self, chain: Any, payload: dict[str, Any]) -> Any:
        total_attempts = self.settings.llm_retry_attempts + 1
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

    def predict(self, profile: StudentProfile, target_programs: list[str]) -> tuple[AdmissionPrediction, str]:
        parser = PydanticOutputParser(pydantic_object=AdmissionPrediction)
        prompt = ChatPromptTemplate.from_messages(prediction_messages())
        response = self.invoke_with_retry(
            prompt | self.llm,
            {
                "student_profile": json.dumps(profile.model_dump(), indent=2, ensure_ascii=True),
                "target_programs": json.dumps(target_programs, indent=2, ensure_ascii=True),
                "format_instructions": parser.get_format_instructions(),
            },
        )
        raw_output = normalize_llm_content(response.content)
        try:
            return parse_prediction_output(parser, raw_output), strip_code_fence(raw_output)
        except Exception as parse_error:
            LOGGER.warning("Initial parse failed, attempting one repair pass: %s", safe_error_message(parse_error))

        repair_prompt = ChatPromptTemplate.from_messages(repair_messages())
        repaired_response = self.invoke_with_retry(
            repair_prompt | self.llm,
            {
                "format_instructions": parser.get_format_instructions(),
                "raw_output": raw_output,
            },
        )
        repaired_raw_output = normalize_llm_content(repaired_response.content)
        try:
            return parse_prediction_output(parser, repaired_raw_output), strip_code_fence(repaired_raw_output)
        except Exception as final_parse_error:
            raise RuntimeError(
                "Model response could not be parsed into the required schema after repair."
            ) from final_parse_error
