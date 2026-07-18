import base64
import hashlib
import hmac
import secrets
from datetime import timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.hybrid_engine import (
    GeneScoreResult,
    compute_prophet_traits,
    compute_quran_values,
    rank_gene_scores,
)
from app.models import (
    AdviceItem,
    ComputedGeneScore,
    ComputedModelMatch,
    Gene,
    ProphetTrait,
    QuranValue,
    SahabaModel,
    TestRun,
)
from app.schemas.share import (
    SharedActivation,
    SharedGeneItem,
    SharedJourneyResultResponse,
    SharedScoreItem,
)


def hash_capability_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def new_owner_token() -> str:
    return secrets.token_urlsafe(32)


def _base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _share_signing_key() -> bytes:
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        b"personaapp-result-share-v1",
        hashlib.sha256,
    ).digest()


def new_share_seed() -> str:
    return _base64url(secrets.token_bytes(32))


def share_token_from_seed(seed: str) -> str:
    signature = hmac.new(_share_signing_key(), seed.encode("ascii"), hashlib.sha256).digest()
    return f"{seed}.{_base64url(signature)}"


def verify_owner_token(test_run: TestRun, token: str) -> bool:
    if not test_run.owner_token_hash or not token or len(token) > 256:
        return False
    return hmac.compare_digest(test_run.owner_token_hash, hash_capability_token(token))


def _localized(en: str, ar: Optional[str], language: str) -> str:
    return ar if language == "ar" and ar else en


def _stored_gene_scores(db: Session, test_run: TestRun) -> List[GeneScoreResult]:
    rows = db.query(ComputedGeneScore).filter(ComputedGeneScore.test_run_id == test_run.id).all()
    ranked = rank_gene_scores({row.gene_code: float(row.raw_score) for row in rows})
    normalized = {row.gene_code: float(row.normalized_score) for row in rows}
    return [
        GeneScoreResult(
            gene_code=row.gene_code,
            raw_score=row.raw_score,
            normalized_score=normalized.get(row.gene_code, row.normalized_score),
            rank=row.rank,
            role=row.role,
        )
        for row in ranked
    ]


def build_shared_result_snapshot(
    db: Session,
    *,
    test_run: TestRun,
    language: str,
) -> SharedJourneyResultResponse:
    gene_scores = _stored_gene_scores(db, test_run)
    genes = {
        row.gene_code: row
        for row in db.query(Gene).filter(Gene.version_id == test_run.version_id).all()
    }
    top_genes = [
        SharedGeneItem(
            name=_localized(genes[row.gene_code].name_en, genes[row.gene_code].name_ar, language),
            score=row.normalized_score,
            rank=row.rank,
            role=row.role or "",
        )
        for row in gene_scores[:3]
        if row.gene_code in genes
    ]

    models = {
        row.model_code: row
        for row in db.query(SahabaModel).filter(SahabaModel.version_id == test_run.version_id).all()
    }
    model_rows = (
        db.query(ComputedModelMatch)
        .filter(ComputedModelMatch.test_run_id == test_run.id)
        .order_by(ComputedModelMatch.rank.asc())
        .all()
    )
    archetypes = [
        SharedScoreItem(
            name=_localized(models[row.model_code].name_en, models[row.model_code].name_ar, language),
            score=round(float(row.similarity) * 100, 2),
            rank=row.rank,
        )
        for row in model_rows
        if row.model_code in models
    ]

    quran_refs = {row.quran_value_code: row for row in db.query(QuranValue).all()}
    quran_values = [
        SharedScoreItem(
            name=_localized(quran_refs[row.quran_value_code].name_en, quran_refs[row.quran_value_code].name_ar, language),
            score=row.score,
            rank=row.rank,
        )
        for row in compute_quran_values(db, test_run.version_id, gene_scores, top_n=3)
        if row.quran_value_code in quran_refs
    ]

    prophet_refs = {row.trait_code: row for row in db.query(ProphetTrait).all()}
    prophet_traits = [
        SharedScoreItem(
            name=_localized(prophet_refs[row.trait_code].name_en, prophet_refs[row.trait_code].name_ar, language),
            score=row.score,
            rank=row.rank,
        )
        for row in compute_prophet_traits(db, test_run.version_id, gene_scores, top_n=3)
        if row.trait_code in prophet_refs
    ]

    activation = None
    if test_run.selected_activation_id:
        item = (
            db.query(AdviceItem)
            .filter(
                AdviceItem.version_id == test_run.version_id,
                AdviceItem.advice_id == test_run.selected_activation_id,
            )
            .first()
        )
        if item:
            activation = SharedActivation(
                channel=item.channel,
                title=_localized(item.title_en, item.title_ar, language),
                body=_localized(item.body_en, item.body_ar, language),
            )

    completed_at = test_run.submitted_at or test_run.created_at
    if completed_at.tzinfo is None:
        completed_at = completed_at.replace(tzinfo=timezone.utc)
    return SharedJourneyResultResponse(
        language=language,
        journey_type="deep" if test_run.version_id.startswith("v2") else "quick",
        completed_at=completed_at,
        top_genes=top_genes,
        archetype_matches=archetypes,
        quran_values=quran_values,
        prophet_traits=prophet_traits,
        selected_activation=activation,
    )
