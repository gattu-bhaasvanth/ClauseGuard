import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base


class TransactionBundle(Base):
    __tablename__ = "transaction_bundles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    project = Column(String(255), nullable=False)
    unit = Column(String(100), nullable=False)
    floor = Column(Integer, default=1)
    tower = Column(String(100), default="")
    developer = Column(String(255), nullable=False)
    city = Column(String(100), default="")
    location = Column(String(255), default="")
    property_type = Column(String(100), default="Residential Apartment")
    
    # Financials & Areas
    carpet_area_sqft = Column(Float, default=0.0)
    super_area_sqft = Column(Float, default=0.0)
    advertised_carpet_area_sqft = Column(Float, nullable=True)
    sale_price = Column(Float, default=0.0)
    possession_date = Column(String(50), default="")
    grace_period_months = Column(Integer, default=6)

    # Health & Status
    health_score = Column(Integer, default=100)
    status = Column(String(50), default="ANALYSIS_COMPLETE")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="bundle", cascade="all, delete-orphan", lazy="selectin")
    clauses = relationship("Clause", back_populates="bundle", cascade="all, delete-orphan", lazy="selectin")
    findings = relationship("Finding", back_populates="bundle", cascade="all, delete-orphan", lazy="selectin")
    extracted_attributes = relationship("ExtractedAttribute", back_populates="bundle", cascade="all, delete-orphan", lazy="selectin")
    chunks = relationship("DocumentChunk", back_populates="bundle", cascade="all, delete-orphan", lazy="selectin")
