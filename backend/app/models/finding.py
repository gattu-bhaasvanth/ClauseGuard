import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bundle_id = Column(String, ForeignKey("transaction_bundles.id", ondelete="CASCADE"), nullable=False)
    finding_type = Column(String(50), nullable=False)  # "INCONSISTENCY" or "RISK"
    category = Column(String(50), default="GENERAL")  # "AREA", "POSSESSION", "PRICING", "PENALTY"
    severity = Column(String(50), default="HIGH")  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    impact = Column(Text, default="")
    recommendation_note = Column(Text, default="")
    
    # JSON evidence payloads
    primary_evidence = Column(JSON, nullable=False)
    secondary_evidence = Column(JSON, nullable=True)  # Populated for cross-document discrepancies
    
    detected_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bundle = relationship("TransactionBundle", back_populates="findings")
