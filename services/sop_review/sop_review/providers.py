import logging
import os
import re
import time
from typing import List, Sequence, Tuple

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from .config import AppSettings
from .prompts import GATEKEEPER_HUMAN, GATEKEEPER_SYSTEM, GRADING_HUMAN, GRADING_SYSTEM
from .schemas import GatekeeperResponse, SOPGrade


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
    return fenced_match.group(1).strip() if fenced_match else cleaned


class GeminiReviewProvider:
    def __init__(self, settings: AppSettings, logger: logging.Logger) -> None:
        self.settings = settings
        self.logger = logger

    def _get_llm_client(self, model_name: str, api_key: str) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.0,
            google_api_key=api_key,
            max_retries=1,
        )

    def _invoke(
        self,
        prompt: ChatPromptTemplate,
        parser: PydanticOutputParser,
        variables: dict,
        request_id: str,
    ) -> Tuple[BaseModel, str, str]:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is missing. Add it to your .env file.")

        messages = prompt.format_messages(
            format_instructions=parser.get_format_instructions(), **variables
        )
        errors: List[str] = []
        for model_name in self.settings.model_candidates:
            for attempt in range(1, self.settings.llm_retries + 1):
                try:
                    response = self._get_llm_client(model_name, api_key).invoke(messages)
                    raw_content = normalize_llm_content(response.content).strip()
                    parsed = parser.parse(extract_json_payload(raw_content))
                    return parsed, raw_content, model_name
                except Exception as exc:  # noqa: BLE001
                    error_message = f"{model_name} attempt {attempt}: {exc}"
                    errors.append(error_message)
                    self.logger.warning("[%s] LLM call failed: %s", request_id, error_message)
                    lowered = str(exc).lower()
                    if "404 models/" in lowered or "not found for api version" in lowered:
                        break
                    if attempt < self.settings.llm_retries:
                        time.sleep(self.settings.llm_retry_backoff_sec * attempt)
        raise RuntimeError(
            "Failed to get a valid response from configured models.\n" + "\n".join(errors)
        )

    def gatekeep(self, sop_text: str, request_id: str) -> Tuple[GatekeeperResponse, str]:
        prompt = ChatPromptTemplate.from_messages(
            [("system", GATEKEEPER_SYSTEM), ("human", GATEKEEPER_HUMAN)]
        )
        response, _, model_name = self._invoke(
            prompt,
            PydanticOutputParser(pydantic_object=GatekeeperResponse),
            {"sop_text": sop_text},
            request_id,
        )
        return response, model_name

    def grade(
        self, sop_text: str, university: str, country: str, request_id: str
    ) -> Tuple[SOPGrade, str, str]:
        prompt = ChatPromptTemplate.from_messages(
            [("system", GRADING_SYSTEM), ("human", GRADING_HUMAN)]
        )
        grade, raw_json, model_name = self._invoke(
            prompt,
            PydanticOutputParser(pydantic_object=SOPGrade),
            {"sop_text": sop_text, "university": university, "country": country},
            request_id,
        )
        return grade, raw_json, model_name
