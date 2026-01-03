"""
Personality test scoring engine.
Converts Likert-scale responses into normalized trait scores (0-100).
"""

from typing import Dict, List
from sqlalchemy.orm import Session
from app.models import Question, TestResponse


def calculate_trait_scores(
    responses: List[Dict[str, int]],
    db: Session
) -> Dict[int, float]:
    """
    Calculate normalized trait scores from test responses.

    Args:
        responses: List of {"question_id": int, "answer": int}
        db: Database session

    Returns:
        Dict mapping trait_id -> normalized score (0-100)
    """
    # Group responses by trait
    trait_responses = {}

    for response_data in responses:
        question_id = response_data["question_id"]
        answer = response_data["answer"]

        # Get question details
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            continue

        trait_id = question.trait_id

        # Apply reverse scoring if needed
        if question.reverse_scored:
            # Assuming 1-5 scale: reverse is (max + min - answer)
            from app.core.config import settings
            answer = settings.LIKERT_SCALE_MAX + settings.LIKERT_SCALE_MIN - answer

        # Add to trait responses
        if trait_id not in trait_responses:
            trait_responses[trait_id] = []
        trait_responses[trait_id].append(answer)

    # Calculate average score per trait and normalize to 0-100
    trait_scores = {}
    from app.core.config import settings

    for trait_id, answers in trait_responses.items():
        # Average score
        avg_score = sum(answers) / len(answers)

        # Normalize to 0-100 scale
        # Formula: ((score - min) / (max - min)) * 100
        normalized = (
            (avg_score - settings.LIKERT_SCALE_MIN) /
            (settings.LIKERT_SCALE_MAX - settings.LIKERT_SCALE_MIN)
        ) * 100

        trait_scores[trait_id] = round(normalized, 2)

    return trait_scores


def validate_responses(responses: List[Dict[str, int]], db: Session) -> bool:
    """
    Validate that responses are complete and valid.

    Args:
        responses: List of question responses
        db: Database session

    Returns:
        True if valid, raises ValueError otherwise
    """
    from app.core.config import settings

    # Check minimum number of responses
    if len(responses) < settings.MIN_QUESTIONS:
        raise ValueError(f"Minimum {settings.MIN_QUESTIONS} responses required")

    # Validate each response
    valid_question_ids = set()
    for response in responses:
        question_id = response.get("question_id")
        answer = response.get("answer")

        if not question_id or not answer:
            raise ValueError("Each response must have question_id and answer")

        # Check for duplicate responses
        if question_id in valid_question_ids:
            raise ValueError(f"Duplicate response for question {question_id}")
        valid_question_ids.add(question_id)

        # Validate answer range
        if not (settings.LIKERT_SCALE_MIN <= answer <= settings.LIKERT_SCALE_MAX):
            raise ValueError(
                f"Answer must be between {settings.LIKERT_SCALE_MIN} "
                f"and {settings.LIKERT_SCALE_MAX}"
            )

        # Verify question exists
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise ValueError(f"Invalid question_id: {question_id}")

    return True
