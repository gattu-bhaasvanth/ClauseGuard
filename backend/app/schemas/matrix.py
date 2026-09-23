from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.finding import InconsistencyResponseSchema, RiskResponseSchema


class DocumentAttributeValueSchema(BaseModel):
    documentId: str
    documentName: str
    documentType: str
    rawValue: str
    normalizedValue: str
    unit: Optional[str] = ""
    sourcePage: int
    sourceClause: Optional[str] = None
    rawExcerpt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ComparisonMatrixItemSchema(BaseModel):
    attributeKey: str
    label: str
    isConsistent: bool
    varianceDescription: Optional[str] = None
    valuesByDocument: List[DocumentAttributeValueSchema]

    model_config = ConfigDict(from_attributes=True)


class ComparisonMatrixResponseSchema(BaseModel):
    bundleId: str
    totalAttributesCompared: int
    inconsistentAttributesCount: int
    matrix: List[ComparisonMatrixItemSchema]

    model_config = ConfigDict(from_attributes=True)


class TransactionAnalysisResponseSchema(BaseModel):
    bundleId: str
    healthScore: int
    status: str
    totalIssues: int
    inconsistenciesCount: int
    risksCount: int
    inconsistencies: List[InconsistencyResponseSchema]
    risks: List[RiskResponseSchema]
    summary: str

    model_config = ConfigDict(from_attributes=True)
