import json
import unittest
from pathlib import Path

from sop_review.prompts import PROMPT_METADATA, PROMPT_VERSION
from sop_review.schemas import EXPECTED_CRITERIA, GatekeeperResponse, SOPGrade


FIXTURES_PATH = Path(__file__).parents[1] / "evals" / "fixtures.json"


def load_fixtures():
    return json.loads(FIXTURES_PATH.read_text())


def word_count(text: str) -> int:
    return len(text.split())


class PromptEvalTests(unittest.TestCase):
    def test_active_prompt_is_versioned_and_documents_quality_philosophy(self) -> None:
        self.assertEqual(PROMPT_VERSION, "v2")
        self.assertIn("judgment over volume", PROMPT_METADATA["quality_philosophy"])
        self.assertEqual(
            PROMPT_METADATA["response_contract"]["criteria"], EXPECTED_CRITERIA
        )

    def test_eval_fixtures_cover_required_cases(self) -> None:
        fixtures = {fixture["id"] for fixture in load_fixtures()}
        self.assertEqual(fixtures, {"strong", "average", "weak_generic", "invalid_non_sop"})

    def test_golden_outputs_match_stable_schema_contract(self) -> None:
        for fixture in load_fixtures():
            if fixture["kind"] == "gatekeeper":
                parsed = GatekeeperResponse.model_validate(fixture["golden_output"])
                self.assertFalse(parsed.is_valid)
            else:
                parsed = SOPGrade.model_validate(fixture["golden_output"])
                self.assertEqual(
                    [item.name for item in parsed.criteria_breakdown], EXPECTED_CRITERIA
                )

    def test_golden_outputs_are_concise_enough_to_render_cleanly(self) -> None:
        for fixture in load_fixtures():
            if fixture["kind"] != "grading":
                continue
            parsed = SOPGrade.model_validate(fixture["golden_output"])
            self.assertLessEqual(word_count(parsed.summary), 70)
            for criterion in parsed.criteria_breakdown:
                self.assertLessEqual(word_count(criterion.feedback), 35)

    def test_golden_outputs_capture_expected_quality_tendencies(self) -> None:
        fixtures = {fixture["id"]: fixture for fixture in load_fixtures()}
        strong = SOPGrade.model_validate(fixtures["strong"]["golden_output"])
        average = SOPGrade.model_validate(fixtures["average"]["golden_output"])
        weak = SOPGrade.model_validate(fixtures["weak_generic"]["golden_output"])

        self.assertGreater(strong.overall_score, average.overall_score)
        self.assertGreater(average.overall_score, weak.overall_score)
        self.assertGreater(
            strong.criteria_breakdown[1].score, average.criteria_breakdown[1].score
        )
        self.assertGreater(
            average.criteria_breakdown[1].score, weak.criteria_breakdown[1].score
        )
        self.assertIn("no concrete", average.criteria_breakdown[1].feedback.lower())
        self.assertIn("no academic background", weak.criteria_breakdown[0].feedback.lower())

    def test_schema_rejects_wrong_criterion_order(self) -> None:
        payload = load_fixtures()[0]["golden_output"]
        payload = {
            **payload,
            "criteria_breakdown": list(reversed(payload["criteria_breakdown"])),
        }
        with self.assertRaisesRegex(ValueError, "exact order"):
            SOPGrade.model_validate(payload)
