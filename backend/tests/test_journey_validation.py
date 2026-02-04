import os
import unittest

os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost/personaapp")
os.environ.setdefault("SECRET_KEY", "test-secret")

from app.api.journey import _validate_answer_payload
from app.schemas.journey import JourneyAnswerSubmission


class JourneyValidationTests(unittest.TestCase):
    def test_validate_answer_payload_accepts_complete_valid_answers(self):
        answers = [
            JourneyAnswerSubmission(scenario_code="S01", option_code="A"),
            JourneyAnswerSubmission(scenario_code="S02", option_code="B"),
        ]
        valid_scenarios = {"S01", "S02"}
        option_map = {"S01": {"A", "B"}, "S02": {"A", "B"}}

        normalized = _validate_answer_payload(answers, valid_scenarios, option_map)

        self.assertEqual(len(normalized), 2)
        self.assertEqual(normalized[0].scenario_code, "S01")
        self.assertEqual(normalized[1].option_code, "B")

    def test_validate_answer_payload_rejects_missing_scenario(self):
        answers = [JourneyAnswerSubmission(scenario_code="S01", option_code="A")]
        valid_scenarios = {"S01", "S02"}
        option_map = {"S01": {"A", "B"}, "S02": {"A", "B"}}

        with self.assertRaises(ValueError) as ctx:
            _validate_answer_payload(answers, valid_scenarios, option_map)

        self.assertIn("Missing answers", str(ctx.exception))

    def test_validate_answer_payload_rejects_invalid_option(self):
        answers = [
            JourneyAnswerSubmission(scenario_code="S01", option_code="A"),
            JourneyAnswerSubmission(scenario_code="S02", option_code="Z"),
        ]
        valid_scenarios = {"S01", "S02"}
        option_map = {"S01": {"A", "B"}, "S02": {"A", "B"}}

        with self.assertRaises(ValueError) as ctx:
            _validate_answer_payload(answers, valid_scenarios, option_map)

        self.assertIn("Unknown option_code", str(ctx.exception))

    def test_validate_answer_payload_rejects_duplicate_scenario(self):
        answers = [
            JourneyAnswerSubmission(scenario_code="S01", option_code="A"),
            JourneyAnswerSubmission(scenario_code="S01", option_code="B"),
        ]
        valid_scenarios = {"S01"}
        option_map = {"S01": {"A", "B"}}

        with self.assertRaises(ValueError) as ctx:
            _validate_answer_payload(answers, valid_scenarios, option_map)

        self.assertIn("Duplicate answer", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
