"""
RAG Engine - Main orchestration
"""
import logging
import time
from typing import List, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.utils.pdf_processor import chunk_text, count_tokens
from app.utils.embeddings import EmbeddingsManager, FAISSVectorStore

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG Engine for document Q&A"""
    
    def __init__(self):
        self.embeddings_manager = EmbeddingsManager()
        self.vector_store = FAISSVectorStore()
        self.llm = ChatOpenAI(
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.7
        )
        self.parser = StrOutputParser()
    
    def process_document(self, text: str, index_id: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> Tuple[str, int, int]:
        """
        Process document: chunk, embed, and index
        
        Args:
            text: Document text
            index_id: Unique index identifier
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Tuple of (index_id, num_chunks, total_tokens)
        """
        try:
            logger.info(f"🔄 Processing document: {index_id}")
            
            # Chunk text
            chunks = chunk_text(text, chunk_size, chunk_overlap)
            num_chunks = len(chunks)
            
            # Generate embeddings
            embeddings, tokens_used = self.embeddings_manager.embed_texts(chunks)
            
            # Create FAISS index
            self.vector_store.create_index(embeddings, index_id)
            
            # Save metadata
            self.vector_store.save_metadata(index_id, chunks)
            
            logger.info(f"✅ Document processed: {num_chunks} chunks, {tokens_used} tokens")
            return index_id, num_chunks, tokens_used
        
        except Exception as e:
            logger.error(f"❌ Error processing document: {e}")
            raise
    
    def query(self, query_text: str, index_id: str, k: int = 5) -> Tuple[str, int, List[str]]:
        """
        Query RAG system
        
        Args:
            query_text: User query
            index_id: Document index ID
            k: Number of similar chunks to retrieve
            
        Returns:
            Tuple of (answer, tokens_used, source_chunks)
        """
        try:
            start_time = time.time()
            
            # Embed query
            query_embedding = self.embeddings_manager.embeddings.embed_query(query_text)
            
            # Search FAISS
            search_results = self.vector_store.search(index_id, query_embedding, k)
            
            # Retrieve chunks
            metadata = self.vector_store.load_metadata(index_id)
            source_chunks = [metadata[idx] for idx, _ in search_results]
            context = "\n\n".join(source_chunks)
            
            # Create prompt
            prompt = PromptTemplate.from_template(
                """You are a helpful assistant that answers questions based on the provided document context.

Context:
{context}

Question: {question}

Provide a clear, concise answer based on the context. If the answer is not in the context, say so."""
            )
            
            # Generate response
            chain = prompt | self.llm | self.parser
            answer = chain.invoke({
                "context": context,
                "question": query_text
            })
            
            response_time = int((time.time() - start_time) * 1000)  # ms
            
            # Count tokens (rough estimate)
            tokens_used = count_tokens(query_text + answer + context)
            
            logger.info(f"✅ Query answered in {response_time}ms using {tokens_used} tokens")
            return answer, tokens_used, source_chunks
        
        except Exception as e:
            logger.error(f"❌ Error querying: {e}")
            raise
