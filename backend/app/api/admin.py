"""
Admin panel API endpoints for managing content.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import case, func
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models import Feedback, Idol, Question, Result, TestRun, Trait, User
from app.schemas.admin import (
    QuestionCreate, QuestionUpdate, QuestionResponse,
    IdolCreate, IdolUpdate, IdolResponse,
    TraitCreate, TraitUpdate, TraitResponse,
    AdminStats
)
from app.core.config import settings

router = APIRouter()


# ============ Authentication Dependency ============

def verify_admin_key(x_admin_key: str = Header(..., description="Admin API key")):
    """Verify the admin API key from header."""
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin API key")
    return True


# ============ Stats Endpoint ============

@router.get("/stats", response_model=AdminStats)
def get_stats(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Get dashboard statistics."""
    total_questions = db.query(Question).count()
    total_idols = db.query(Idol).count()
    total_traits = db.query(Trait).count()
    total_users = db.query(User).count()
    total_tests_completed = db.query(Result).count()

    # Count items with Arabic translations
    questions_with_arabic = db.query(Question).filter(Question.text_ar.isnot(None)).count()
    idols_with_arabic = db.query(Idol).filter(Idol.name_ar.isnot(None)).count()
    traits_with_arabic = db.query(Trait).filter(Trait.name_ar.isnot(None)).count()

    run_type_expr = case(
        (TestRun.version_id.like("v2%"), "deep"),
        else_="quick",
    )

    feedback_summary = (
        db.query(
            func.count(Feedback.id),
            func.avg(Feedback.accuracy_score),
            func.avg(Feedback.personality_match_score),
        )
        .first()
    )
    journey_feedback_count = int(feedback_summary[0] or 0)
    journey_feedback_avg_accuracy = (
        float(feedback_summary[1]) if feedback_summary and feedback_summary[1] is not None else None
    )
    journey_feedback_avg_personality_match = (
        float(feedback_summary[2]) if feedback_summary and feedback_summary[2] is not None else None
    )

    feedback_by_run_type_rows = (
        db.query(
            run_type_expr.label("run_type"),
            func.count(Feedback.id).label("count"),
            func.avg(Feedback.accuracy_score).label("avg_accuracy_score"),
            func.avg(Feedback.personality_match_score).label("avg_personality_match_score"),
        )
        .join(TestRun, TestRun.id == Feedback.test_run_id)
        .group_by(run_type_expr)
        .order_by(run_type_expr.asc())
        .all()
    )
    feedback_by_run_type = [
        {
            "run_type": row.run_type,
            "count": int(row.count or 0),
            "avg_accuracy_score": (
                float(row.avg_accuracy_score) if row.avg_accuracy_score is not None else None
            ),
            "avg_personality_match_score": (
                float(row.avg_personality_match_score)
                if row.avg_personality_match_score is not None
                else None
            ),
        }
        for row in feedback_by_run_type_rows
    ]

    feedback_by_set_rows = (
        db.query(
            TestRun.scenario_set_code,
            run_type_expr.label("run_type"),
            func.count(Feedback.id).label("count"),
            func.avg(Feedback.accuracy_score).label("avg_accuracy_score"),
            func.avg(Feedback.personality_match_score).label("avg_personality_match_score"),
        )
        .join(TestRun, TestRun.id == Feedback.test_run_id)
        .group_by(TestRun.scenario_set_code, run_type_expr)
        .order_by(func.count(Feedback.id).desc(), TestRun.scenario_set_code.asc())
        .all()
    )
    feedback_by_set = [
        {
            "scenario_set_code": row.scenario_set_code or "unknown",
            "run_type": row.run_type,
            "count": int(row.count or 0),
            "avg_accuracy_score": (
                float(row.avg_accuracy_score) if row.avg_accuracy_score is not None else None
            ),
            "avg_personality_match_score": (
                float(row.avg_personality_match_score)
                if row.avg_personality_match_score is not None
                else None
            ),
        }
        for row in feedback_by_set_rows
    ]

    return AdminStats(
        total_questions=total_questions,
        total_idols=total_idols,
        total_traits=total_traits,
        total_users=total_users,
        total_tests_completed=total_tests_completed,
        questions_with_arabic=questions_with_arabic,
        idols_with_arabic=idols_with_arabic,
        traits_with_arabic=traits_with_arabic,
        journey_feedback_count=journey_feedback_count,
        journey_feedback_avg_accuracy=journey_feedback_avg_accuracy,
        journey_feedback_avg_personality_match=journey_feedback_avg_personality_match,
        journey_feedback_by_run_type=feedback_by_run_type,
        journey_feedback_by_set=feedback_by_set,
    )


# ============ Question Endpoints ============

