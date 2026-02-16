from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class JourneyStartRequest(BaseModel):
    version_id: Optional[str] = None
    journey_type: Optional[Literal["quick", "deep"]] = None


class JourneyPreviewStartRequest(BaseModel):
    preview_token: str = Field(..., min_length=1)


class JourneyResumeRequest(BaseModel):
    test_run_id: int = Field(..., ge=1)


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


class JourneyPreviewSubmitAnswersRequest(BaseModel):
    preview_token: str = Field(..., min_length=1)
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


class JourneyQuranValue(BaseModel):
    quran_value_code: str
    name_en: str
    name_ar: Optional[str]
    desc_en: str
    desc_ar: Optional[str]
    score: float
    rank: int


class JourneyProphetTrait(BaseModel):
    trait_code: str
    name_en: str
    name_ar: Optional[str]
    desc_en: str
    desc_ar: Optional[str]
    score: float
    rank: int


class JourneySubmitAnswersResponse(BaseModel):
    version_id: str
    test_run_id: int
    top_genes: List[JourneyTopGene]
    archetype_matches: List[JourneyArchetypeMatch]
    quran_values: List[JourneyQuranValue]
    prophet_traits: List[JourneyProphetTrait]
    activation_items: List[JourneyActivationItem]


class JourneyFeedbackRequest(BaseModel):
    test_run_id: int = Field(..., ge=1)
    accuracy_score: Optional[int] = Field(default=None, ge=1, le=10)
    personality_match_score: Optional[int] = Field(default=None, ge=1, le=10)
    selected_activation_id: Optional[str] = Field(default=None, min_length=1, max_length=64)

    @model_validator(mode="after")
    def ensure_feedback_payload(self) -> "JourneyFeedbackRequest":
        if (
            self.accuracy_score is None
            and self.personality_match_score is None
            and self.selected_activation_id is None
        ):
            raise ValueError(
                "At least one of accuracy_score, personality_match_score, or selected_activation_id is required"
            )
        return self


class JourneyFeedbackResponse(BaseModel):
    test_run_id: int
    accuracy_score: Optional[int]
    personality_match_score: Optional[int]
    selected_activation_id: Optional[str]
    status: str


class JourneyCancelRequest(BaseModel):
    test_run_id: int = Field(..., ge=1)


class JourneyCancelResponse(BaseModel):
    test_run_id: int
    status: Literal["started", "completed", "cancelled"]
