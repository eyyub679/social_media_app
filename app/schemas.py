from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID

class PostBase(BaseModel):
    caption: str | None = None
    url: str
    file_type: str
    file_name: str
    

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    email: EmailStr

class UserRegister(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    is_active: bool
    is_superuser: bool

    model_config=ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

