"""
Idol matching algorithm using cosine similarity.
"""

import numpy as np
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from app.models import Idol, Trait


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vector_a: First vector
        vector_b: Second vector

    Returns:
        Similarity score between -1 and 1 (typically 0 to 1 for personality traits)
    """
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def trait_dict_to_vector(trait_scores: Dict[int, float], trait_ids: List[int]) -> np.ndarray:
    """
    Convert trait score dictionary to ordered numpy vector.

    Args:
        trait_scores: Dict mapping trait_id -> score
        trait_ids: Ordered list of trait IDs to use for vector

    Returns:
        Numpy array with scores in order of trait_ids
    """
    return np.array([trait_scores.get(tid, 0.0) for tid in trait_ids])


def find_top_matches(
    user_trait_scores: Dict[int, float],
    db: Session,
    top_n: int = 3
) -> List[Dict]:
    """
    Find top N most similar idols to user's personality profile.

    Args:
        user_trait_scores: User's trait scores (trait_id -> score)
        db: Database session
        top_n: Number of top matches to return

    Returns:
        List of dicts with idol info and similarity scores, sorted by similarity
        Format: [{"idol_id": int, "name": str, "similarity": float, "similarity_percentage": float}, ...]
    """
    # Get all traits to ensure consistent vector ordering
    traits = db.query(Trait).order_by(Trait.id).all()
    trait_ids = [t.id for t in traits]

    # Convert user scores to vector
    user_vector = trait_dict_to_vector(user_trait_scores, trait_ids)

    # Get all idols
    idols = db.query(Idol).all()

    # Calculate similarity for each idol
    similarities = []
    for idol in idols:
        # Convert idol trait_scores (stored as JSONB) to proper format
        # JSONB stores keys as strings, so we need to convert
        idol_scores = {int(k): float(v) for k, v in idol.trait_scores.items()}

        idol_vector = trait_dict_to_vector(idol_scores, trait_ids)
        similarity = cosine_similarity(user_vector, idol_vector)

        similarities.append({
            "idol_id": idol.id,
            "name": idol.name,
            "description": idol.description,
            "image_url": idol.image_url,
            "similarity": float(similarity),
            "similarity_percentage": round(float(similarity) * 100, 1),
            "trait_scores": idol_scores
        })

    # Sort by similarity (descending) and return top N
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    return similarities[:top_n]


def calculate_trait_differences(
    user_scores: Dict[int, float],
    idol_scores: Dict[int, float],
    db: Session
) -> List[Dict]:
    """
    Calculate trait-by-trait differences between user and idol.

    Args:
        user_scores: User's trait scores
        idol_scores: Idol's trait scores
        db: Database session

    Returns:
        List of trait comparisons with names and scores
    """
    traits = db.query(Trait).all()
    trait_map = {t.id: t.name for t in traits}

    comparisons = []
    for trait_id in user_scores.keys():
        user_score = user_scores.get(trait_id, 0)
        idol_score = idol_scores.get(trait_id, 0)

        comparisons.append({
            "trait_id": trait_id,
            "trait_name": trait_map.get(trait_id, "Unknown"),
            "user_score": user_score,
            "idol_score": idol_score,
            "difference": abs(user_score - idol_score)
        })

    # Sort by smallest difference (most similar traits first)
    comparisons.sort(key=lambda x: x["difference"])
    return comparisons
