import uuid
from qdrant_client import QdrantClient, models
from langchain_community.embeddings import OllamaEmbeddings
from ..core.config import settings
from ..core.vector_store import qdrant_cli

class VectorService:
    def __init__(self, client: QdrantClient):
        self.client = client
        self.embedding_model = OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model="nomic-embed-text"  # This should ideally be in settings
        )
        # The size for nomic-embed-text is 768
        self.embedding_size = 768

    def create_collection(self, collection_name: str):
        """Creates a new collection in Qdrant if it doesn't exist."""
        try:
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=self.embedding_size, distance=models.Distance.COSINE)
            )
            print(f"Collection '{collection_name}' created successfully.")
        except Exception as e:
            # Handle cases where collection might already exist or other errors
            print(f"Error creating collection '{collection_name}': {e}")
            # You might want to check if it exists and log that instead of failing
            # For now, we assume recreate is what we want.
            pass

    def upsert_chunks(self, collection_name: str, chunks: list[str]):
        """Generates embeddings and upserts text chunks into a collection."""
        if not chunks:
            return

        embeddings = self.embedding_model.embed_documents(chunks)

        points = [
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={"text": chunk}
            ) for embedding, chunk in zip(embeddings, chunks)
        ]

        self.client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True  # Wait for the operation to complete
        )

    async def search(self, collection_name: str, query: str, k: int = 3) -> list[str]:
        """Performs a similarity search in a collection."""
        query_embedding = self.embedding_model.embed_query(query)

        hits = self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=k
        )

        return [hit.payload['text'] for hit in hits]

# Singleton instance of the service
vector_service_instance = VectorService(client=qdrant_cli)

def get_vector_service() -> VectorService:
    """Dependency injector for the VectorService."""
    return vector_service_instance
