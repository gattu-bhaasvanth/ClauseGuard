"""add clause intelligence enhancements

Revision ID: 0005_add_clause_intelligence_enhancements
Revises: 0004_add_document_chunks
Create Date: 2026-09-24 20:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0005_add_clause_intelligence_enhancements'
down_revision: Union[str, None] = '0004_add_document_chunks'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('clauses') as batch_op:
        batch_op.add_column(sa.Column('confidence', sa.Float(), nullable=True, server_default='1.0'))
        batch_op.add_column(sa.Column('classification_source', sa.String(length=50), nullable=True, server_default='DETERMINISTIC_HEURISTIC'))
        batch_op.add_column(sa.Column('model_version', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('dataset_version', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('top_alternatives', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('explanation_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('clauses') as batch_op:
        batch_op.drop_column('explanation_notes')
        batch_op.drop_column('top_alternatives')
        batch_op.drop_column('dataset_version')
        batch_op.drop_column('model_version')
        batch_op.drop_column('classification_source')
        batch_op.drop_column('confidence')
