import unittest
from pathlib import Path

from sop_review.config import AppSettings
from sop_review.schemas import CriterionFeedback, GatekeeperResponse, SOPGrade, StudentProfile
from sop_review.service import SOPReviewService


def settings() -> AppSettings:
    return AppSettings(
        db_path=Path(":memory:"),
        min_words=3,
        max_words=20,
        max_upload_mb=10,
        max_sop_chars=1000,
        max_requests_per_window=6,
        rate_limit_window_minutes=60,
        app_env="test",
    )


def profile() -> StudentProfile:
    return StudentProfile("Ada", "1234567890", "Example University", "Fall", "UK")


def grade() -> SOPGrade:
    return SOPGrade(
        overall_score=8,
        criteria_breakdown=[
            CriterionFeedback(name="Academic Fit", score=8, feedback="Strong"),
            CriterionFeedback(name="University Specificity", score=8, feedback="Strong"),
            CriterionFeedback(name="Career Clarity", score=8, feedback="Strong"),
            CriterionFeedback(name="Narrative Flow", score=8, feedback="Strong"),
            CriterionFeedback(name="Language & Tone", score=8, feedback="Strong"),
        ],
        summary="Good SOP",
    )


class FakeProvider:
    def __init__(self, gatekeeper: GatekeeperResponse) -> None:
        self.gatekeeper = gatekeeper
        self.gatekeep_calls = 0
        self.grade_calls = 0

    def gatekeep(self, sop_text: str, request_id: str):
        self.gatekeep_calls += 1
        return self.gatekeeper, "fake-gate"

    def grade(self, sop_text: str, university: str, country: str, request_id: str):
        self.grade_calls += 1
        return grade(), '{"overall_score":8}', "fake-grade"


class FakeRepository:
    def __init__(self) -> None:
        self.saved = []

    def save(self, profile, sop_text, grade, raw_json):
        self.saved.append((profile, sop_text, grade, raw_json))
        return 42


class ServiceTests(unittest.TestCase):
    def test_local_word_count_gate_skips_provider_and_repository(self) -> None:
        provider = FakeProvider(GatekeeperResponse(is_valid=True, reason="ok"))
        repository = FakeRepository()
        result = SOPReviewService(settings(), provider, repository).review(
            profile(), "too short", "req"
        )
        self.assertFalse(result.gatekeeper.is_valid)
        self.assertEqual(result.gatekeeper_model, "local-word-count")
        self.assertEqual(provider.gatekeep_calls, 0)
        self.assertEqual(repository.saved, [])

    def test_provider_rejection_skips_grading_and_persistence(self) -> None:
        provider = FakeProvider(GatekeeperResponse(is_valid=False, reason="not sop"))
        repository = FakeRepository()
        result = SOPReviewService(settings(), provider, repository).review(
            profile(), "one two three four", "req"
        )
        self.assertFalse(result.gatekeeper.is_valid)
        self.assertEqual(provider.gatekeep_calls, 1)
        self.assertEqual(provider.grade_calls, 0)
        self.assertEqual(repository.saved, [])

    def test_valid_review_grades_and_persists(self) -> None:
        provider = FakeProvider(GatekeeperResponse(is_valid=True, reason="valid"))
        repository = FakeRepository()
        result = SOPReviewService(settings(), provider, repository).review(
            profile(), "one two three four", "req"
        )
        self.assertTrue(result.gatekeeper.is_valid)
        self.assertEqual(result.grading_model, "fake-grade")
        self.assertEqual(result.submission_id, 42)
        self.assertEqual(provider.gatekeep_calls, 1)
        self.assertEqual(provider.grade_calls, 1)
        self.assertEqual(len(repository.saved), 1)
