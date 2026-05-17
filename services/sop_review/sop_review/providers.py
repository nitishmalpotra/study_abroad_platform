from ai_runtime import AIRuntime, parse_model_json, schema_instructions

from .prompts import GATEKEEPER_HUMAN, GATEKEEPER_SYSTEM, GRADING_HUMAN, GRADING_SYSTEM
from .schemas import GatekeeperResponse, SOPGrade


def _messages(system: str, human: str, variables: dict[str, str]) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": human.format(**variables)},
    ]


class RuntimeReviewProvider:
    def __init__(self, runtime: AIRuntime) -> None:
        self.runtime = runtime

    def gatekeep(self, sop_text: str, request_id: str) -> tuple[GatekeeperResponse, str]:
        response = self.runtime.complete(
            _messages(
                GATEKEEPER_SYSTEM,
                GATEKEEPER_HUMAN,
                {
                    "format_instructions": schema_instructions(GatekeeperResponse),
                    "sop_text": sop_text,
                },
            ),
            request_id,
        )
        return parse_model_json(GatekeeperResponse, response.text), response.model

    def grade(
        self, sop_text: str, university: str, country: str, request_id: str
    ) -> tuple[SOPGrade, str, str]:
        response = self.runtime.complete(
            _messages(
                GRADING_SYSTEM,
                GRADING_HUMAN,
                {
                    "format_instructions": schema_instructions(SOPGrade),
                    "sop_text": sop_text,
                    "university": university,
                    "country": country,
                },
            ),
            request_id,
        )
        return parse_model_json(SOPGrade, response.text), response.text, response.model
