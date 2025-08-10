import qdrant_client
from .config import settings

qdrant_cli = qdrant_client.QdrantClient(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT,
    # api_key=settings.QDRANT_API_KEY, # if you have one
)
