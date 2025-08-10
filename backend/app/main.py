from fastapi import FastAPI, Depends
import fastapi_users

from .core.security import auth_backend, get_user_manager
from .core.config import settings
from .schemas.user import UserRead, UserCreate, UserUpdate
from .models.user import User
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

# Auth routes from fastapi-users
auth_router = fastapi_users.get_auth_router(auth_backend)
register_router = fastapi_users.get_register_router(UserRead, UserCreate)
reset_password_router = fastapi_users.get_reset_password_router()
verify_router = fastapi_users.get_verify_router(UserRead)
users_router = fastapi_users.get_users_router(
    UserRead,
    UserUpdate,
    requires_verification=False, # Set to True in production
)

from .api.v1.api import api_router

# Include routers
# Main application API
app.include_router(api_router, prefix="/api/v1")

# Auth routes
app.include_router(auth_router, prefix="/auth/jwt", tags=["Auth"])
app.include_router(register_router, prefix="/auth", tags=["Auth"])
app.include_router(reset_password_router, prefix="/auth", tags=["Auth"])
app.include_router(verify_router, prefix="/auth", tags=["Auth"])
app.include_router(users_router, prefix="/users", tags=["Users"])


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to G-AI Backend"}


@app.get("/health", tags=["Health Check"])
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
