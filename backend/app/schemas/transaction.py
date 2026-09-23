from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.document import DocumentResponseSchema
from app.schemas.finding import InconsistencyResponseSchema, RiskResponseSchema
from app.schemas.clause import ClauseResponseSchema


class PropertySummarySchema(BaseModel):
    project: str
    developer: str
    unit: str
    floor: int
    tower: str
    carpetAreaSqFt: float
    superAreaSqFt: float
    advertisedCarpetAreaSqFt: Optional[float] = None
    salePrice: float
    possessionDate: str
    gracePeriodMonths: int
    location: str


class ImportantDateSchema(BaseModel):
    id: str
    title: str
    date: str
    sourceDoc: str
    isMilestone: bool
    status: str
    description: str


class PaymentObligationSchema(BaseModel):
    id: str
    milestoneTitle: str
    percentage: float
    amount: float
    dueDateCondition: str
    status: str
    clauseCitation: str


class TransactionCreateSchema(BaseModel):
    projectName: str
    unit: str
    developer: str
    city: str
    propertyType: Optional[str] = "Residential Apartment"
    approxPrice: Optional[float] = 0.0
    carpetAreaSqFt: Optional[float] = 0.0
    superAreaSqFt: Optional[float] = 0.0


class TransactionListItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    property: PropertySummarySchema
    healthScore: int
    status: str
    documentsCount: int
    issuesCount: int
    updatedAt: str


class TransactionDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    property: PropertySummarySchema
    healthScore: int
    status: str
    documentsCount: int
    issuesCount: int
    inconsistenciesCount: int
    risksCount: int
    importantDatesCount: int
    paymentObligationsCount: int
    documents: List[DocumentResponseSchema]
    inconsistencies: List[InconsistencyResponseSchema]
    risks: List[RiskResponseSchema]
    importantDates: List[ImportantDateSchema]
    paymentObligations: List[PaymentObligationSchema]
    clauses: List[ClauseResponseSchema]
    createdAt: str
    updatedAt: str
