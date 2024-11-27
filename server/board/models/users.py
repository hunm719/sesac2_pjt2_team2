from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# 사용자 등록 시 사용할 모델
class UserSignUp(SQLModel):
    user_id: str
    user_password: str
    name: str
    nickname: str
    email: EmailStr
    user_img: str

class UserSignIn(SQLModel):
    user_id: str
    password: str
