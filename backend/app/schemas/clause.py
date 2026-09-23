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
    pageNumber: int
    previewText: str
    fullExcerpt: str
    analysisSummary: str
    riskDetails: Optional[str] = None