@router.get("/questions", response_model=List[QuestionResponse])
def list_questions(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """List all questions."""
    questions = db.query(Question).order_by(Question.order_index).all()
    return questions


@router.get("/questions/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Get a specific question."""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.post("/questions", response_model=QuestionResponse, status_code=201)
def create_question(
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Create a new question."""
    # Verify trait exists
    trait = db.query(Trait).filter(Trait.id == question_data.trait_id).first()
    if not trait:
        raise HTTPException(status_code=400, detail=f"Trait with id {question_data.trait_id} not found")

    question = Question(**question_data.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.put("/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Update a question."""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Verify trait exists if being updated
    if question_data.trait_id is not None:
        trait = db.query(Trait).filter(Trait.id == question_data.trait_id).first()
        if not trait:
            raise HTTPException(status_code=400, detail=f"Trait with id {question_data.trait_id} not found")

    update_data = question_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(question, field, value)

    db.commit()
    db.refresh(question)
    return question


@router.delete("/questions/{question_id}", status_code=204)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Delete a question."""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(question)
    db.commit()
    return None


# ============ Idol Endpoints ============

@router.get("/idols", response_model=List[IdolResponse])
def list_idols(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """List all idols."""
    idols = db.query(Idol).order_by(Idol.name_en).all()
    return idols


@router.get("/idols/{idol_id}", response_model=IdolResponse)
def get_idol(
    idol_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Get a specific idol."""
    idol = db.query(Idol).filter(Idol.id == idol_id).first()
    if not idol:
        raise HTTPException(status_code=404, detail="Idol not found")
    return idol


@router.post("/idols", response_model=IdolResponse, status_code=201)
def create_idol(
    idol_data: IdolCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Create a new idol."""
    idol = Idol(**idol_data.model_dump())
    db.add(idol)
    db.commit()
    db.refresh(idol)
    return idol


@router.put("/idols/{idol_id}", response_model=IdolResponse)
def update_idol(
    idol_id: int,
    idol_data: IdolUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Update an idol."""
    idol = db.query(Idol).filter(Idol.id == idol_id).first()
    if not idol:
        raise HTTPException(status_code=404, detail="Idol not found")

    update_data = idol_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(idol, field, value)

    db.commit()
    db.refresh(idol)
    return idol


@router.delete("/idols/{idol_id}", status_code=204)
def delete_idol(
    idol_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Delete an idol."""
    idol = db.query(Idol).filter(Idol.id == idol_id).first()
    if not idol:
        raise HTTPException(status_code=404, detail="Idol not found")

    db.delete(idol)
    db.commit()
    return None


# ============ Trait Endpoints ============

@router.get("/traits", response_model=List[TraitResponse])
def list_traits(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """List all traits."""
    traits = db.query(Trait).order_by(Trait.name_en).all()
    return traits


@router.get("/traits/{trait_id}", response_model=TraitResponse)
def get_trait(
    trait_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Get a specific trait."""
    trait = db.query(Trait).filter(Trait.id == trait_id).first()
    if not trait:
        raise HTTPException(status_code=404, detail="Trait not found")
    return trait


@router.post("/traits", response_model=TraitResponse, status_code=201)
def create_trait(
    trait_data: TraitCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Create a new trait."""
    # Check for duplicate name
    existing = db.query(Trait).filter(Trait.name_en == trait_data.name_en).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Trait with name '{trait_data.name_en}' already exists")

    trait = Trait(**trait_data.model_dump())
    db.add(trait)
    db.commit()
    db.refresh(trait)
    return trait


@router.put("/traits/{trait_id}", response_model=TraitResponse)
def update_trait(
    trait_id: int,
    trait_data: TraitUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Update a trait."""
    trait = db.query(Trait).filter(Trait.id == trait_id).first()
    if not trait:
        raise HTTPException(status_code=404, detail="Trait not found")

    # Check for duplicate name if being updated
    if trait_data.name_en is not None:
        existing = db.query(Trait).filter(
            Trait.name_en == trait_data.name_en,
            Trait.id != trait_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Trait with name '{trait_data.name_en}' already exists")

    update_data = trait_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trait, field, value)

    db.commit()
    db.refresh(trait)
    return trait


@router.delete("/traits/{trait_id}", status_code=204)
def delete_trait(
    trait_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Delete a trait."""
    trait = db.query(Trait).filter(Trait.id == trait_id).first()
    if not trait:
        raise HTTPException(status_code=404, detail="Trait not found")

    # Check if trait is used by any questions
    question_count = db.query(Question).filter(Question.trait_id == trait_id).count()
    if question_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete trait: {question_count} questions are using this trait"
        )

    db.delete(trait)
    db.commit()
    return None
