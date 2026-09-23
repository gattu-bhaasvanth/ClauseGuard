"""add raw_excerpt and confidence to extracted_attributes

Revision ID: 0003_add_attribute_excerpt_confidence
Revises: 0002_add_obligation_type
Create Date: 2026-09-23 16:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0003_add_attribute_excerpt_confidence'
down_revision: Union[str, None] = '0002_add_obligation_type'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('extracted_attributes', sa.Column('raw_excerpt', sa.Text(), nullable=True))
    op.add_column('extracted_attributes', sa.Column('confidence', sa.Float(), nullable=True, server_default='1.0'))


def downgrade() -> None:
    op.drop_column('extracted_attributes', 'confidence')
    op.drop_column('extracted_attributes', 'raw_excerpt')
