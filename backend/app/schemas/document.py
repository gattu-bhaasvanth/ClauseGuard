from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentCreateSchema(BaseModel):
    file_name: str
    document_type: str
    file_path: Optional[str] = ""
    file_size: Optional[str] = "0 KB"
    page_count: Optional[int] = 1


class DocumentResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    fileName: str
    documentType: str
    fileSize: str
    pageCount: int
    uploadedAt: str
    ocrStatus: str
    clauseCount: int
    issueCount: int


class DocumentPageResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    documentId: str
    pageNumber: int
    rawText: str
    layoutBoxes: List[Dict[str, Any]]


class DocumentIngestionResponseSchema(BaseModel):
    documentId: str
    bundleId: str
    fileName: str
    fileSize: str
    pageCount: int
    scannedPagesCount: int
    ocrStatus: str
    ocrEngineUsed: Optional[str] = None
    message: str
