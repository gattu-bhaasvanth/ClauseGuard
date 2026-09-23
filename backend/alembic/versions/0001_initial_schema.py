"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-23 14:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Transaction Bundles table
    op.create_table(
        'transaction_bundles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('project', sa.String(length=255), nullable=False),
        sa.Column('unit', sa.String(length=100), nullable=False),
        sa.Column('floor', sa.Integer(), nullable=True),
        sa.Column('tower', sa.String(length=100), nullable=True),
        sa.Column('developer', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('property_type', sa.String(length=100), nullable=True),
        sa.Column('carpet_area_sqft', sa.Float(), nullable=True),
        sa.Column('super_area_sqft', sa.Float(), nullable=True),
        sa.Column('advertised_carpet_area_sqft', sa.Float(), nullable=True),
        sa.Column('sale_price', sa.Float(), nullable=True),
        sa.Column('possession_date', sa.String(length=50), nullable=True),
        sa.Column('grace_period_months', sa.Integer(), nullable=True),
        sa.Column('health_score', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('bundle_id', sa.String(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('document_type', sa.String(length=100), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_size', sa.String(length=50), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('ocr_status', sa.String(length=50), nullable=True),
        sa.Column('clause_count', sa.Integer(), nullable=True),
        sa.Column('issue_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['bundle_id'], ['transaction_bundles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Document Pages table
    op.create_table(
        'document_pages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('layout_boxes', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Clauses table
    op.create_table(
        'clauses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('bundle_id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('clause_number', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('preview_text', sa.Text(), nullable=True),
        sa.Column('full_excerpt', sa.Text(), nullable=True),
        sa.Column('analysis_summary', sa.Text(), nullable=True),
        sa.Column('risk_details', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['bundle_id'], ['transaction_bundles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Extracted Attributes table
    op.create_table(
        'extracted_attributes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('bundle_id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('attribute_key', sa.String(length=100), nullable=False),
        sa.Column('attribute_value', sa.String(length=255), nullable=False),
        sa.Column('normalized_value', sa.String(length=255), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('source_page', sa.Integer(), nullable=True),
        sa.Column('source_clause', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['bundle_id'], ['transaction_bundles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Findings table
    op.create_table(
        'findings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('bundle_id', sa.String(), nullable=False),
        sa.Column('finding_type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('impact', sa.Text(), nullable=True),
        sa.Column('recommendation_note', sa.Text(), nullable=True),
        sa.Column('primary_evidence', sa.JSON(), nullable=False),
        sa.Column('secondary_evidence', sa.JSON(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['bundle_id'], ['transaction_bundles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('findings')
    op.drop_table('extracted_attributes')
    op.drop_table('clauses')
    op.drop_table('document_pages')
    op.drop_table('documents')
    op.drop_table('transaction_bundles')
