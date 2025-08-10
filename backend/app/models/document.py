import uuid
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from ..core.db import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)
    content_type = Column(String)
    size_bytes = Column(Integer)

    # We can use a UUID for the collection name to ensure uniqueness
    qdrant_collection_id = Column(UUID(as_uuid=True), primary_key=False, default=uuid.uuid4, unique=True)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User") #, back_populates="documents")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
