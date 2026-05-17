import json
import re
from typing import TypeVar

from pydantic import BaseModel


ModelT = TypeVar("ModelT", bound=BaseModel)


def extract_json_payload(raw_text: str) -> str:
    cleaned = raw_text.strip()
    fenced_match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if fenced_match:
        return fenced_match.group(1).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end > start:
        return cleaned[start : end + 1]
    return cleaned


def parse_model_json(model_type: type[ModelT], raw_text: str) -> ModelT:
    payload = extract_json_payload(raw_text)
    try:
        return model_type.model_validate_json(payload)
    except Exception:
        return model_type.model_validate(json.loads(payload))


def schema_instructions(model_type: type[BaseModel]) -> str:
    return json.dumps(model_type.model_json_schema(), ensure_ascii=True)
