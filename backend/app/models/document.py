import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# Base schema for documents, includes common fields
class DocumentBase(BaseModel):
    filename: str = Field(..., description="The name of the file.")
    content_type: str = Field(..., description="The MIME type of the file.")
    size_bytes: int = Field(..., description="The size of the file in bytes.")

# Schema for creating a new document (used for POST requests)
class DocumentCreate(DocumentBase):
    pass

# Schema for reading a document (used for GET responses)
class DocumentRead(DocumentBase):
    id: int
    qdrant_collection_id: uuid.UUID
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
