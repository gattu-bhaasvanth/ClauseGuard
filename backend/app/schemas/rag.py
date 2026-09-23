from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EvidenceCitationSchema(BaseModel):
    documentId: str
    documentName: str
    documentType: str
    pageNumber: int
    clauseNumber: Optional[str] = None
    clauseTitle: Optional[str] = None
    excerpt: str
    relevanceScore: float

    model_config = ConfigDict(from_attributes=True)


class RAGQueryRequestSchema(BaseModel):
    query: str = Field(..., min_length=2, description="Natural language question regarding the transaction documents")
    topK: Optional[int] = Field(5, ge=1, le=20, description="Number of context chunks to retrieve")

    model_config = ConfigDict(from_attributes=True)


class RAGQueryResponseSchema(BaseModel):
    query: str
    answer: str
    grounded: bool
    status: str  # "GROUNDED", "INSUFFICIENT_EVIDENCE"
    confidence: float
    citations: List[EvidenceCitationSchema] = []
    bundleId: str
    disclaimer: str = "ClauseGuard is an informational verification platform and does not provide legal advice."

    model_config = ConfigDict(from_attributes=True)


class DocumentIndexingStatusSchema(BaseModel):
    bundleId: str
    documentId: str
    documentName: str
    chunksIndexed: int
    message: str

    model_config = ConfigDict(from_attributes=True)


class ChunkResponseSchema(BaseModel):
    id: str
    bundleId: str
    documentId: str
    pageNumber: int
    clauseNumber: Optional[str] = None
    clauseTitle: Optional[str] = None
    chunkType: str
    chunkText: str
    hasEmbedding: bool
    createdAt: str

    model_config = ConfigDict(from_attributes=True)
