"""add obligation_type to clauses

Revision ID: 0002_add_obligation_type
Revises: 0001_initial_schema
Create Date: 2026-09-23 15:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0002_add_obligation_type'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('clauses', sa.Column('obligation_type', sa.String(length=50), nullable=True, server_default='MUTUAL'))


def downgrade() -> None:
    op.drop_column('clauses', 'obligation_type')
