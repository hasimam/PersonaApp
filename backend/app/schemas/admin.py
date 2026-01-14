"""
Admin panel schemas for CRUD operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


# ============ Question Schemas ============

class QuestionBase(BaseModel):
    """Base schema for question data."""
    text_en: str = Field(..., min_length=1, description="Question text in English")
    text_ar: Optional[str] = Field(None, description="Question text in Arabic")
    trait_id: int = Field(..., gt=0, description="Associated trait ID")
    reverse_scored: bool = Field(False, description="Whether the question is reverse scored")
    order_index: int = Field(..., ge=0, description="Display order")


class QuestionCreate(QuestionBase):
    """Schema for creating a new question."""
    pass


class QuestionUpdate(BaseModel):
    """Schema for updating a question (all fields optional)."""
    text_en: Optional[str] = Field(None, min_length=1)
    text_ar: Optional[str] = None
    trait_id: Optional[int] = Field(None, gt=0)
    reverse_scored: Optional[bool] = None
    order_index: Optional[int] = Field(None, ge=0)


class QuestionResponse(QuestionBase):
    """Schema for question response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Idol Schemas ============

class IdolBase(BaseModel):
    """Base schema for idol data."""
    name_en: str = Field(..., min_length=1, max_length=100, description="Idol name in English")
    name_ar: Optional[str] = Field(None, max_length=100, description="Idol name in Arabic")
    description_en: Optional[str] = Field(None, description="Description in English")
    description_ar: Optional[str] = Field(None, description="Description in Arabic")
    image_url: Optional[str] = Field(None, max_length=255, description="Image URL")
    trait_scores: Dict[str, int] = Field(..., description="Trait scores as {trait_id: score}")


class IdolCreate(IdolBase):
    """Schema for creating a new idol."""
    pass


class IdolUpdate(BaseModel):
    """Schema for updating an idol (all fields optional)."""
    name_en: Optional[str] = Field(None, min_length=1, max_length=100)
    name_ar: Optional[str] = Field(None, max_length=100)
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=255)
    trait_scores: Optional[Dict[str, int]] = None


class IdolResponse(IdolBase):
    """Schema for idol response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Trait Schemas ============

class TraitBase(BaseModel):
    """Base schema for trait data."""
    name_en: str = Field(..., min_length=1, max_length=100, description="Trait name in English")
    name_ar: Optional[str] = Field(None, max_length=100, description="Trait name in Arabic")
    description_en: str = Field(..., min_length=1, description="Description in English")
    description_ar: Optional[str] = Field(None, description="Description in Arabic")
    high_behavior_en: Optional[str] = Field(None, description="High trait behavior in English")
    high_behavior_ar: Optional[str] = Field(None, description="High trait behavior in Arabic")
    low_behavior_en: Optional[str] = Field(None, description="Low trait behavior in English")
    low_behavior_ar: Optional[str] = Field(None, description="Low trait behavior in Arabic")


class TraitCreate(TraitBase):
    """Schema for creating a new trait."""
    pass


class TraitUpdate(BaseModel):
    """Schema for updating a trait (all fields optional)."""
    name_en: Optional[str] = Field(None, min_length=1, max_length=100)
    name_ar: Optional[str] = Field(None, max_length=100)
    description_en: Optional[str] = Field(None, min_length=1)
    description_ar: Optional[str] = None
    high_behavior_en: Optional[str] = None
    high_behavior_ar: Optional[str] = None
    low_behavior_en: Optional[str] = None
    low_behavior_ar: Optional[str] = None


class TraitResponse(TraitBase):
    """Schema for trait response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Stats Schemas ============

class AdminStats(BaseModel):
    """Schema for admin dashboard stats."""
    total_questions: int
    total_idols: int
    total_traits: int
    total_users: int
    total_tests_completed: int
    questions_with_arabic: int
    idols_with_arabic: int
    traits_with_arabic: int
