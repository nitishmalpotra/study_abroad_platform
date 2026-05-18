from pathlib import Path
import json

from pydantic import BaseModel

from .api import (
    AdmissionsPredictionRequest,
    AdmissionsPredictionResponse,
    ApiError,
    SOPReviewRequest,
    SOPReviewResponse,
)


SCHEMAS: dict[str, type[BaseModel]] = {
    "api_error.schema.json": ApiError,
    "sop_review_request.schema.json": SOPReviewRequest,
    "sop_review_response.schema.json": SOPReviewResponse,
    "admissions_prediction_request.schema.json": AdmissionsPredictionRequest,
    "admissions_prediction_response.schema.json": AdmissionsPredictionResponse,
}


def export_json_schemas(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for file_name, model in SCHEMAS.items():
        path = output_dir / file_name
        path.write_text(
            json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n"
        )
