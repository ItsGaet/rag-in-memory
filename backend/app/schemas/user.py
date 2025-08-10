from fastapi_users import schemas
from pydantic import ConfigDict

class UserRead(schemas.BaseUser[int]):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    full_name: str | None = None


class UserCreate(schemas.BaseUserCreate):
    full_name: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    full_name: str | None = None
