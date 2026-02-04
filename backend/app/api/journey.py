from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Set

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.hybrid_engine import JourneyAnswer, compute_hybrid_outcome
from app.db.session import get_db
from app.models import (
    Answer,
    AdviceItem,
    AppVersion,
    ComputedGeneScore,
    ComputedModelMatch,
    Feedback,
    Gene,
    SahabaModel,
    Scenario,
    ScenarioOption,
    TestRun,
)
from app.schemas.journey import (
    JourneyAnswerSubmission,
    JourneyArchetypeMatch,
    JourneyFeedbackRequest,
    JourneyFeedbackResponse,
    JourneyScenario,
    JourneyScenarioOption,
    JourneyStartRequest,
    JourneyStartResponse,
    JourneySubmitAnswersRequest,
    JourneySubmitAnswersResponse,
    JourneyTopGene,
    JourneyActivationItem,
)

router = APIRouter()


def _resolve_version_id(db: Session, requested_version_id: Optional[str]) -> str:
    if requested_version_id:
        version = db.query(AppVersion).filter(AppVersion.version_id == requested_version_id).first()
        if not version:
            raise HTTPException(status_code=404, detail=f"Version '{requested_version_id}' not found")
        return version.version_id

    active_versions = (
        db.query(AppVersion)
        .filter(AppVersion.is_active.is_(True))
        .order_by(AppVersion.published_at.desc(), AppVersion.version_id.desc())
        .all()
    )
    if not active_versions:
        raise HTTPException(status_code=400, detail="No active app version found")
    return active_versions[0].version_id


def _load_option_codes_by_scenario(db: Session, version_id: str) -> Dict[str, Set[str]]:
    rows = db.query(ScenarioOption).filter(ScenarioOption.version_id == version_id).all()
    option_codes_by_scenario: Dict[str, Set[str]] = {}
    for row in rows:
        option_codes_by_scenario.setdefault(row.scenario_code, set()).add(row.option_code)
    return option_codes_by_scenario


def _validate_answer_payload(
    answers: Sequence[JourneyAnswerSubmission],
    valid_scenario_codes: Set[str],
    option_codes_by_scenario: Dict[str, Set[str]],
) -> List[JourneyAnswer]:
    seen_scenarios: Set[str] = set()
    normalized_answers: List[JourneyAnswer] = []

    for answer in answers:
        scenario_code = answer.scenario_code.strip()
        option_code = answer.option_code.strip()
        if not scenario_code or not option_code:
            raise ValueError("Each answer must include non-empty scenario_code and option_code")
        if scenario_code in seen_scenarios:
            raise ValueError(f"Duplicate answer for scenario '{scenario_code}'")
        if scenario_code not in valid_scenario_codes:
            raise ValueError(f"Unknown scenario_code '{scenario_code}'")

        valid_options = option_codes_by_scenario.get(scenario_code, set())
        if option_code not in valid_options:
            raise ValueError(
                f"Unknown option_code '{option_code}' for scenario '{scenario_code}'"
            )

        seen_scenarios.add(scenario_code)
        normalized_answers.append(JourneyAnswer(scenario_code=scenario_code, option_code=option_code))

    missing_scenarios = sorted(valid_scenario_codes - seen_scenarios)
    if missing_scenarios:
        preview = ", ".join(missing_scenarios[:3])
        if len(missing_scenarios) > 3:
            preview += ", ..."
        raise ValueError(f"Missing answers for scenarios: {preview}")

    return normalized_answers


@router.post("/start", response_model=JourneyStartResponse)
def start_journey(
    payload: Optional[JourneyStartRequest] = None,
    db: Session = Depends(get_db),
):
    requested_version_id = payload.version_id if payload else None
    version_id = _resolve_version_id(db=db, requested_version_id=requested_version_id)

    scenarios = (
        db.query(Scenario)
        .filter(Scenario.version_id == version_id)
        .order_by(Scenario.order_index.asc())
        .all()
    )
    if not scenarios:
        raise HTTPException(status_code=400, detail=f"No scenarios found for version '{version_id}'")

    options = (
        db.query(ScenarioOption)
        .filter(ScenarioOption.version_id == version_id)
        .order_by(ScenarioOption.scenario_code.asc(), ScenarioOption.option_code.asc())
        .all()
    )
    options_by_scenario: Dict[str, List[ScenarioOption]] = {}
    for option in options:
        options_by_scenario.setdefault(option.scenario_code, []).append(option)

    test_run = TestRun(version_id=version_id, session_id=None)
    db.add(test_run)
    db.commit()
    db.refresh(test_run)

    response_scenarios: List[JourneyScenario] = []
    for scenario in scenarios:
        response_scenarios.append(
            JourneyScenario(
                scenario_code=scenario.scenario_code,
                order_index=scenario.order_index,
                scenario_text_en=scenario.scenario_text_en,
                scenario_text_ar=scenario.scenario_text_ar,
                options=[
                    JourneyScenarioOption(
                        option_code=option.option_code,
                        option_text_en=option.option_text_en,
                        option_text_ar=option.option_text_ar,
                    )
                    for option in options_by_scenario.get(scenario.scenario_code, [])
                ],
            )
        )

    return JourneyStartResponse(
        test_run_id=test_run.id,
        version_id=version_id,
        scenarios=response_scenarios,
    )


