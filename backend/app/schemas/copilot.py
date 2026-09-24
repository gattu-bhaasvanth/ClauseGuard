from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CopilotCitationSchema(BaseModel):
    documentId: str
    documentName: str
    documentType: str
    pageNumber: int
    clauseNumber: Optional[str] = None
    clauseTitle: Optional[str] = None
    excerpt: str
    relevanceScore: float

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CopilotQueryRequestSchema(BaseModel):
    query: str = Field(..., min_length=2, description="Natural language transaction question")
    topK: Optional[int] = Field(5, ge=1, le=20, description="Max context chunks to retrieve")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CopilotQueryResponseSchema(BaseModel):
    query: str
    answer: str
    grounded: bool
    refused: bool = False
    intent: str = "GENERAL_GROUNDED"
    confidence: float
    citations: List[CopilotCitationSchema] = []
    bundleId: str
    suggestedNextQuestions: List[str] = []
    disclaimer: str = (
        "ClauseGuard is an informational verification platform and does not provide legal advice. "
        "All answers are grounded in the uploaded transaction bundle."
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
