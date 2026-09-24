from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class RiskVectorItemSchema(BaseModel):
    id: str
    name: str
    score: int  # 0-100 (100 = completely safe, 0 = severe risk)
    riskLevel: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    primaryConcern: str
    quantifiedStat: Optional[str] = None
    findingIds: List[str] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FinancialExposureBreakdownSchema(BaseModel):
    totalFinancialAtRisk: float
    totalFinancialAtRiskFormatted: str
    baseConsideration: float
    baseConsiderationFormatted: str
    earnestMoneyForfeitRisk: float
    earnestMoneyForfeitRiskFormatted: str
    statutoryForfeitLimit: float
    statutoryForfeitLimitFormatted: str
    excessForfeitExposure: float
    excessForfeitExposureFormatted: str
    delayInterestRateBuyer: float
    delayCompensationRateDeveloper: float
    monthlyAsymmetryCost: float
    monthlyAsymmetryCostFormatted: str
    areaDiscrepancyCostImpact: float
    areaDiscrepancyCostImpactFormatted: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PriorityActionItemSchema(BaseModel):
    id: str
    title: str
    category: str  # "NEGOTIATION", "DOCUMENT_REQUEST", "LEGAL_REVIEW", "PAYMENT_HOLD"
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    description: str
    clauseReference: Optional[str] = None
    documentName: Optional[str] = None
    recommendedAction: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TransactionCommandCenterResponse(BaseModel):
    bundleId: str
    projectName: str
    unitNumber: str
    developerName: str
    healthScore: int
    riskLevel: str
    financialExposure: FinancialExposureBreakdownSchema
    riskVectors: List[RiskVectorItemSchema]
    priorityActions: List[PriorityActionItemSchema]
    missingDocumentsCount: int
    totalDocumentsCount: int
    totalClausesAnalyzed: int
    totalFindingsCount: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ExplainableRiskLineageSchema(BaseModel):
    documentName: str
    pageNumber: int
    clauseNumber: Optional[str] = None
    clauseTitle: Optional[str] = None
    findingId: str
    verbatimExcerpt: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ExplainableRiskResponseSchema(BaseModel):
    findingId: str
    title: str
    severity: str
    category: str
    plainEnglishHarm: str
    statutoryBenchmark: str
    quantifiedImpact: str
    lineage: ExplainableRiskLineageSchema
    primaryEvidence: Dict[str, Any]
    secondaryEvidence: Optional[Dict[str, Any]] = None
    recommendedNegotiationScript: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TimelineEventSchema(BaseModel):
    id: str
    title: str
    eventDate: Optional[str] = None
    dateType: str  # "CONTRACTUAL", "INFERRED", "MARKETING", "CONFLICTING", "UNCERTAIN"
    status: str  # "PAST", "UPCOMING", "TENTATIVE"
    description: str
    documentName: Optional[str] = None
    pageNumber: Optional[int] = None
    clauseReference: Optional[str] = None
    linkedObligationAmount: Optional[float] = None
    linkedObligationFormatted: Optional[str] = None
    conflictingDate: Optional[str] = None
    conflictDetails: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TimelineResponseSchema(BaseModel):
    bundleId: str
    events: List[TimelineEventSchema]
    totalEvents: int
    conflictingEventsCount: int
    contractualEventsCount: int
    marketingEventsCount: int
    inferredEventsCount: int
    uncertainEventsCount: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BriefSectionSchema(BaseModel):
    sectionNumber: int
    sectionKey: str
    title: str
    summary: str
    bulletPoints: List[str]
    evidenceLineage: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TransactionBriefSchema(BaseModel):
    briefId: str
    bundleId: str
    generatedAt: str
    project: str
    unit: str
    developer: str
    healthScore: int
    riskLevel: str
    totalFinancialExposure: str
    sections: List[BriefSectionSchema]
    disclaimer: str = (
        "ClauseGuard Transaction Brief is an automated forensic intelligence synthesis "
        "and does not constitute formal legal counsel. All figures and assertions cite "
        "evidence extracted from the uploaded transaction bundle."
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
