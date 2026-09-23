from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.finding import InconsistencyResponseSchema, RiskResponseSchema
from app.schemas.matrix import ComparisonMatrixItemSchema


class DocumentChecklistItemSchema(BaseModel):
    documentType: str
    displayName: str
    status: str  # "PRESENT", "MISSING", "RECOMMENDED"
    fileName: Optional[str] = None
    pageCount: Optional[int] = None
    description: str
    importance: str  # "MANDATORY", "REQUIRED", "RECOMMENDED", "OPTIONAL"
    impactOfMissing: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RiskCategoryScoreSchema(BaseModel):
    category: str
    score: int  # 0 to 100 (100 = safe, 0 = critical risk)
    riskLevel: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    primaryConcern: str

    model_config = ConfigDict(from_attributes=True)


class ExecutiveSummarySchema(BaseModel):
    transactionProfile: str
    keyFindingsNarrative: str
    criticalRisksNarrative: str
    recommendedActions: List[str]

    model_config = ConfigDict(from_attributes=True)


class TransactionAuditReportSchema(BaseModel):
    reportId: str
    bundleId: str
    generatedAt: str
    projectTitle: str
    unit: str
    developer: str
    city: str
    healthScore: int
    status: str
    
    # Core Sections
    executiveSummary: ExecutiveSummarySchema
    documentChecklist: List[DocumentChecklistItemSchema]
    categoryRiskScores: List[RiskCategoryScoreSchema]
    inconsistencies: List[InconsistencyResponseSchema]
    risks: List[RiskResponseSchema]
    comparisonMatrix: List[ComparisonMatrixItemSchema]

    disclaimer: str

    model_config = ConfigDict(from_attributes=True)
