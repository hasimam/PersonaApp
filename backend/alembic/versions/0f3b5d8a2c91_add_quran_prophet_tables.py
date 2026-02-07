"""Add quran values and prophet traits tables

Revision ID: 0f3b5d8a2c91
Revises: 9d7f6b3a2c11
Create Date: 2026-02-07 22:30:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0f3b5d8a2c91"
down_revision = "9d7f6b3a2c11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "quran_values",
        sa.Column("quran_value_code", sa.String(length=32), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("name_ar", sa.String(length=255), nullable=True),
        sa.Column("desc_en", sa.Text(), nullable=False),
        sa.Column("desc_ar", sa.Text(), nullable=True),
        sa.Column("refs", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("quran_value_code"),
    )

    op.create_table(
        "prophet_traits",
        sa.Column("trait_code", sa.String(length=32), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("name_ar", sa.String(length=255), nullable=True),
        sa.Column("desc_en", sa.Text(), nullable=False),
        sa.Column("desc_ar", sa.Text(), nullable=True),
        sa.Column("refs", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("trait_code"),
    )

    op.create_table(
        "quran_value_gene_weights",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.String(length=50), nullable=False),
        sa.Column("quran_value_code", sa.String(length=32), nullable=False),
        sa.Column("gene_weights_jsonb", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["version_id"], ["app_versions.version_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["quran_value_code"], ["quran_values.quran_value_code"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "version_id",
            "quran_value_code",
            name="uq_quran_value_gene_weights_version_value",
        ),
    )
    op.create_index(
        "ix_quran_value_gene_weights_version_id",
        "quran_value_gene_weights",
        ["version_id"],
        unique=False,
    )
    op.create_index(
        "ix_quran_value_gene_weights_quran_value_code",
        "quran_value_gene_weights",
        ["quran_value_code"],
        unique=False,
    )

    op.create_table(
        "prophet_trait_gene_weights",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.String(length=50), nullable=False),
        sa.Column("trait_code", sa.String(length=32), nullable=False),
        sa.Column("gene_weights_jsonb", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["version_id"], ["app_versions.version_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["trait_code"], ["prophet_traits.trait_code"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "version_id",
            "trait_code",
            name="uq_prophet_trait_gene_weights_version_trait",
        ),
    )
    op.create_index(
        "ix_prophet_trait_gene_weights_version_id",
        "prophet_trait_gene_weights",
        ["version_id"],
        unique=False,
    )
    op.create_index(
        "ix_prophet_trait_gene_weights_trait_code",
        "prophet_trait_gene_weights",
        ["trait_code"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_prophet_trait_gene_weights_trait_code", table_name="prophet_trait_gene_weights")
    op.drop_index("ix_prophet_trait_gene_weights_version_id", table_name="prophet_trait_gene_weights")
    op.drop_table("prophet_trait_gene_weights")

    op.drop_index("ix_quran_value_gene_weights_quran_value_code", table_name="quran_value_gene_weights")
    op.drop_index("ix_quran_value_gene_weights_version_id", table_name="quran_value_gene_weights")
    op.drop_table("quran_value_gene_weights")

    op.drop_table("prophet_traits")
    op.drop_table("quran_values")
