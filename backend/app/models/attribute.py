import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ExtractedAttribute(Base):
    __tablename__ = "extracted_attributes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bundle_id = Column(String, ForeignKey("transaction_bundles.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    attribute_key = Column(String(100), nullable=False)  # e.g. "carpet_area", "possession_date"
    attribute_value = Column(String(255), nullable=False)
    normalized_value = Column(String(255), default="")
    unit = Column(String(50), default="")  # e.g. "sq.ft", "INR"
    source_page = Column(Integer, default=1)
    source_clause = Column(String(50), nullable=True)

    # Relationships
    bundle = relationship("TransactionBundle", back_populates="extracted_attributes")
