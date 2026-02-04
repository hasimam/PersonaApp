"""Add scenario set support for journey selection

Revision ID: e4c9a31df224
Revises: b6d5dd2ee2f6
Create Date: 2026-02-04 18:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e4c9a31df224"
down_revision = "b6d5dd2ee2f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "scenarios",
        sa.Column("scenario_set_code", sa.String(length=64), nullable=False, server_default="default"),
    )
    op.add_column("test_runs", sa.Column("scenario_set_code", sa.String(length=64), nullable=True))

    op.drop_constraint("uq_scenarios_version_order", "scenarios", type_="unique")
    op.create_unique_constraint(
        "uq_scenarios_version_set_order",
        "scenarios",
        ["version_id", "scenario_set_code", "order_index"],
    )
    op.create_index("ix_scenarios_version_set_code", "scenarios", ["version_id", "scenario_set_code"], unique=False)
    op.create_index(op.f("ix_test_runs_scenario_set_code"), "test_runs", ["scenario_set_code"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_test_runs_scenario_set_code"), table_name="test_runs")
    op.drop_index("ix_scenarios_version_set_code", table_name="scenarios")

    op.drop_constraint("uq_scenarios_version_set_order", "scenarios", type_="unique")
    op.create_unique_constraint("uq_scenarios_version_order", "scenarios", ["version_id", "order_index"])

    op.drop_column("test_runs", "scenario_set_code")
    op.drop_column("scenarios", "scenario_set_code")
