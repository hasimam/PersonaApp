from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class JourneyStartRequest(BaseModel):
    version_id: Optional[str] = None


class JourneyScenarioOption(BaseModel):
    option_code: str
    option_text_en: str
    option_text_ar: Optional[str]


class JourneyScenario(BaseModel):
    scenario_code: str
    order_index: int
    scenario_text_en: str
    scenario_text_ar: Optional[str]
    options: List[JourneyScenarioOption]


class JourneyStartResponse(BaseModel):
    test_run_id: int
    version_id: str
    scenarios: List[JourneyScenario]


class JourneyAnswerSubmission(BaseModel):
    scenario_code: str
    option_code: str


class JourneySubmitAnswersRequest(BaseModel):
    version_id: str
    test_run_id: int = Field(..., ge=1)
    answers: List[JourneyAnswerSubmission] = Field(..., min_length=1)


class JourneyTopGene(BaseModel):
    gene_code: str
    name_en: str
    name_ar: Optional[str]
    desc_en: str
    desc_ar: Optional[str]
    raw_score: float
    normalized_score: float
    rank: int
    role: str


class JourneyArchetypeMatch(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_code: str
    name_en: str
    name_ar: Optional[str]
    summary_ar: Optional[str]
    similarity: float
    rank: int


class JourneyActivationItem(BaseModel):
    channel: str
    advice_id: str
    advice_type: str
    title_en: str
    title_ar: Optional[str]
    body_en: str
    body_ar: Optional[str]
    priority: int


class JourneySubmitAnswersResponse(BaseModel):
    version_id: str
    test_run_id: int
    top_genes: List[JourneyTopGene]
    archetype_matches: List[JourneyArchetypeMatch]
    activation_items: List[JourneyActivationItem]


class JourneyFeedbackRequest(BaseModel):
    test_run_id: int = Field(..., ge=1)
    judged_score: int = Field(..., ge=1, le=5)
    selected_activation_id: Optional[str] = Field(default=None, min_length=1, max_length=64)


class JourneyFeedbackResponse(BaseModel):
    test_run_id: int
    judged_score: int
    selected_activation_id: Optional[str]
    status: str
