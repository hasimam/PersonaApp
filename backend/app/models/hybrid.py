from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class AppVersion(Base):
    __tablename__ = "app_versions"

    version_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    genes = relationship("Gene", back_populates="app_version")
    scenarios = relationship("Scenario", back_populates="app_version")
    sahaba_models = relationship("SahabaModel", back_populates="app_version")
    advice_items = relationship("AdviceItem", back_populates="app_version")
    test_runs = relationship("TestRun", back_populates="app_version")


class Gene(Base):
    __tablename__ = "genes"

    version_id = Column(String(50), ForeignKey("app_versions.version_id"), primary_key=True)
    gene_code = Column(String(32), primary_key=True)
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    desc_en = Column(Text, nullable=False)
    desc_ar = Column(Text, nullable=True)

    app_version = relationship("AppVersion", back_populates="genes")


class Scenario(Base):
    __tablename__ = "scenarios"
    __table_args__ = (
        UniqueConstraint(
            "version_id",
            "scenario_set_code",
            "order_index",
            name="uq_scenarios_version_set_order",
        ),
    )

    version_id = Column(String(50), ForeignKey("app_versions.version_id"), primary_key=True)
    scenario_code = Column(String(32), primary_key=True)
    scenario_set_code = Column(String(64), nullable=False, default="default")
    order_index = Column(Integer, nullable=False)
    scenario_text_en = Column(Text, nullable=False)
    scenario_text_ar = Column(Text, nullable=True)

    app_version = relationship("AppVersion", back_populates="scenarios")
    options = relationship("ScenarioOption", back_populates="scenario")


class ScenarioOption(Base):
    __tablename__ = "scenario_options"
    __table_args__ = (
        ForeignKeyConstraint(
            ["version_id", "scenario_code"],
            ["scenarios.version_id", "scenarios.scenario_code"],
            ondelete="CASCADE",
        ),
    )

    version_id = Column(String(50), primary_key=True)
    scenario_code = Column(String(32), primary_key=True)
    option_code = Column(String(32), primary_key=True)
    option_text_en = Column(Text, nullable=False)
    option_text_ar = Column(Text, nullable=True)

    scenario = relationship("Scenario", back_populates="options")
    option_weights = relationship("OptionWeight", back_populates="scenario_option")


class OptionWeight(Base):
    __tablename__ = "option_weights"
    __table_args__ = (
        ForeignKeyConstraint(
            ["version_id", "scenario_code", "option_code"],
            [
                "scenario_options.version_id",
                "scenario_options.scenario_code",
                "scenario_options.option_code",
            ],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["version_id", "gene_code"],
            ["genes.version_id", "genes.gene_code"],
            ondelete="CASCADE",
        ),
    )

    version_id = Column(String(50), primary_key=True)
    scenario_code = Column(String(32), primary_key=True)
    option_code = Column(String(32), primary_key=True)
    gene_code = Column(String(32), primary_key=True)
    weight = Column(Float, nullable=False)

    scenario_option = relationship("ScenarioOption", back_populates="option_weights")


class SahabaModel(Base):
    __tablename__ = "sahaba_models"

    version_id = Column(String(50), ForeignKey("app_versions.version_id"), primary_key=True)
    model_code = Column(String(32), primary_key=True)
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    summary_ar = Column(Text, nullable=True)
    gene_vector_jsonb = Column(JSONB, nullable=False)

    app_version = relationship("AppVersion", back_populates="sahaba_models")


class AdviceItem(Base):
    __tablename__ = "advice_items"

    version_id = Column(String(50), ForeignKey("app_versions.version_id"), primary_key=True)
    advice_id = Column(String(64), primary_key=True)
    channel = Column(String(32), nullable=False)
    advice_type = Column(String(32), nullable=False)
    title_en = Column(Text, nullable=False)
    title_ar = Column(Text, nullable=True)
    body_en = Column(Text, nullable=False)
    body_ar = Column(Text, nullable=True)
    priority = Column(Integer, nullable=False, default=0)

    app_version = relationship("AppVersion", back_populates="advice_items")
    triggers = relationship("AdviceTrigger", back_populates="advice_item")


