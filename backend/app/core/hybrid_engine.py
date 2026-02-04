"""Hybrid self-discovery scoring, matching, and activation selection."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from sqlalchemy.orm import Session

from app.models import AdviceItem, AdviceTrigger, Gene, OptionWeight, SahabaModel


ACTIVATION_CHANNELS: Tuple[str, str, str] = ("behavior", "reflection", "social")
TOP_GENE_ROLES: Tuple[str, str, str] = ("dominant", "secondary", "support")


@dataclass(frozen=True)
class JourneyAnswer:
    scenario_code: str
    option_code: str


@dataclass(frozen=True)
class GeneScoreResult:
    gene_code: str
    raw_score: float
    normalized_score: float
    rank: int
    role: Optional[str]


@dataclass(frozen=True)
class ModelMatchResult:
    model_code: str
    similarity: float
    rank: int


@dataclass(frozen=True)
class ActivationItemResult:
    channel: str
    advice_id: str
    advice_type: str
    title_en: str
    title_ar: Optional[str]
    body_en: str
    body_ar: Optional[str]
    priority: int
    trigger_id: Optional[str]
    is_fallback: bool


@dataclass(frozen=True)
class HybridComputationResult:
    gene_scores: List[GeneScoreResult]
    model_matches: List[ModelMatchResult]
    activation_items: List[ActivationItemResult]


def rank_gene_scores(raw_scores: Mapping[str, float]) -> List[GeneScoreResult]:
    """Normalize and rank gene scores deterministically."""
    if not raw_scores:
        return []

    max_raw = max(raw_scores.values())
    normalized_by_gene: Dict[str, float] = {}
    for gene_code, raw_score in raw_scores.items():
        if max_raw <= 0:
            normalized = 0.0
        else:
            normalized = (raw_score / max_raw) * 100.0
            normalized = max(0.0, min(100.0, normalized))
        normalized_by_gene[gene_code] = round(normalized, 2)

    ranked_pairs = sorted(raw_scores.items(), key=lambda pair: (-pair[1], pair[0]))
    ranked_scores: List[GeneScoreResult] = []
    for index, (gene_code, raw_score) in enumerate(ranked_pairs):
        role = TOP_GENE_ROLES[index] if index < len(TOP_GENE_ROLES) else None
        ranked_scores.append(
            GeneScoreResult(
                gene_code=gene_code,
                raw_score=round(raw_score, 4),
                normalized_score=normalized_by_gene[gene_code],
                rank=index + 1,
                role=role,
            )
        )

    return ranked_scores


def _cosine_similarity(vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError("cosine vectors must have identical dimensions")

    dot = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = sqrt(sum(a * a for a in vector_a))
    norm_b = sqrt(sum(b * b for b in vector_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _normalize_answers(answers: Sequence[JourneyAnswer]) -> List[JourneyAnswer]:
    normalized: List[JourneyAnswer] = []
    seen_scenarios = set()

    for answer in answers:
        scenario_code = answer.scenario_code.strip()
        option_code = answer.option_code.strip()
        if not scenario_code or not option_code:
            raise ValueError("each answer requires non-empty scenario_code and option_code")
        if scenario_code in seen_scenarios:
            raise ValueError(f"duplicate answer for scenario '{scenario_code}'")

        seen_scenarios.add(scenario_code)
        normalized.append(JourneyAnswer(scenario_code=scenario_code, option_code=option_code))

    return normalized


def compute_gene_scores(
    db: Session,
    version_id: str,
    answers: Sequence[JourneyAnswer],
) -> List[GeneScoreResult]:
    """Compute raw and normalized gene scores from option weights."""
    genes = db.query(Gene).filter(Gene.version_id == version_id).order_by(Gene.gene_code).all()
    if not genes:
        raise ValueError(f"no genes found for version '{version_id}'")

    raw_by_gene: Dict[str, float] = {gene.gene_code: 0.0 for gene in genes}

    weight_rows = db.query(OptionWeight).filter(OptionWeight.version_id == version_id).all()
    weight_map: Dict[Tuple[str, str], List[Tuple[str, float]]] = {}
    for row in weight_rows:
        key = (row.scenario_code, row.option_code)
        weight_map.setdefault(key, []).append((row.gene_code, float(row.weight)))

    normalized_answers = _normalize_answers(answers)
    for answer in normalized_answers:
        key = (answer.scenario_code, answer.option_code)
        if key not in weight_map:
            raise ValueError(
                f"missing option weights for answer ({answer.scenario_code}, {answer.option_code})"
            )

        for gene_code, weight in weight_map[key]:
            if gene_code not in raw_by_gene:
                raise ValueError(f"unknown gene_code '{gene_code}' in option_weights")
            raw_by_gene[gene_code] += weight

    return rank_gene_scores(raw_by_gene)


def compute_model_matches(
    db: Session,
    version_id: str,
    gene_scores: Sequence[GeneScoreResult],
    top_n: int = 3,
) -> List[ModelMatchResult]:
    """Match ranked genes against sahaba model vectors with cosine similarity."""
    if top_n <= 0:
        return []

    raw_by_gene = {score.gene_code: float(score.raw_score) for score in gene_scores}
    gene_codes = sorted(raw_by_gene.keys())
    user_vector = [raw_by_gene[gene_code] for gene_code in gene_codes]

    models = db.query(SahabaModel).filter(SahabaModel.version_id == version_id).order_by(SahabaModel.model_code).all()
    scored_models: List[Tuple[str, float]] = []

    for model in models:
        model_vector_map = model.gene_vector_jsonb or {}
        model_vector = [float(model_vector_map.get(gene_code, 0.0)) for gene_code in gene_codes]
        similarity = _cosine_similarity(user_vector, model_vector)
        scored_models.append((model.model_code, round(float(similarity), 6)))

    scored_models.sort(key=lambda pair: (-pair[1], pair[0]))
    top_models = scored_models[:top_n]

    return [
        ModelMatchResult(model_code=model_code, similarity=similarity, rank=index + 1)
        for index, (model_code, similarity) in enumerate(top_models)
    ]


def _trigger_type_matches(
    trigger_type: str,
    trigger_gene_code: Optional[str],
    trigger_model_code: Optional[str],
    role_genes: Mapping[str, str],
    top_model_code: Optional[str],
) -> bool:
    normalized_type = trigger_type.upper()

    if normalized_type == "TOP_GENE":
        return trigger_gene_code == role_genes.get("dominant")
    if normalized_type == "SECONDARY_GENE":
        return trigger_gene_code == role_genes.get("secondary")
    if normalized_type == "SUPPORT_GENE":
        return trigger_gene_code == role_genes.get("support")
    if normalized_type in {"TOP_2_GENE", "TOP2_GENE"}:
        return trigger_gene_code in {role_genes.get("dominant"), role_genes.get("secondary")}
    if normalized_type in {"TOP_MODEL", "BEST_MODEL"}:
        return trigger_model_code == top_model_code
    if normalized_type in {"ANY", "ANY_GENE", "ANY_MODEL"}:
        return True

    return False


def _score_within_range(score: float, min_score: float, max_score: float) -> bool:
    return min_score <= score <= max_score


def _select_activation_items(
    advice_items: Sequence[AdviceItem],
    triggers: Sequence[AdviceTrigger],
    gene_scores: Sequence[GeneScoreResult],
    model_matches: Sequence[ModelMatchResult],
) -> List[ActivationItemResult]:
    advice_by_id = {item.advice_id: item for item in advice_items}
    advice_by_channel: Dict[str, List[AdviceItem]] = {channel: [] for channel in ACTIVATION_CHANNELS}
    for item in advice_items:
        if item.channel in advice_by_channel:
            advice_by_channel[item.channel].append(item)

    normalized_gene_scores = {entry.gene_code: entry.normalized_score for entry in gene_scores}
    role_genes = {entry.role: entry.gene_code for entry in gene_scores if entry.role}
    model_scores = {entry.model_code: entry.similarity * 100.0 for entry in model_matches}
    top_model_code = model_matches[0].model_code if model_matches else None

    selected: List[ActivationItemResult] = []

    for channel in ACTIVATION_CHANNELS:
        candidates: List[Tuple[int, float, str, str]] = []
        for trigger in triggers:
            if trigger.channel != channel:
                continue

            advice = advice_by_id.get(trigger.advice_id)
            if advice is None:
                continue

            if not _trigger_type_matches(
                trigger_type=trigger.trigger_type,
                trigger_gene_code=trigger.gene_code,
                trigger_model_code=trigger.model_code,
                role_genes=role_genes,
                top_model_code=top_model_code,
            ):
                continue

            match_score = 0.0
            if trigger.gene_code:
                gene_score = normalized_gene_scores.get(trigger.gene_code)
                if gene_score is None:
                    continue
                if not _score_within_range(gene_score, float(trigger.min_score), float(trigger.max_score)):
                    continue
                match_score = max(match_score, gene_score)

            if trigger.model_code:
                model_score = model_scores.get(trigger.model_code)
                if model_score is None:
                    continue
                if not _score_within_range(model_score, float(trigger.min_score), float(trigger.max_score)):
                    continue
                match_score = max(match_score, model_score)

            candidates.append((int(advice.priority), round(match_score, 4), advice.advice_id, trigger.trigger_id))

        if candidates:
            candidates.sort(key=lambda item: (-item[0], -item[1], item[2], item[3]))
            _, _, advice_id, trigger_id = candidates[0]
            chosen = advice_by_id[advice_id]
            selected.append(
                ActivationItemResult(
                    channel=channel,
                    advice_id=chosen.advice_id,
                    advice_type=chosen.advice_type,
                    title_en=chosen.title_en,
                    title_ar=chosen.title_ar,
                    body_en=chosen.body_en,
                    body_ar=chosen.body_ar,
                    priority=chosen.priority,
                    trigger_id=trigger_id,
                    is_fallback=False,
                )
            )
            continue

        fallback_items = advice_by_channel.get(channel, [])
        if not fallback_items:
            raise ValueError(f"no advice_items found for activation channel '{channel}'")

        fallback_items = sorted(fallback_items, key=lambda item: (-int(item.priority), item.advice_id))
        fallback = fallback_items[0]
        selected.append(
            ActivationItemResult(
                channel=channel,
                advice_id=fallback.advice_id,
                advice_type=fallback.advice_type,
                title_en=fallback.title_en,
                title_ar=fallback.title_ar,
                body_en=fallback.body_en,
                body_ar=fallback.body_ar,
                priority=fallback.priority,
                trigger_id=None,
                is_fallback=True,
            )
        )

    return selected


def select_activation_items(
    db: Session,
    version_id: str,
    gene_scores: Sequence[GeneScoreResult],
    model_matches: Sequence[ModelMatchResult],
) -> List[ActivationItemResult]:
    """Select exactly one activation item per channel from triggers, with deterministic fallbacks."""
    advice_items = db.query(AdviceItem).filter(AdviceItem.version_id == version_id).all()
    triggers = db.query(AdviceTrigger).filter(AdviceTrigger.version_id == version_id).all()
    return _select_activation_items(advice_items, triggers, gene_scores, model_matches)


def compute_hybrid_outcome(
    db: Session,
    version_id: str,
    answers: Sequence[JourneyAnswer],
    top_model_n: int = 3,
) -> HybridComputationResult:
    """Run Phase 3 hybrid scoring + matching + activation selection."""
    gene_scores = compute_gene_scores(db=db, version_id=version_id, answers=answers)
    model_matches = compute_model_matches(
        db=db,
        version_id=version_id,
        gene_scores=gene_scores,
        top_n=top_model_n,
    )
    activation_items = select_activation_items(
        db=db,
        version_id=version_id,
        gene_scores=gene_scores,
        model_matches=model_matches,
    )

    return HybridComputationResult(
        gene_scores=gene_scores,
        model_matches=model_matches,
        activation_items=activation_items,
    )
