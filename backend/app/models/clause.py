import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Clause(Base):
    __tablename__ = "clauses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bundle_id = Column(String, ForeignKey("transaction_bundles.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    clause_number = Column(String(50), nullable=False)  # e.g. "Clause 8.2"
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="General Terms")
    status = Column(String(50), default="VERIFIED")  # "RISK", "INCONSISTENCY", "REVIEW_REQUIRED", "VERIFIED"
    severity = Column(String(50), nullable=True)  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    page_number = Column(Integer, default=1)
    preview_text = Column(Text, default="")
    full_excerpt = Column(Text, default="")
    analysis_summary = Column(Text, default="")
    risk_details = Column(Text, nullable=True)

    # Relationships
    bundle = relationship("TransactionBundle", back_populates="clauses")
    document = relationship("Document", back_populates="clauses")
