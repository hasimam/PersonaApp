"""Add owner capabilities and temporary result shares.

Revision ID: c8a4f2e9d631
Revises: 7c1e2d9a4b55
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "c8a4f2e9d631"
down_revision = "7c1e2d9a4b55"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("test_runs", sa.Column("owner_token_hash", sa.String(length=64), nullable=True))
    op.create_table(
        "result_shares",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("test_run_id", sa.Integer(), nullable=False),
        sa.Column("token_seed", sa.String(length=64), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("language", sa.String(length=2), nullable=False),
        sa.Column("snapshot_jsonb", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["test_run_id"], ["test_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("test_run_id", "language", name="uq_result_shares_test_run_language"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(op.f("ix_result_shares_id"), "result_shares", ["id"], unique=False)
    op.create_index(op.f("ix_result_shares_test_run_id"), "result_shares", ["test_run_id"], unique=False)
    op.create_index(op.f("ix_result_shares_expires_at"), "result_shares", ["expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_result_shares_expires_at"), table_name="result_shares")
    op.drop_index(op.f("ix_result_shares_test_run_id"), table_name="result_shares")
    op.drop_index(op.f("ix_result_shares_id"), table_name="result_shares")
    op.drop_table("result_shares")
    op.drop_column("test_runs", "owner_token_hash")
