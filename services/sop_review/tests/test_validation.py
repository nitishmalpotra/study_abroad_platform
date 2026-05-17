import unittest
from pathlib import Path

from sop_review.config import AppSettings
from sop_review.validation import validate_profile, validate_sop_text, word_count_gate


def settings() -> AppSettings:
    return AppSettings(
        db_path=Path(":memory:"),
        min_words=3,
        max_words=10,
        max_upload_mb=10,
        max_sop_chars=20,
        max_requests_per_window=6,
        rate_limit_window_minutes=60,
        app_env="test",
    )


class ValidationTests(unittest.TestCase):
    def test_profile_validation_sanitizes_fields(self) -> None:
        ok, profile, error = validate_profile(
            " Ada  Lovelace ",
            "+44 (123) 456-7890",
            " Example University ",
            " Fall 2026 ",
            " UK ",
        )
        self.assertTrue(ok)
        self.assertEqual(error, "")
        self.assertEqual(profile.full_name, "Ada Lovelace")
        self.assertEqual(profile.mobile, "441234567890")

    def test_profile_validation_rejects_invalid_mobile(self) -> None:
        ok, profile, error = validate_profile("Ada", "123", "Uni", "Fall", "UK")
        self.assertFalse(ok)
        self.assertIsNone(profile)
        self.assertEqual(error, "Mobile must be 10 to 15 digits.")

    def test_validate_sop_text_rejects_empty_and_overlong_text(self) -> None:
        with self.assertRaisesRegex(ValueError, "Provide SOP text"):
            validate_sop_text("   ", settings())
        with self.assertRaisesRegex(ValueError, "too long"):
            validate_sop_text("x" * 21, settings())

    def test_word_count_gate_enforces_bounds(self) -> None:
        self.assertIsNone(word_count_gate("one two three", settings()))
        rejection = word_count_gate("one two", settings())
        self.assertFalse(rejection.is_valid)
        self.assertIn("Word count is 2", rejection.reason)
