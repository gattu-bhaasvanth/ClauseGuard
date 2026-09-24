import uuid
from sqlalchemy import Column, String, Integer, Float, Text, JSON, ForeignKey
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
    obligation_type = Column(String(50), default="MUTUAL")  # "BUYER", "DEVELOPER", "MUTUAL"
    page_number = Column(Integer, default=1)
    preview_text = Column(Text, default="")
    full_excerpt = Column(Text, default="")
    analysis_summary = Column(Text, default="")
    risk_details = Column(Text, nullable=True)

    # Phase 9: Intelligence Enhancement & Provenance Metadata
    confidence = Column(Float, default=1.0)
    classification_source = Column(String(50), default="DETERMINISTIC_HEURISTIC")  # "ML_TRANSFORMER" or "DETERMINISTIC_HEURISTIC"
    model_version = Column(String(100), nullable=True)
    dataset_version = Column(String(100), nullable=True)
    top_alternatives = Column(JSON, nullable=True)  # List of {"category": str, "probability": float}
    explanation_notes = Column(Text, nullable=True)

    # Relationships
    bundle = relationship("TransactionBundle", back_populates="clauses")
    document = relationship("Document", back_populates="clauses")
