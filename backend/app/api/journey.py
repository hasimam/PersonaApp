from datetime import datetime, timedelta, timezone
import random
from typing import Dict, List, Optional, Sequence, Set

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.hybrid_engine import (
    GeneScoreResult,
    JourneyAnswer,
    ModelMatchResult,
    compute_hybrid_outcome,
    rank_gene_scores,
    select_activation_items,
)
from app.db.session import get_db
from app.models import (
    Answer,
    AppVersion,
    ComputedGeneScore,
    ComputedModelMatch,
    Feedback,
    Gene,
    ProphetTrait,
    QuranValue,
    SahabaModel,
    Scenario,
    ScenarioOption,
    TestRun,
)
from app.schemas.journey import (
    JourneyAnswerSubmission,
    JourneyCancelRequest,
    JourneyCancelResponse,
    JourneyArchetypeMatch,
    JourneyFeedbackRequest,
    JourneyFeedbackResponse,
    JourneyResumeRequest,
    JourneyScenario,
    JourneyScenarioOption,
    JourneyStartRequest,
    JourneyStartResponse,
    JourneySubmitAnswersRequest,
    JourneySubmitAnswersResponse,
    JourneyTopGene,
    JourneyActivationItem,
    JourneyQuranValue,
    JourneyProphetTrait,
)

router = APIRouter()
RUN_STATUS_STARTED = "started"
RUN_STATUS_COMPLETED = "completed"
RUN_STATUS_CANCELLED = "cancelled"
RUN_INACTIVITY_TTL = timedelta(hours=24)


def _resolve_version_id(
    db: Session,
    requested_version_id: Optional[str],
    journey_type: Optional[str],
) -> str:
    if requested_version_id:
        version = db.query(AppVersion).filter(AppVersion.version_id == requested_version_id).first()
        if not version:
            raise HTTPException(status_code=404, detail=f"Version '{requested_version_id}' not found")
        return version.version_id

    if journey_type:
        normalized_type = journey_type.lower()
        journey_map = {"quick": "v1", "deep": "v2"}
        mapped_version = journey_map.get(normalized_type)
        if not mapped_version:
            raise HTTPException(status_code=400, detail="Invalid journey_type")
        version = db.query(AppVersion).filter(AppVersion.version_id == mapped_version).first()
        if not version:
            raise HTTPException(status_code=404, detail=f"Version '{mapped_version}' not found")
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


def _load_scenario_set_codes(db: Session, version_id: str) -> List[str]:
    rows = (
        db.query(Scenario.scenario_set_code)
        .filter(Scenario.version_id == version_id)
        .distinct()
        .order_by(Scenario.scenario_set_code.asc())
        .all()
    )
    return [set_code for (set_code,) in rows if set_code]


def _select_scenario_set_code(set_codes: Sequence[str], test_run_id: int) -> str:
    if not set_codes:
        raise ValueError("No scenario sets available")
    return random.choice(list(set_codes))


def _touch_test_run(test_run: TestRun) -> None:
    test_run.last_activity_at = datetime.now(timezone.utc)


def _is_run_expired(test_run: TestRun) -> bool:
    last_activity = test_run.last_activity_at or test_run.created_at
    if not last_activity:
        return False
    if last_activity.tzinfo is None:
        last_activity = last_activity.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - last_activity > RUN_INACTIVITY_TTL


