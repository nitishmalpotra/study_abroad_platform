import json
from pathlib import Path

from study_abroad_contracts import (
    AdmissionsPredictionRequest,
    AdmissionsPredictionResponse,
    ApiError,
    SOPReviewRequest,
    SOPReviewResponse,
)
from study_abroad_contracts.examples import (
    SOP_REVIEW_MOCK_RESPONSE,
    admissions_prediction_mock_response,
)
from study_abroad_contracts.schema_export import SCHEMAS


SCHEMA_DIR = Path(__file__).parents[1] / "schemas"


def test_committed_json_schemas_match_contract_models() -> None:
    for file_name, model in SCHEMAS.items():
        committed = json.loads((SCHEMA_DIR / file_name).read_text())
        assert committed == model.model_json_schema()


def test_mock_payloads_conform_to_live_response_contracts() -> None:
    assert isinstance(SOP_REVIEW_MOCK_RESPONSE, SOPReviewResponse)
    assert isinstance(
        admissions_prediction_mock_response("MS CS at Oxford"),
        AdmissionsPredictionResponse,
    )


def test_contract_names_keep_workflows_explicit() -> None:
    assert SOPReviewRequest.__name__ == "SOPReviewRequest"
    assert SOPReviewResponse.__name__ == "SOPReviewResponse"
    assert AdmissionsPredictionRequest.__name__ == "AdmissionsPredictionRequest"
    assert AdmissionsPredictionResponse.__name__ == "AdmissionsPredictionResponse"
    assert ApiError.__name__ == "ApiError"
