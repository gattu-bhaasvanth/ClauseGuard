from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ExtractedAttributeSchema(BaseModel):
    id: str
    documentId: str
    bundleId: str
    attributeKey: str
    attributeValue: str
    normalizedValue: str
    unit: Optional[str] = ""
    sourcePage: int = 1
    sourceClause: Optional[str] = None
    rawExcerpt: Optional[str] = None
    confidence: float = 1.0

    model_config = ConfigDict(from_attributes=True)


class DocumentMetadataResponseSchema(BaseModel):
    documentId: str
    bundleId: str
    attributeCount: int
    attributes: List[ExtractedAttributeSchema]

    model_config = ConfigDict(from_attributes=True)


class PaymentMilestoneItemSchema(BaseModel):
    milestone: str
    percentage: Optional[float] = None
    amount: Optional[float] = None
    dueEventOrDate: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UnifiedTransactionMetadataSchema(BaseModel):
    bundleId: str
    carpetAreaSqft: Optional[float] = None
    superAreaSqft: Optional[float] = None
    advertisedCarpetAreaSqft: Optional[float] = None
    salePrice: Optional[float] = None
    possessionDate: Optional[str] = None
    gracePeriodMonths: Optional[int] = None
    unitNumber: Optional[str] = None
    floor: Optional[int] = None
    tower: Optional[str] = None
    developer: Optional[str] = None
    buyer: Optional[str] = None
    reraNumber: Optional[str] = None
    delayedPaymentRate: Optional[float] = None
    paymentMilestones: List[PaymentMilestoneItemSchema] = []
    totalAttributesExtracted: int = 0

    model_config = ConfigDict(from_attributes=True)
