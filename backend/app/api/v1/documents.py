from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import typing as t

from ... import models, schemas
from ...core.db import get_async_db
from ...core.security import current_active_user
from ...services.document_processing import extract_text_from_file, split_text_into_chunks
from ...services.vector_service import get_vector_service, VectorService

router = APIRouter()

@router.post("/", response_model=schemas.DocumentRead)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
    user: models.User = Depends(current_active_user),
    vs: VectorService = Depends(get_vector_service),
):
    """
    Upload a document, process it, and create a vector index.
    """
    text = await extract_text_from_file(file)
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from file or file type is not supported.")

    # Create document record in the database
    db_document = models.Document(
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=file.size,
        owner_id=user.id
    )
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)

    # Use the generated UUID from the DB record as the collection name
    collection_name = str(db_document.qdrant_collection_id)

    # Create a collection in Qdrant and upsert the document chunks
    vs.create_collection(collection_name)
    chunks = split_text_into_chunks(text)
    vs.upsert_chunks(collection_name, chunks)

    return db_document

@router.get("/", response_model=t.List[schemas.DocumentRead])
async def list_documents(
    db: AsyncSession = Depends(get_async_db),
    user: models.User = Depends(current_active_user),
):
    """
    List all documents for the current user.
    """
    result = await db.execute(select(models.Document).where(models.Document.owner_id == user.id))
    documents = result.scalars().all()
    return documents

@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_async_db),
    user: models.User = Depends(current_active_user),
    vs: VectorService = Depends(get_vector_service),
):
    """
    Delete a document and its associated vector index.
    """
    result = await db.execute(select(models.Document).where(models.Document.id == document_id))
    db_document = result.scalar_one_or_none()

    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if db_document.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")

    # Delete collection from Qdrant
    collection_name = str(db_document.qdrant_collection_id)
    vs.client.delete_collection(collection_name=collection_name)

    # Delete from DB
    await db.delete(db_document)
    await db.commit()

    return None
