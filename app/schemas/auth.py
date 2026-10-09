from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    username: str = Field(min_length = 3, max_length = 50)
    email: EmailStr
    password: str = Field(min_length = 8)


class UserReads(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    xp: int

    model_config = ConfigDict(from_attributes = True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str
