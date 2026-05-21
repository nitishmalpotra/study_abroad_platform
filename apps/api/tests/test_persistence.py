from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from admissions.schemas import AdmissionPrediction, ProgramPrediction
from app.core.config import ApiSettings
from app.core.rate_limits import PostgresRateLimiter
from app.persistence.migrations import load_migrations, migration_statements
from app.persistence.privacy import admissions_record, hash_identifier, sop_record
from app.persistence.repositories import (
    PostgresAdmissionsPredictionRepository,
    PostgresSOPSubmissionRepository,
)
from fastapi import HTTPException
from sop_review.schemas import CriterionFeedback, SOPGrade

from test_api import admissions_payload, sop_payload


class FakeCursor:
    def __init__(self, rows: list[tuple[Any, ...]] | None = None) -> None:
        self.rows = rows or []
        self.statements: list[tuple[str, Any]] = []

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def execute(self, query: str, params: Any = ()) -> None:
        self.statements.append((query, params))

    def fetchone(self) -> tuple[Any, ...]:
        return self.rows.pop(0)

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self.rows


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False

    def cursor(self) -> FakeCursor:
        return self._cursor

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        return None


class FakeDatabase:
    def __init__(self, cursor: FakeCursor) -> None:
        self.connection_obj = FakeConnection(cursor)

    @contextmanager
    def connection(self) -> Iterator[FakeConnection]:
        yield self.connection_obj
        self.connection_obj.commit()


def sop_grade() -> SOPGrade:
    return SOPGrade(
        overall_score=8,
        criteria_breakdown=[
            CriterionFeedback(name="Academic Fit", score=8, feedback="Strong"),
            CriterionFeedback(
                name="University Specificity", score=8, feedback="Strong"
            ),
            CriterionFeedback(name="Career Clarity", score=8, feedback="Strong"),
            CriterionFeedback(name="Narrative Flow", score=8, feedback="Strong"),
            CriterionFeedback(name="Language & Tone", score=8, feedback="Strong"),
        ],
        summary="Good SOP",
    )


def prediction() -> AdmissionPrediction:
    return AdmissionPrediction(
        target_predictions=[
            ProgramPrediction(
                program_name="MS CS at Oxford",
                chance_category="Reach",
                estimated_probability_percentage=30,
                brief_reasoning="Competitive target with a strong applicant pool.",
            )
        ],
        profile_strengths=["Strong GPA", "Research", "Experience"],
        profile_weaknesses=["Few publications", "Leadership", "No GMAT"],
        actionable_roadmap=["Improve SOP", "Add projects", "Apply early"],
        recommended_universities=["A", "B", "C"],
    )


def test_sop_record_minimizes_stored_content() -> None:
    from app.api.routes.sop import _profile_from_request
    from study_abroad_contracts import SOPReviewRequest

    profile = _profile_from_request(SOPReviewRequest(**sop_payload()))
    record = sop_record(profile, " ".join(["word"] * 120), sop_grade())

    assert "full_name" not in record
    assert "mobile" not in record
    assert "sop_text" not in record
    assert record["sop_word_count"] == 120
    assert record["overall_score"] == 8


def test_admissions_record_minimizes_stored_content() -> None:
    from admissions.schemas import StudentProfile

    payload = admissions_payload()
    target_programs = payload["target_programs"]
    assert isinstance(target_programs, list)
    assert all(isinstance(program, str) for program in target_programs)
    profile = StudentProfile(
        **{k: v for k, v in payload.items() if k != "target_programs"}
    )
    record = admissions_record(profile, target_programs, prediction())

    assert "full_name" not in record["profile_summary_json"]
    assert "raw_output" not in record
    assert record["target_country"] == "United Kingdom"


def test_postgres_repositories_write_separate_tables() -> None:
    from admissions.schemas import StudentProfile as AdmissionsProfile
    from app.api.routes.sop import _profile_from_request
    from study_abroad_contracts import SOPReviewRequest

    sop_cursor = FakeCursor()
    sop_repo = PostgresSOPSubmissionRepository(FakeDatabase(sop_cursor))  # type: ignore[arg-type]
    sop_repo.save(
        _profile_from_request(SOPReviewRequest(**sop_payload())),
        " ".join(["word"] * 120),
        sop_grade(),
        '{"unused": true}',
    )
    sop_query, sop_params = sop_cursor.statements[0]

    admissions_cursor = FakeCursor()
    admissions_repo = PostgresAdmissionsPredictionRepository(
        FakeDatabase(admissions_cursor)  # type: ignore[arg-type]
    )
    payload = admissions_payload()
    target_programs = payload["target_programs"]
    assert isinstance(target_programs, list)
    assert all(isinstance(program, str) for program in target_programs)
    admissions_repo.save_prediction(
        AdmissionsProfile(
            **{k: v for k, v in payload.items() if k != "target_programs"}
        ),
        target_programs,
        prediction(),
    )
    admissions_query, admissions_params = admissions_cursor.statements[0]

    assert "sop_review_submissions" in sop_query
    assert "admissions_predictions" in admissions_query
    assert "raw" not in sop_params
    assert "full_name" not in admissions_params["profile_summary_json"]


def test_rate_limit_hashing_is_stable_and_salted() -> None:
    assert hash_identifier(" 127.0.0.1 ", "salt") == hash_identifier(
        "127.0.0.1", "salt"
    )
    assert hash_identifier("127.0.0.1", "salt") != hash_identifier(
        "127.0.0.1", "other-salt"
    )


def test_postgres_rate_limiter_uses_hashed_bucket_keys() -> None:
    cursor = FakeCursor(rows=[(1,), (2,)])
    limiter = PostgresRateLimiter(
        ApiSettings(1, 3600, (), rate_limit_hash_salt="salt"),
        FakeDatabase(cursor),  # type: ignore[arg-type]
    )

    limiter.check("127.0.0.1")
    try:
        limiter.check("127.0.0.1")
    except HTTPException as exc:
        assert exc.status_code == 429
    else:
        raise AssertionError("Expected rate limit failure.")

    params = cursor.statements[0][1]
    assert params["key_hash"] == hash_identifier("127.0.0.1", "salt")
    assert "127.0.0.1" not in str(params)


def test_migration_files_are_versioned_and_create_required_tables() -> None:
    migrations = load_migrations(Path("migrations"))
    sql = "\n".join(migration.sql for migration in migrations)

    assert [migration.version for migration in migrations] == [
        "001_public_platform_persistence"
    ]
    assert "CREATE TABLE IF NOT EXISTS sop_review_submissions" in sql
    assert "CREATE TABLE IF NOT EXISTS admissions_predictions" in sql
    assert "CREATE TABLE IF NOT EXISTS rate_limit_buckets" in sql
    assert len(migration_statements(sql)) >= 8