def _build_journey_response(
    db: Session,
    *,
    version_id: str,
    test_run_id: int,
    scenario_set_code: str,
) -> JourneyStartResponse:
    scenarios = (
        db.query(Scenario)
        .filter(
            Scenario.version_id == version_id,
            Scenario.scenario_set_code == scenario_set_code,
        )
        .order_by(Scenario.order_index.asc(), Scenario.scenario_code.asc())
        .all()
    )
    if not scenarios:
        raise HTTPException(
            status_code=400,
            detail=f"No scenarios found for version '{version_id}' and set '{scenario_set_code}'",
        )

    scenario_codes = [scenario.scenario_code for scenario in scenarios]
    options = (
        db.query(ScenarioOption)
        .filter(
            ScenarioOption.version_id == version_id,
            ScenarioOption.scenario_code.in_(scenario_codes),
        )
        .order_by(ScenarioOption.scenario_code.asc(), ScenarioOption.option_code.asc())
        .all()
    )
    options_by_scenario: Dict[str, List[ScenarioOption]] = {}
    for option in options:
        options_by_scenario.setdefault(option.scenario_code, []).append(option)

    response_scenarios: List[JourneyScenario] = []
    for scenario in scenarios:
        scenario_options = list(options_by_scenario.get(scenario.scenario_code, []))
        scenario_seed = f"{test_run_id}:{scenario.scenario_code}"
        random.Random(scenario_seed).shuffle(scenario_options)
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
                    for option in scenario_options
                ],
            )
        )

    return JourneyStartResponse(
        test_run_id=test_run_id,
        version_id=version_id,
        scenarios=response_scenarios,
    )


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


def _load_allowed_activation_ids(db: Session, test_run: TestRun) -> Set[str]:
    gene_score_rows = (
        db.query(ComputedGeneScore)
        .filter(ComputedGeneScore.test_run_id == test_run.id)
        .all()
    )
    if not gene_score_rows:
        raise HTTPException(
            status_code=400,
            detail="selected_activation_id requires completed submit-answers for this test_run",
        )

    raw_scores = {row.gene_code: float(row.raw_score) for row in gene_score_rows}
    ranked_scores = rank_gene_scores(raw_scores)
    normalized_by_gene = {row.gene_code: float(row.normalized_score) for row in gene_score_rows}
    gene_scores: List[GeneScoreResult] = [
        GeneScoreResult(
            gene_code=score.gene_code,
            raw_score=score.raw_score,
            normalized_score=normalized_by_gene.get(score.gene_code, score.normalized_score),
            rank=score.rank,
            role=score.role,
        )
        for score in ranked_scores
    ]

    model_rows = (
        db.query(ComputedModelMatch)
        .filter(ComputedModelMatch.test_run_id == test_run.id)
        .order_by(ComputedModelMatch.rank.asc(), ComputedModelMatch.model_code.asc())
        .all()
    )
    model_matches: List[ModelMatchResult] = [
        ModelMatchResult(model_code=row.model_code, similarity=float(row.similarity), rank=row.rank)
        for row in model_rows
    ]

    activation_items = select_activation_items(
        db=db,
        version_id=test_run.version_id,
        gene_scores=gene_scores,
        model_matches=model_matches,
    )
    return {item.advice_id for item in activation_items}


@router.post("/start", response_model=JourneyStartResponse)
def start_journey(
    payload: Optional[JourneyStartRequest] = None,
    db: Session = Depends(get_db),
):
    requested_version_id = payload.version_id if payload else None
    journey_type = payload.journey_type if payload else None
    version_id = _resolve_version_id(
        db=db,
        requested_version_id=requested_version_id,
        journey_type=journey_type,
    )

    scenario_set_codes = _load_scenario_set_codes(db=db, version_id=version_id)
    if not scenario_set_codes:
        raise HTTPException(status_code=400, detail=f"No scenarios found for version '{version_id}'")

    test_run = TestRun(
        version_id=version_id,
        session_id=None,
        status=RUN_STATUS_STARTED,
        last_activity_at=datetime.now(timezone.utc),
    )
    db.add(test_run)
    db.commit()
    db.refresh(test_run)

    selected_set_code = _select_scenario_set_code(
        set_codes=scenario_set_codes,
        test_run_id=test_run.id,
    )
    test_run.scenario_set_code = selected_set_code
    _touch_test_run(test_run)
    db.commit()

    return _build_journey_response(
        db=db,
        version_id=version_id,
        test_run_id=test_run.id,
        scenario_set_code=selected_set_code,
    )


