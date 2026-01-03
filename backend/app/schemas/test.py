from pydantic import BaseModel, Field
from typing import List


class QuestionResponse(BaseModel):
    """Schema for a single question in the test."""
    id: int
    text: str
    trait_id: int
    order_index: int

    class Config:
        from_attributes = True


class TestStartResponse(BaseModel):
    """Response when starting a new test."""
    session_id: str
    questions: List[QuestionResponse]
    total_questions: int


class AnswerSubmission(BaseModel):
    """Schema for a single answer submission."""
    question_id: int = Field(..., ge=1)
    answer: int = Field(..., ge=1, le=5)


class TestSubmission(BaseModel):
    """Schema for submitting complete test responses."""
    session_id: str
    responses: List[AnswerSubmission] = Field(..., min_length=40)


class TestSubmitResponse(BaseModel):
    """Response after submitting test."""
    result_id: int
    message: str
