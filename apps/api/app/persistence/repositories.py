from typing import Any

from admissions.schemas import AdmissionPrediction
from admissions.schemas import StudentProfile as AdmissionsProfile
from sop_review.schemas import SOPGrade
from sop_review.schemas import StudentProfile as SOPProfile

from .database import Database
from .privacy import admissions_record, json_dumps, sop_record


class PostgresLeadRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save_lead(self, lead: dict[str, str]) -> None:
        with self.database.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tool_leads (
                        tool_name,
                        phone,
                        email,
                        target_country,
                        target_intake,
                        target_college,
                        target_course,
                        journey_stage
                    )
                    VALUES (
                        %(tool_name)s,
                        %(phone)s,
                        %(email)s,
                        %(target_country)s,
                        %(target_intake)s,
                        %(target_college)s,
                        %(target_course)s,
                        %(journey_stage)s
                    )
                    """,
                    lead,
                )


class NullSOPSubmissionRepository:
    def save(
        self,
        profile: SOPProfile,
        sop_text: str,
        grade: SOPGrade,
        raw_json: str,
    ) -> int:
        return 0


class PostgresSOPSubmissionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save(
        self,
        profile: SOPProfile,
        sop_text: str,
        grade: SOPGrade,
        raw_json: str,
    ) -> int:
        record = sop_record(profile, sop_text, grade)
        with self.database.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO sop_review_submissions (
                        university,
                        intake,
                        country,
                        sop_word_count,
                        overall_score,
                        grade_json
                    )
                    VALUES (
                        %(university)s,
                        %(intake)s,
                        %(country)s,
                        %(sop_word_count)s,
                        %(overall_score)s,
                        %(grade_json)s::jsonb
                    )
                    """,
                    {
                        **record,
                        "grade_json": json_dumps(record["grade_json"]),
                    },
                )
        return 0


class NullAdmissionsPredictionRepository:
    def save_prediction(
        self,
        profile: AdmissionsProfile,
        target_programs: list[str],
        prediction: AdmissionPrediction,
    ) -> None:
        return None


class PostgresAdmissionsPredictionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save_prediction(
        self,
        profile: AdmissionsProfile,
        target_programs: list[str],
        prediction: AdmissionPrediction,
    ) -> None:
        record = admissions_record(profile, target_programs, prediction)
        params: dict[str, Any] = {
            **record,
            "profile_summary_json": json_dumps(record["profile_summary_json"]),
            "target_programs_json": json_dumps(record["target_programs_json"]),
            "prediction_json": json_dumps(record["prediction_json"]),
        }
        with self.database.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO admissions_predictions (
                        target_intake,
                        target_country,
                        profile_summary_json,
                        target_programs_json,
                        prediction_json
                    )
                    VALUES (
                        %(target_intake)s,
                        %(target_country)s,
                        %(profile_summary_json)s::jsonb,
                        %(target_programs_json)s::jsonb,
                        %(prediction_json)s::jsonb
                    )
                    """,
                    params,
                )
