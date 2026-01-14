"""
API endpoints for retrieving test results.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Literal

from app.db.session import get_db
from app.models import Result, Trait, Idol
from app.schemas import ResultResponse, TraitScore, IdolMatch, DetailedMatchResponse, TraitComparison
from app.core.matching import calculate_trait_differences

router = APIRouter()


@router.get("/{result_id}", response_model=ResultResponse)
def get_result(
    result_id: int,
    lang: Literal["en", "ar"] = Query(default="en", description="Language for results"),
    db: Session = Depends(get_db)
):
    """
    Retrieve test results by result ID.
    Returns user trait scores and top 3 idol matches in the requested language.
    """
    # Get result from database
    result = db.query(Result).filter(Result.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    # Get trait information
    traits = db.query(Trait).all()
    trait_map = {t.id: (t.name_ar if lang == "ar" and t.name_ar else t.name_en) for t in traits}

    # Parse trait scores (stored as string keys in JSONB)
    user_trait_scores = [
        TraitScore(
            trait_id=int(trait_id),
            trait_name=trait_map.get(int(trait_id), "Unknown"),
            score=score
        )
        for trait_id, score in result.trait_scores.items()
    ]

    # Get full idol information for top matches
    top_matches = []
    for match_data in result.top_matches:
        idol = db.query(Idol).filter(Idol.id == match_data["idol_id"]).first()
        if idol:
            # Use Arabic if available and requested, otherwise English
            name = idol.name_ar if lang == "ar" and idol.name_ar else idol.name_en
            description = idol.description_ar if lang == "ar" and idol.description_ar else idol.description_en
            top_matches.append(
                IdolMatch(
                    idol_id=idol.id,
                    name=name,
                    description=description,
                    image_url=idol.image_url,
                    similarity=match_data["similarity"],
                    similarity_percentage=round(match_data["similarity"] * 100, 1)
                )
            )

    return ResultResponse(
        result_id=result.id,
        user_trait_scores=user_trait_scores,
        top_matches=top_matches,
        created_at=result.created_at.isoformat()
    )


@router.get("/{result_id}/compare/{idol_id}", response_model=DetailedMatchResponse)
def compare_with_idol(
    result_id: int,
    idol_id: int,
    lang: Literal["en", "ar"] = Query(default="en", description="Language for results"),
    db: Session = Depends(get_db)
):
    """
    Get detailed trait-by-trait comparison between user and specific idol.
    """
    # Get result
    result = db.query(Result).filter(Result.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    # Get idol
    idol = db.query(Idol).filter(Idol.id == idol_id).first()
    if not idol:
        raise HTTPException(status_code=404, detail="Idol not found")

    # Convert user scores from JSONB (string keys) to int keys
    user_scores = {int(k): float(v) for k, v in result.trait_scores.items()}

    # Convert idol scores from JSONB
    idol_scores = {int(k): float(v) for k, v in idol.trait_scores.items()}

    # Calculate similarity (recalculate for accuracy)
    from app.core.matching import find_top_matches
    matches = find_top_matches(user_scores, db, top_n=50)
    idol_match = next((m for m in matches if m["idol_id"] == idol_id), None)

    if not idol_match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Get trait comparisons with language support
    trait_comparisons = calculate_trait_differences(user_scores, idol_scores, db, lang=lang)

    # Use Arabic if available and requested, otherwise English
    name = idol.name_ar if lang == "ar" and idol.name_ar else idol.name_en
    description = idol.description_ar if lang == "ar" and idol.description_ar else idol.description_en

    return DetailedMatchResponse(
        idol=IdolMatch(
            idol_id=idol.id,
            name=name,
            description=description,
            image_url=idol.image_url,
            similarity=idol_match["similarity"],
            similarity_percentage=idol_match["similarity_percentage"]
        ),
        trait_comparisons=[
            TraitComparison(**comp) for comp in trait_comparisons
        ]
    )
