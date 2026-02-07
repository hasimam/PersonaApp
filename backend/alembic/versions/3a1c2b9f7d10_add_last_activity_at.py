"""Add last activity timestamp to test runs

Revision ID: 3a1c2b9f7d10
Revises: 0f3b5d8a2c91
Create Date: 2026-02-07 22:45:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3a1c2b9f7d10"
down_revision = "0f3b5d8a2c91"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "test_runs",
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(op.f("ix_test_runs_last_activity_at"), "test_runs", ["last_activity_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_test_runs_last_activity_at"), table_name="test_runs")
    op.drop_column("test_runs", "last_activity_at")
