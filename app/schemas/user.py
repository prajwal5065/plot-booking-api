from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user import Role


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role = Role.agent


class UserUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
