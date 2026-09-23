import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bundle_id = Column(String, ForeignKey("transaction_bundles.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=False)
    file_path = Column(String(500), default="")
    file_size = Column(String(50), default="0 KB")
    page_count = Column(Integer, default=1)
    ocr_status = Column(String(50), default="NOT_REQUIRED")
    clause_count = Column(Integer, default=0)
    issue_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bundle = relationship("TransactionBundle", back_populates="documents")
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan", lazy="selectin")
    clauses = relationship("Clause", back_populates="document", cascade="all, delete-orphan", lazy="selectin")


class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    raw_text = Column(Text, default="")
    layout_boxes = Column(JSON, default=list)  # Bounding boxes for OCR / highlighting

    # Relationships
    document = relationship("Document", back_populates="pages")
