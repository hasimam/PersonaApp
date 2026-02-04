"""Add hybrid self-discovery schema

Revision ID: b6d5dd2ee2f6
Revises: 94e50da19371
Create Date: 2026-02-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "b6d5dd2ee2f6"
down_revision = "94e50da19371"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_versions",
        sa.Column("version_id", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("version_id"),
    )
    op.create_index("ix_app_versions_is_active", "app_versions", ["is_active"], unique=False)

    op.create_table(
        "genes",
        sa.Column("version_id", sa.String(length=50), nullable=False),
        sa.Column("gene_code", sa.String(length=32), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("name_ar", sa.String(length=255), nullable=True),
        sa.Column("desc_en", sa.Text(), nullable=False),
        sa.Column("desc_ar", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["version_id"], ["app_versions.version_id"]),
        sa.PrimaryKeyConstraint("version_id", "gene_code"),
    )

    op.create_table(
        "scenarios",
        sa.Column("version_id", sa.String(length=50), nullable=False),
        sa.Column("scenario_code", sa.String(length=32), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("scenario_text_en", sa.Text(), nullable=False),
        sa.Column("scenario_text_ar", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["version_id"], ["app_versions.version_id"]),
        sa.PrimaryKeyConstraint("version_id", "scenario_code"),
        sa.UniqueConstraint("version_id", "order_index", name="uq_scenarios_version_order"),
    )

    op.create_table(
        "scenario_options",
        sa.Column("version_id", sa.String(length=50), nullable=False),
        sa.Column("scenario_code", sa.String(length=32), nullable=False),
        sa.Column("option_code", sa.String(length=32), nullable=False),
        sa.Column("option_text_en", sa.Text(), nullable=False),
        sa.Column("option_text_ar", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["version_id", "scenario_code"],
            ["scenarios.version_id", "scenarios.scenario_code"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("version_id", "scenario_code", "option_code"),
    )

    op.create_table(
        "sahaba_models",
        sa.Column("version_id", sa.String(length=50), nullable=False),
        sa.Column("model_code", sa.String(length=32), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("name_ar", sa.String(length=255), nullable=True),
        sa.Column("summary_ar", sa.Text(), nullable=True),
        sa.Column("gene_vector_jsonb", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["version_id"], ["app_versions.version_id"]),
        sa.PrimaryKeyConstraint("version_id", "model_code"),
    )

    op.create_table(
        "advice_items",
        sa.Column("version_id", sa.String(length=50), nullable=False),
        sa.Column("advice_id", sa.String(length=64), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("advice_type", sa.String(length=32), nullable=False),
        sa.Column("title_en", sa.Text(), nullable=False),
        sa.Column("title_ar", sa.Text(), nullable=True),
        sa.Column("body_en", sa.Text(), nullable=False),
        sa.Column("body_ar", sa.Text(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["version_id"], ["app_versions.version_id"]),
        sa.PrimaryKeyConstraint("version_id", "advice_id"),
    )

    op.create_table(
        "option_weights",
        sa.Column("version_id", sa.String(length=50), nullable=False),
        sa.Column("scenario_code", sa.String(length=32), nullable=False),
        sa.Column("option_code", sa.String(length=32), nullable=False),
        sa.Column("gene_code", sa.String(length=32), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["version_id", "gene_code"],
            ["genes.version_id", "genes.gene_code"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["version_id", "scenario_code", "option_code"],
            [
                "scenario_options.version_id",
                "scenario_options.scenario_code",
                "scenario_options.option_code",
            ],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("version_id", "scenario_code", "option_code", "gene_code"),
    )

    op.create_table(
        "advice_triggers",
        sa.Column("version_id", sa.String(length=50), nullable=False),
        sa.Column("trigger_id", sa.String(length=64), nullable=False),
        sa.Column("trigger_type", sa.String(length=32), nullable=False),
        sa.Column("gene_code", sa.String(length=32), nullable=True),
        sa.Column("model_code", sa.String(length=32), nullable=True),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("advice_id", sa.String(length=64), nullable=False),
        sa.Column("min_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("max_score", sa.Float(), nullable=False, server_default="100"),
        sa.CheckConstraint("min_score <= max_score", name="ck_advice_triggers_score_range"),
        sa.ForeignKeyConstraint(
            ["version_id", "advice_id"],
            ["advice_items.version_id", "advice_items.advice_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["version_id", "gene_code"],
            ["genes.version_id", "genes.gene_code"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["version_id", "model_code"],
            ["sahaba_models.version_id", "sahaba_models.model_code"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["version_id"], ["app_versions.version_id"]),
        sa.PrimaryKeyConstraint("version_id", "trigger_id"),
    )

    op.create_index(
        "ix_advice_triggers_version_channel",
        "advice_triggers",
        ["version_id", "channel"],
        unique=False,
    )

    op.create_table(
        "test_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.String(length=50), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=True),
        sa.Column("selected_activation_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["version_id"], ["app_versions.version_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_test_runs_id"), "test_runs", ["id"], unique=False)
    op.create_index(op.f("ix_test_runs_session_id"), "test_runs", ["session_id"], unique=False)
    op.create_index(op.f("ix_test_runs_version_id"), "test_runs", ["version_id"], unique=False)

    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("test_run_id", sa.Integer(), nullable=False),
        sa.Column("scenario_code", sa.String(length=32), nullable=False),
        sa.Column("option_code", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["test_run_id"], ["test_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("test_run_id", "scenario_code", name="uq_answers_test_run_scenario"),
    )
    op.create_index(op.f("ix_answers_id"), "answers", ["id"], unique=False)
    op.create_index(op.f("ix_answers_test_run_id"), "answers", ["test_run_id"], unique=False)

    op.create_table(
        "computed_gene_scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("test_run_id", sa.Integer(), nullable=False),
        sa.Column("gene_code", sa.String(length=32), nullable=False),
        sa.Column("raw_score", sa.Float(), nullable=False),
        sa.Column("normalized_score", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["test_run_id"], ["test_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("test_run_id", "gene_code", name="uq_computed_gene_scores_test_run_gene"),
    )
    op.create_index(op.f("ix_computed_gene_scores_id"), "computed_gene_scores", ["id"], unique=False)
    op.create_index(op.f("ix_computed_gene_scores_test_run_id"), "computed_gene_scores", ["test_run_id"], unique=False)

    op.create_table(
        "computed_model_matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("test_run_id", sa.Integer(), nullable=False),
        sa.Column("model_code", sa.String(length=32), nullable=False),
        sa.Column("similarity", sa.Float(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["test_run_id"], ["test_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("test_run_id", "model_code", name="uq_computed_model_matches_test_run_model"),
        sa.UniqueConstraint("test_run_id", "rank", name="uq_computed_model_matches_test_run_rank"),
    )
    op.create_index(op.f("ix_computed_model_matches_id"), "computed_model_matches", ["id"], unique=False)
    op.create_index(op.f("ix_computed_model_matches_test_run_id"), "computed_model_matches", ["test_run_id"], unique=False)

    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("test_run_id", sa.Integer(), nullable=False),
        sa.Column("judged_score", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.CheckConstraint("judged_score >= 1 AND judged_score <= 5", name="ck_feedback_judged_score_range"),
        sa.ForeignKeyConstraint(["test_run_id"], ["test_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("test_run_id", name="uq_feedback_test_run"),
    )
    op.create_index(op.f("ix_feedback_id"), "feedback", ["id"], unique=False)
    op.create_index(op.f("ix_feedback_test_run_id"), "feedback", ["test_run_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_feedback_test_run_id"), table_name="feedback")
    op.drop_index(op.f("ix_feedback_id"), table_name="feedback")
    op.drop_table("feedback")

    op.drop_index(op.f("ix_computed_model_matches_test_run_id"), table_name="computed_model_matches")
    op.drop_index(op.f("ix_computed_model_matches_id"), table_name="computed_model_matches")
    op.drop_table("computed_model_matches")

    op.drop_index(op.f("ix_computed_gene_scores_test_run_id"), table_name="computed_gene_scores")
    op.drop_index(op.f("ix_computed_gene_scores_id"), table_name="computed_gene_scores")
    op.drop_table("computed_gene_scores")

    op.drop_index(op.f("ix_answers_test_run_id"), table_name="answers")
    op.drop_index(op.f("ix_answers_id"), table_name="answers")
    op.drop_table("answers")

    op.drop_index(op.f("ix_test_runs_version_id"), table_name="test_runs")
    op.drop_index(op.f("ix_test_runs_session_id"), table_name="test_runs")
    op.drop_index(op.f("ix_test_runs_id"), table_name="test_runs")
    op.drop_table("test_runs")

    op.drop_index("ix_advice_triggers_version_channel", table_name="advice_triggers")
    op.drop_table("advice_triggers")

    op.drop_table("option_weights")
    op.drop_table("advice_items")
    op.drop_table("sahaba_models")
    op.drop_table("scenario_options")
    op.drop_table("scenarios")
    op.drop_table("genes")

    op.drop_index("ix_app_versions_is_active", table_name="app_versions")
    op.drop_table("app_versions")
