"""Add Mother's Miraat tables without changing existing journeys."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = 'd21e0a6f9310'
down_revision = 'c8a4f2e9d631'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('mother_content_releases',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('version', sa.String(80), unique=True, nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('content', JSONB, nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True)))
    op.create_table('mother_journeys',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('content_release_id', sa.String(36), sa.ForeignKey('mother_content_releases.id'), nullable=False),
        sa.Column('owner_token_hash', sa.String(64), nullable=False),
        sa.Column('age_band', sa.String(10), nullable=False),
        sa.Column('timezone', sa.String(80), nullable=False),
        sa.Column('focus_code', sa.String(30)),
        sa.Column('status', sa.String(30), nullable=False),
        sa.Column('current_day', sa.Integer, nullable=False),
        sa.Column('next_available_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True)))
    op.create_table('mother_assessments',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('journey_id', sa.String(36), sa.ForeignKey('mother_journeys.id', ondelete='CASCADE'), nullable=False),
        sa.Column('kind', sa.String(20), nullable=False),
        sa.Column('answers', JSONB, nullable=False),
        sa.Column('result', JSONB),
        sa.Column('submitted_at', sa.DateTime(timezone=True)),
        sa.UniqueConstraint('journey_id', 'kind'))
    op.create_index('ix_mother_assessments_journey_id', 'mother_assessments', ['journey_id'])
    op.create_table('mother_checkins',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('journey_id', sa.String(36), sa.ForeignKey('mother_journeys.id', ondelete='CASCADE'), nullable=False),
        sa.Column('day_number', sa.Integer, nullable=False),
        sa.Column('outcome', sa.String(30), nullable=False),
        sa.Column('repeat_requested', sa.Boolean, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('journey_id', 'day_number'))
    op.create_index('ix_mother_checkins_journey_id', 'mother_checkins', ['journey_id'])


def downgrade():
    for table in ('mother_checkins', 'mother_assessments', 'mother_journeys', 'mother_content_releases'):
        op.drop_table(table)