class AdviceTrigger(Base):
    __tablename__ = "advice_triggers"
    __table_args__ = (
        ForeignKeyConstraint(
            ["version_id", "advice_id"],
            ["advice_items.version_id", "advice_items.advice_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["version_id", "gene_code"],
            ["genes.version_id", "genes.gene_code"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["version_id", "model_code"],
            ["sahaba_models.version_id", "sahaba_models.model_code"],
            ondelete="CASCADE",
        ),
        CheckConstraint("min_score <= max_score", name="ck_advice_triggers_score_range"),
    )

    version_id = Column(String(50), ForeignKey("app_versions.version_id"), primary_key=True)
    trigger_id = Column(String(64), primary_key=True)
    trigger_type = Column(String(32), nullable=False)
    gene_code = Column(String(32), nullable=True)
    model_code = Column(String(32), nullable=True)
    channel = Column(String(32), nullable=False)
    advice_id = Column(String(64), nullable=False)
    min_score = Column(Float, nullable=False, default=0)
    max_score = Column(Float, nullable=False, default=100)

    advice_item = relationship("AdviceItem", back_populates="triggers")


class QuranValue(Base):
    __tablename__ = "quran_values"

    quran_value_code = Column(String(32), primary_key=True)
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    desc_en = Column(Text, nullable=False)
    desc_ar = Column(Text, nullable=True)
    refs = Column(Text, nullable=True)


class ProphetTrait(Base):
    __tablename__ = "prophet_traits"

    trait_code = Column(String(32), primary_key=True)
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    desc_en = Column(Text, nullable=False)
    desc_ar = Column(Text, nullable=True)
    refs = Column(Text, nullable=True)


class QuranValueGeneWeight(Base):
    __tablename__ = "quran_value_gene_weights"
    __table_args__ = (
        ForeignKeyConstraint(
            ["version_id"],
            ["app_versions.version_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["quran_value_code"],
            ["quran_values.quran_value_code"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("version_id", "quran_value_code", name="uq_quran_value_gene_weights_version_value"),
    )

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(String(50), nullable=False, index=True)
    quran_value_code = Column(String(32), nullable=False, index=True)
    gene_weights_jsonb = Column(JSONB, nullable=False)


class ProphetTraitGeneWeight(Base):
    __tablename__ = "prophet_trait_gene_weights"
    __table_args__ = (
        ForeignKeyConstraint(
            ["version_id"],
            ["app_versions.version_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["trait_code"],
            ["prophet_traits.trait_code"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("version_id", "trait_code", name="uq_prophet_trait_gene_weights_version_trait"),
    )

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(String(50), nullable=False, index=True)
    trait_code = Column(String(32), nullable=False, index=True)
    gene_weights_jsonb = Column(JSONB, nullable=False)


class TestRun(Base):
    __tablename__ = "test_runs"
    __table_args__ = (
        CheckConstraint("status IN ('started', 'completed', 'cancelled')", name="ck_test_runs_status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(String(50), ForeignKey("app_versions.version_id"), nullable=False, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    scenario_set_code = Column(String(64), nullable=True, index=True)
    status = Column(String(32), nullable=False, index=True, default="started", server_default="started")
    selected_activation_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)

    app_version = relationship("AppVersion", back_populates="test_runs")
    answers = relationship("Answer", back_populates="test_run")
    computed_gene_scores = relationship("ComputedGeneScore", back_populates="test_run")
    computed_model_matches = relationship("ComputedModelMatch", back_populates="test_run")
    feedback_entries = relationship("Feedback", back_populates="test_run")


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = (
        UniqueConstraint("test_run_id", "scenario_code", name="uq_answers_test_run_scenario"),
    )

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_code = Column(String(32), nullable=False)
    option_code = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    test_run = relationship("TestRun", back_populates="answers")


class ComputedGeneScore(Base):
    __tablename__ = "computed_gene_scores"
    __table_args__ = (
        UniqueConstraint("test_run_id", "gene_code", name="uq_computed_gene_scores_test_run_gene"),
    )

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    gene_code = Column(String(32), nullable=False)
    raw_score = Column(Float, nullable=False)
    normalized_score = Column(Float, nullable=False)

    test_run = relationship("TestRun", back_populates="computed_gene_scores")


class ComputedModelMatch(Base):
    __tablename__ = "computed_model_matches"
    __table_args__ = (
        UniqueConstraint("test_run_id", "model_code", name="uq_computed_model_matches_test_run_model"),
        UniqueConstraint("test_run_id", "rank", name="uq_computed_model_matches_test_run_rank"),
    )

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    model_code = Column(String(32), nullable=False)
    similarity = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)

    test_run = relationship("TestRun", back_populates="computed_model_matches")


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        UniqueConstraint("test_run_id", name="uq_feedback_test_run"),
        CheckConstraint("judged_score >= 1 AND judged_score <= 5", name="ck_feedback_judged_score_range"),
    )

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    judged_score = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    test_run = relationship("TestRun", back_populates="feedback_entries")
