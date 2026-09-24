from typing import Optional
from pydantic import BaseModel, ConfigDict


class ClauseResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    clauseNumber: str
    title: str
    category: str
    status: str
    severity: Optional[str] = None
    obligationType: Optional[str] = "MUTUAL"
    pageNumber: int
    previewText: str
    fullExcerpt: str
    analysisSummary: str
    riskDetails: Optional[str] = None
    confidence: Optional[float] = 1.0
    classificationSource: Optional[str] = "DETERMINISTIC_HEURISTIC"
    modelVersion: Optional[str] = None
    datasetVersion: Optional[str] = None
    topAlternatives: Optional[list] = None
    explanationNotes: Optional[str] = None
