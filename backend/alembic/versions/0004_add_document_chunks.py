"""add document_chunks table

Revision ID: 0004_add_document_chunks
Revises: 0003_add_attribute_excerpt_confidence
Create Date: 2026-09-23 16:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0004_add_document_chunks'
down_revision: Union[str, None] = '0003_add_attribute_excerpt_confidence'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('bundle_id', sa.String(), sa.ForeignKey('transaction_bundles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_id', sa.String(), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('clause_number', sa.String(length=50), nullable=True),
        sa.Column('clause_title', sa.String(length=255), nullable=True),
        sa.Column('chunk_type', sa.String(length=50), nullable=False, server_default='CLAUSE'),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_document_chunks_bundle_id', 'document_chunks', ['bundle_id'])
    op.create_index('ix_document_chunks_document_id', 'document_chunks', ['document_id'])


def downgrade() -> None:
    op.drop_index('ix_document_chunks_document_id', table_name='document_chunks')
    op.drop_index('ix_document_chunks_bundle_id', table_name='document_chunks')
    op.drop_table('document_chunks')
