from pydantic import BaseModel
from typing import List, Dict, Optional


class TraitScore(BaseModel):
    """Individual trait score."""
    trait_id: int
    trait_name: str
    score: float


class IdolMatch(BaseModel):
    """Idol match with similarity score."""
    idol_id: int
    name: str
    description: Optional[str]
    image_url: Optional[str]
    similarity: float
    similarity_percentage: float


class TraitComparison(BaseModel):
    """Trait comparison between user and idol."""
    trait_id: int
    trait_name: str
    user_score: float
    idol_score: float
    difference: float


class ResultResponse(BaseModel):
    """Complete test result with matches and comparisons."""
    result_id: int
    user_trait_scores: List[TraitScore]
    top_matches: List[IdolMatch]
    created_at: str

    class Config:
        from_attributes = True


class DetailedMatchResponse(BaseModel):
    """Detailed comparison with a specific idol."""
    idol: IdolMatch
    trait_comparisons: List[TraitComparison]
