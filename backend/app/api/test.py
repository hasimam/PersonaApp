"""
API endpoints for personality test functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Literal
import uuid

from app.db.session import get_db
from app.models import Question, User, TestResponse, Result, Trait
from app.schemas import TestStartResponse, TestSubmission, TestSubmitResponse, QuestionResponse
from app.core.scoring import calculate_trait_scores, validate_responses
from app.core.matching import find_top_matches
from app.core.config import settings

router = APIRouter()


@router.get("/start", response_model=TestStartResponse)
def start_test(
    lang: Literal["en", "ar"] = Query(default="en", description="Language for questions"),
    db: Session = Depends(get_db)
):
    """
    Start a new personality test.
    Returns a session ID and all test questions in the requested language.
    """
    # Generate unique session ID
    session_id = str(uuid.uuid4())

    # Create user session
    user = User(session_id=session_id)
    db.add(user)
    db.commit()

    # Get all questions, ordered
    questions = db.query(Question).order_by(Question.order_index).all()

    # Filter questions based on language availability
    if lang == "ar":
        # For Arabic, only include questions that have Arabic text
        questions = [q for q in questions if q.text_ar]

    if len(questions) < settings.MIN_QUESTIONS:
        raise HTTPException(
            status_code=500,
            detail=f"Insufficient questions in database for language '{lang}'. Need at least {settings.MIN_QUESTIONS}"
        )

    # Convert to response schema with appropriate language
    question_responses = [
        QuestionResponse(
            id=q.id,
            text=q.text_ar if lang == "ar" else q.text_en,
            trait_id=q.trait_id,
            order_index=q.order_index
        )
        for q in questions
    ]

    return TestStartResponse(
        session_id=session_id,
        questions=question_responses,
        total_questions=len(questions)
    )


@router.post("/submit", response_model=TestSubmitResponse)
def submit_test(
    submission: TestSubmission,
    db: Session = Depends(get_db)
):
    """
    Submit completed personality test.
    Calculates trait scores, finds top matches, and returns result ID.
    """
    # Verify session exists
    user = db.query(User).filter(User.session_id == submission.session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Invalid session_id")

    # Convert responses to dict format
    responses = [
        {"question_id": r.question_id, "answer": r.answer}
        for r in submission.responses
    ]

    # Validate responses
    try:
        validate_responses(responses, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save individual responses to database
    for response_data in responses:
        test_response = TestResponse(
            user_id=user.id,
            session_id=submission.session_id,
            question_id=response_data["question_id"],
            response=response_data["answer"]
        )
        db.add(test_response)

    # Calculate trait scores
    trait_scores = calculate_trait_scores(responses, db)

    # Find top matches
    top_matches = find_top_matches(
        trait_scores,
        db,
        top_n=settings.TOP_N_MATCHES
    )

    # Format matches for storage
    matches_data = [
        {
            "idol_id": match["idol_id"],
            "similarity": match["similarity"]
        }
        for match in top_matches
    ]

    # Convert trait_scores keys to strings for JSONB storage
    trait_scores_json = {str(k): v for k, v in trait_scores.items()}

    # Save result
    result = Result(
        user_id=user.id,
        session_id=submission.session_id,
        trait_scores=trait_scores_json,
        top_matches=matches_data
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return TestSubmitResponse(
        result_id=result.id,
        message="Test submitted successfully"
    )
