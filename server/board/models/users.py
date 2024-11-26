from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: EmailStr
    password: str
    username: str

# 사용자 등록 시 사용할 모델
class UserSignUp(SQLModel):
    email: EmailStr
    password: str
    username: str

class UserSignIn(SQLModel):
    email: EmailStr
    password: str
