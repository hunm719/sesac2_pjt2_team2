from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    user_id: str
    password: str
    name: str
    nickname: Optional[str] = None
    email: EmailStr
    user_img: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    user_id: str
    name: str
    nickname: str
    email: EmailStr
    user_img: Optional[str]
    is_admin: bool

    class Config:
        orm_mode = True
