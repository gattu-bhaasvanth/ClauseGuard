from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class EvidenceCitationSchema(BaseModel):
    documentId: str
    documentName: str
    documentType: str
    pageNumber: int
    clauseNumber: Optional[str] = None
    excerpt: str
    boundingBox: Optional[Dict[str, Any]] = None


class FindingResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    bundle_id: str
    finding_type: str
    category: str
    severity: str
    title: str
    description: str
    impact: Optional[str] = ""
    recommendation_note: Optional[str] = ""
    primary_evidence: Dict[str, Any]
    secondary_evidence: Optional[Dict[str, Any]] = None
    detected_at: datetime


class InconsistencyResponseSchema(BaseModel):
    id: str
    title: str
    field: str
    category: str
    severity: str
    description: str
    primaryEvidence: EvidenceCitationSchema
    secondaryEvidence: EvidenceCitationSchema
    detectedAt: str


class RiskResponseSchema(BaseModel):
    id: str
    title: str
    clauseType: str
    severity: str
    impact: str
    explanation: str
    citation: EvidenceCitationSchema
    recommendationNote: str