@router.post("/resume", response_model=JourneyStartResponse)
def resume_journey(
    payload: JourneyResumeRequest,
    db: Session = Depends(get_db),
):
    test_run = db.query(TestRun).filter(TestRun.id == payload.test_run_id).first()
    if not test_run:
        raise HTTPException(status_code=404, detail="test_run_id not found")
    if test_run.status != RUN_STATUS_STARTED:
        raise HTTPException(status_code=400, detail="test_run is not active")
    if _is_run_expired(test_run):
        test_run.status = RUN_STATUS_CANCELLED
        db.commit()
        raise HTTPException(status_code=410, detail="test_run expired")
    if not test_run.scenario_set_code:
        raise HTTPException(status_code=400, detail="test_run has no scenario set")

    _touch_test_run(test_run)
    db.commit()

    return _build_journey_response(
        db=db,
        version_id=test_run.version_id,
        test_run_id=test_run.id,
        scenario_set_code=test_run.scenario_set_code,
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

    scenario_query = db.query(Scenario).filter(Scenario.version_id == payload.version_id)
    if test_run.scenario_set_code:
        scenario_query = scenario_query.filter(Scenario.scenario_set_code == test_run.scenario_set_code)
    scenario_rows = scenario_query.all()
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
    _touch_test_run(test_run)
    test_run.status = RUN_STATUS_COMPLETED
    db.commit()

    genes = db.query(Gene).filter(Gene.version_id == payload.version_id).all()
    genes_by_code = {gene.gene_code: gene for gene in genes}

    models = db.query(SahabaModel).filter(SahabaModel.version_id == payload.version_id).all()
    models_by_code = {model.model_code: model for model in models}

    top_gene_rows = outcome.gene_scores[:5]
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

    quran_values = db.query(QuranValue).all()
    quran_by_code = {value.quran_value_code: value for value in quran_values}
    quran_results = [
        JourneyQuranValue(
            quran_value_code=row.quran_value_code,
            name_en=quran_by_code[row.quran_value_code].name_en,
            name_ar=quran_by_code[row.quran_value_code].name_ar,
            desc_en=quran_by_code[row.quran_value_code].desc_en,
            desc_ar=quran_by_code[row.quran_value_code].desc_ar,
            score=row.score,
            rank=row.rank,
        )
        for row in outcome.quran_values
        if row.quran_value_code in quran_by_code
    ]

    prophet_traits = db.query(ProphetTrait).all()
    prophet_by_code = {trait.trait_code: trait for trait in prophet_traits}
    prophet_results = [
        JourneyProphetTrait(
            trait_code=row.trait_code,
            name_en=prophet_by_code[row.trait_code].name_en,
            name_ar=prophet_by_code[row.trait_code].name_ar,
            desc_en=prophet_by_code[row.trait_code].desc_en,
            desc_ar=prophet_by_code[row.trait_code].desc_ar,
            score=row.score,
            rank=row.rank,
        )
        for row in outcome.prophet_traits
        if row.trait_code in prophet_by_code
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
        quran_values=quran_results,
        prophet_traits=prophet_results,
        activation_items=activation_items,
    )


@router.post("/cancel", response_model=JourneyCancelResponse)
def cancel_journey(
    payload: JourneyCancelRequest,
    db: Session = Depends(get_db),
):
    test_run = db.query(TestRun).filter(TestRun.id == payload.test_run_id).first()
    if not test_run:
        raise HTTPException(status_code=404, detail="test_run_id not found")

    if test_run.status != RUN_STATUS_COMPLETED:
        test_run.status = RUN_STATUS_CANCELLED
        _touch_test_run(test_run)
        db.commit()

    return JourneyCancelResponse(
        test_run_id=test_run.id,
        status=test_run.status,
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
        allowed_activation_ids = _load_allowed_activation_ids(db=db, test_run=test_run)
        if selected_activation_id not in allowed_activation_ids:
            raise HTTPException(
                status_code=400,
                detail=f"selected_activation_id '{selected_activation_id}' was not offered for this test_run",
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

    _touch_test_run(test_run)
    db.commit()
    return JourneyFeedbackResponse(
        test_run_id=payload.test_run_id,
        judged_score=payload.judged_score,
        selected_activation_id=test_run.selected_activation_id,
        status="recorded",
    )
