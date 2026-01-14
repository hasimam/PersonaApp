"""Add bilingual support columns

Revision ID: 94e50da19371
Revises: bf4d134328da
Create Date: 2026-01-13 20:32:17.900137

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94e50da19371'
down_revision = 'bf4d134328da'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Questions table: rename text -> text_en, add text_ar
    op.alter_column('questions', 'text', new_column_name='text_en')
    op.add_column('questions', sa.Column('text_ar', sa.Text(), nullable=True))

    # Idols table: rename columns and add Arabic versions
    op.alter_column('idols', 'name', new_column_name='name_en')
    op.alter_column('idols', 'description', new_column_name='description_en')
    op.add_column('idols', sa.Column('name_ar', sa.String(100), nullable=True))
    op.add_column('idols', sa.Column('description_ar', sa.Text(), nullable=True))

    # Traits table: rename columns and add Arabic versions
    op.alter_column('traits', 'name', new_column_name='name_en')
    op.alter_column('traits', 'description', new_column_name='description_en')
    op.alter_column('traits', 'high_behavior', new_column_name='high_behavior_en')
    op.alter_column('traits', 'low_behavior', new_column_name='low_behavior_en')
    op.add_column('traits', sa.Column('name_ar', sa.String(100), nullable=True))
    op.add_column('traits', sa.Column('description_ar', sa.Text(), nullable=True))
    op.add_column('traits', sa.Column('high_behavior_ar', sa.Text(), nullable=True))
    op.add_column('traits', sa.Column('low_behavior_ar', sa.Text(), nullable=True))


def downgrade() -> None:
    # Traits table: remove Arabic columns and rename back
    op.drop_column('traits', 'low_behavior_ar')
    op.drop_column('traits', 'high_behavior_ar')
    op.drop_column('traits', 'description_ar')
    op.drop_column('traits', 'name_ar')
    op.alter_column('traits', 'low_behavior_en', new_column_name='low_behavior')
    op.alter_column('traits', 'high_behavior_en', new_column_name='high_behavior')
    op.alter_column('traits', 'description_en', new_column_name='description')
    op.alter_column('traits', 'name_en', new_column_name='name')

    # Idols table: remove Arabic columns and rename back
    op.drop_column('idols', 'description_ar')
    op.drop_column('idols', 'name_ar')
    op.alter_column('idols', 'description_en', new_column_name='description')
    op.alter_column('idols', 'name_en', new_column_name='name')

    # Questions table: remove Arabic column and rename back
    op.drop_column('questions', 'text_ar')
    op.alter_column('questions', 'text_en', new_column_name='text')
