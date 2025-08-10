from fastapi import Depends
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.authentication import AuthenticationBackend, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from .config import settings
from .db import get_async_db
from .transport import bearer_transport

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    # You can override methods here, e.g., for sending emails
    # async def on_after_register(self, user: User, request: Request | None = None):
    #     print(f"User {user.id} has registered.")

async def get_user_db(session: AsyncSession = Depends(get_async_db)):
    yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)

import fastapi_users

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users_instance = fastapi_users.FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Dependency to get the current active user
current_active_user = fastapi_users_instance.current_user(active=True)
