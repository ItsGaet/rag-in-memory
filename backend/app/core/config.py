import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    QDRANT_HOST: str
    QDRANT_PORT: int = 6333
    OLLAMA_BASE_URL: str

    class Config:
        env_file = ".env"
        # The env_file path is relative to where the app is run.
        # In the docker container, the working dir is /app.
        # We need to make sure the .env file is available there.
        # For local dev, we might run from the backend directory.
        # A more robust solution might be needed if we run from different places.
        # For now, let's assume the .env file is in the root of the project
        # and we will handle its location in docker-compose.
        # Let's adjust the docker-compose to copy the .env file.
        # No, docker-compose's `env_file` directive handles this.
        # The python code will receive them as environment variables.
        # So we don't need to specify `env_file` here.
        # Pydantic-settings will automatically read from environment variables.
        pass

settings = Settings()
