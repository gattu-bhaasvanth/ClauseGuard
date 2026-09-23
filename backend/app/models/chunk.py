import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bundle_id = Column(String, ForeignKey("transaction_bundles.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False, default=1)
    clause_number = Column(String(50), nullable=True)  # e.g. "Clause 8.2"
    clause_title = Column(String(255), nullable=True)
    chunk_type = Column(String(50), default="CLAUSE")  # "CLAUSE", "PAGE_SECTION"
    chunk_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # 384-dimensional float array
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bundle = relationship("TransactionBundle", back_populates="chunks")
    document = relationship("Document", back_populates="chunks")
