from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_community.llms import Ollama

from ... import models, schemas
from ...core.config import settings
from ...core.db import get_async_db
from ...core.security import current_active_user
from ...services.vector_service import get_vector_service, VectorService

router = APIRouter()

class ChatRequest(BaseModel):
    document_id: int
    question: str
    model: str = "llama2" # Allow user to specify model, with a default

class ChatResponse(BaseModel):
    answer: str
    context: list[str]

@router.post("/", response_model=ChatResponse)
async def chat_with_document(
    request: ChatRequest,
    db: AsyncSession = Depends(get_async_db),
    user: models.User = Depends(current_active_user),
    vs: VectorService = Depends(get_vector_service),
):
    """
    Ask a question about a specific document.
    """
    # 1. Retrieve the document from the database to ensure it exists and belongs to the user.
    doc = await db.get(models.Document, request.document_id)
    if not doc or doc.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found or you don't have access.")

    # 2. Perform a similarity search to find relevant context.
    collection_name = str(doc.qdrant_collection_id)
    context_chunks = await vs.search(collection_name, request.question, k=3)

    if not context_chunks:
        # Handle case where no relevant context is found
        return ChatResponse(answer="I couldn't find any relevant information in the document to answer your question.", context=[])

    # 3. Prepare the prompt and generate a response using Ollama.
    llm = Ollama(base_url=settings.OLLAMA_BASE_URL, model=request.model)

    context_str = "\\n\\n---\\n\\n".join(context_chunks)
    prompt = (
        "You are a helpful AI assistant. Answer the user's question based ONLY on the following context. "
        "If the context doesn't contain the answer, say that you don't know.\\n\\n"
        f"CONTEXT:\\n{context_str}\\n\\n"
        f"QUESTION: {request.question}\\n\\n"
        "ANSWER:"
    )

    try:
        answer = llm.invoke(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with LLM: {e}")

    return ChatResponse(answer=answer, context=context_chunks)
