"""Expand journey feedback scores to 1-10 and add personality match

Revision ID: 7c1e2d9a4b55
Revises: 3a1c2b9f7d10
Create Date: 2026-02-16 10:15:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7c1e2d9a4b55"
down_revision = "3a1c2b9f7d10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_feedback_judged_score_range", "feedback", type_="check")
    op.alter_column("feedback", "judged_score", new_column_name="accuracy_score")
    op.create_check_constraint(
        "ck_feedback_accuracy_score_range",
        "feedback",
        "accuracy_score >= 1 AND accuracy_score <= 10",
    )
    op.add_column("feedback", sa.Column("personality_match_score", sa.Integer(), nullable=True))
    op.create_check_constraint(
        "ck_feedback_personality_match_score_range",
        "feedback",
        "personality_match_score IS NULL OR (personality_match_score >= 1 AND personality_match_score <= 10)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_feedback_personality_match_score_range", "feedback", type_="check")
    op.drop_column("feedback", "personality_match_score")
    op.drop_constraint("ck_feedback_accuracy_score_range", "feedback", type_="check")
    op.alter_column("feedback", "accuracy_score", new_column_name="judged_score")
    op.create_check_constraint(
        "ck_feedback_judged_score_range",
        "feedback",
        "judged_score >= 1 AND judged_score <= 5",
    )
