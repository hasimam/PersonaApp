"""Add lifecycle status to test runs

Revision ID: 9d7f6b3a2c11
Revises: e4c9a31df224
Create Date: 2026-02-05 01:10:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9d7f6b3a2c11"
down_revision = "e4c9a31df224"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "test_runs",
        sa.Column("status", sa.String(length=32), nullable=False, server_default="started"),
    )
    op.create_check_constraint(
        "ck_test_runs_status",
        "test_runs",
        "status IN ('started', 'completed', 'cancelled')",
    )
    op.create_index(op.f("ix_test_runs_status"), "test_runs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_test_runs_status"), table_name="test_runs")
    op.drop_constraint("ck_test_runs_status", "test_runs", type_="check")
    op.drop_column("test_runs", "status")