@router.post("/submit-answers", response_model=JourneySubmitAnswersResponse)
def submit_journey_answers(
    payload: JourneySubmitAnswersRequest,
    db: Session = Depends(get_db),
):
    test_run = db.query(TestRun).filter(TestRun.id == payload.test_run_id).first()
    if not test_run:
        raise HTTPException(status_code=404, detail="test_run_id not found")
    if test_run.version_id != payload.version_id:
        raise HTTPException(status_code=400, detail="version_id does not match test_run_id")

    scenario_rows = db.query(Scenario).filter(Scenario.version_id == payload.version_id).all()
    valid_scenario_codes = {row.scenario_code for row in scenario_rows}
    if not valid_scenario_codes:
        raise HTTPException(status_code=400, detail=f"No scenarios found for version '{payload.version_id}'")

    option_codes_by_scenario = _load_option_codes_by_scenario(db=db, version_id=payload.version_id)
    try:
        normalized_answers = _validate_answer_payload(
            answers=payload.answers,
            valid_scenario_codes=valid_scenario_codes,
            option_codes_by_scenario=option_codes_by_scenario,
        )
        outcome = compute_hybrid_outcome(
            db=db,
            version_id=payload.version_id,
            answers=normalized_answers,
            top_model_n=3,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    db.query(Answer).filter(Answer.test_run_id == test_run.id).delete(synchronize_session=False)
    db.query(ComputedGeneScore).filter(ComputedGeneScore.test_run_id == test_run.id).delete(
        synchronize_session=False
    )
    db.query(ComputedModelMatch).filter(ComputedModelMatch.test_run_id == test_run.id).delete(
        synchronize_session=False
    )

    for answer in normalized_answers:
        db.add(
            Answer(
                test_run_id=test_run.id,
                scenario_code=answer.scenario_code,
                option_code=answer.option_code,
            )
        )

    for score in outcome.gene_scores:
        db.add(
            ComputedGeneScore(
                test_run_id=test_run.id,
                gene_code=score.gene_code,
                raw_score=score.raw_score,
                normalized_score=score.normalized_score,
            )
        )

    for match in outcome.model_matches:
        db.add(
            ComputedModelMatch(
                test_run_id=test_run.id,
                model_code=match.model_code,
                similarity=match.similarity,
                rank=match.rank,
            )
        )

    test_run.submitted_at = datetime.now(timezone.utc)
    db.commit()

    genes = db.query(Gene).filter(Gene.version_id == payload.version_id).all()
    genes_by_code = {gene.gene_code: gene for gene in genes}

    models = db.query(SahabaModel).filter(SahabaModel.version_id == payload.version_id).all()
    models_by_code = {model.model_code: model for model in models}

    top_gene_rows = [row for row in outcome.gene_scores if row.role in {"dominant", "secondary", "support"}][:3]
    top_genes = [
        JourneyTopGene(
            gene_code=row.gene_code,
            name_en=genes_by_code[row.gene_code].name_en,
            name_ar=genes_by_code[row.gene_code].name_ar,
            desc_en=genes_by_code[row.gene_code].desc_en,
            desc_ar=genes_by_code[row.gene_code].desc_ar,
            raw_score=row.raw_score,
            normalized_score=row.normalized_score,
            rank=row.rank,
            role=row.role or "",
        )
        for row in top_gene_rows
    ]

    archetype_matches = [
        JourneyArchetypeMatch(
            model_code=match.model_code,
            name_en=models_by_code[match.model_code].name_en,
            name_ar=models_by_code[match.model_code].name_ar,
            summary_ar=models_by_code[match.model_code].summary_ar,
            similarity=match.similarity,
            rank=match.rank,
        )
        for match in outcome.model_matches
        if match.model_code in models_by_code
    ]

    activation_items = [
        JourneyActivationItem(
            channel=item.channel,
            advice_id=item.advice_id,
            advice_type=item.advice_type,
            title_en=item.title_en,
            title_ar=item.title_ar,
            body_en=item.body_en,
            body_ar=item.body_ar,
            priority=item.priority,
        )
        for item in outcome.activation_items
    ]

    return JourneySubmitAnswersResponse(
        version_id=payload.version_id,
        test_run_id=test_run.id,
        top_genes=top_genes,
        archetype_matches=archetype_matches,
        activation_items=activation_items,
    )


@router.post("/feedback", response_model=JourneyFeedbackResponse)
def submit_journey_feedback(
    payload: JourneyFeedbackRequest,
    db: Session = Depends(get_db),
):
    test_run = db.query(TestRun).filter(TestRun.id == payload.test_run_id).first()
    if not test_run:
        raise HTTPException(status_code=404, detail="test_run_id not found")

    selected_activation_id = (
        payload.selected_activation_id.strip() if payload.selected_activation_id else None
    )
    if selected_activation_id:
        activation_item = (
            db.query(AdviceItem.advice_id)
            .filter(
                AdviceItem.version_id == test_run.version_id,
                AdviceItem.advice_id == selected_activation_id,
            )
            .first()
        )
        if not activation_item:
            raise HTTPException(
                status_code=400,
                detail=f"selected_activation_id '{selected_activation_id}' not found",
            )
        test_run.selected_activation_id = selected_activation_id

    feedback = db.query(Feedback).filter(Feedback.test_run_id == payload.test_run_id).first()
    if feedback:
        feedback.judged_score = payload.judged_score
    else:
        db.add(
            Feedback(
                test_run_id=payload.test_run_id,
                judged_score=payload.judged_score,
            )
        )

    db.commit()
    return JourneyFeedbackResponse(
        test_run_id=payload.test_run_id,
        judged_score=payload.judged_score,
        selected_activation_id=test_run.selected_activation_id,
        status="recorded",
    )
