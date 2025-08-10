from fastapi import FastAPI, Depends
import fastapi_users

from .core.security import auth_backend, fastapi_users_instance
from .schemas.user import UserRead, UserCreate, UserUpdate
from .core.db import Base, async_engine

app = FastAPI(
    title="G-AI Backend",
    version="0.1.0",
    description="Backend for the G-AI application.",
)

# Create DB tables on startup
@app.on_event("startup")
async def on_startup():
    async with async_engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Use for development to clear tables
        await conn.run_sync(Base.metadata.create_all)

from .api.v1.api import api_router

# Main application API
app.include_router(api_router, prefix="/api/v1")

# Auth routes from fastapi-users
app.include_router(
    fastapi_users_instance.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["Auth"]
)
app.include_router(
    fastapi_users_instance.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["Auth"]
)
app.include_router(
    fastapi_users_instance.get_reset_password_router(), prefix="/auth", tags=["Auth"]
)
app.include_router(
    fastapi_users_instance.get_verify_router(UserRead), prefix="/auth", tags=["Auth"]
)
app.include_router(
    fastapi_users_instance.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["Users"]
)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to G-AI Backend"}


@app.get("/health", tags=["Health Check"])
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
