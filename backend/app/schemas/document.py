from pydantic import BaseModel, ConfigDict
import datetime
import uuid

class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str | None
    size_bytes: int | None
    created_at: datetime.datetime
    owner_id: int
    qdrant_collection_id: uuid.UUID

class DocumentCreate(BaseModel):
    filename: str
    content_type: str | None
    size_bytes: int | None
