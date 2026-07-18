from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class CreateResultShareRequest(BaseModel):
    test_run_id: int = Field(..., ge=1)
    language: Literal["en", "ar"]


class CreateResultShareResponse(BaseModel):
    token: str
    expires_at: datetime


class SharedScoreItem(BaseModel):
    name: str
    score: float
    rank: int


class SharedGeneItem(SharedScoreItem):
    role: str


class SharedActivation(BaseModel):
    channel: str
    title: str
    body: str


class SharedJourneyResultResponse(BaseModel):
    language: Literal["en", "ar"]
    journey_type: Literal["quick", "deep"]
    completed_at: datetime
    top_genes: List[SharedGeneItem]
    archetype_matches: List[SharedScoreItem]
    quran_values: List[SharedScoreItem]
    prophet_traits: List[SharedScoreItem]
    selected_activation: Optional[SharedActivation]
