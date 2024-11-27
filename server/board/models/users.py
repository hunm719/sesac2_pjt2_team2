from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from board.models.roles import Role

class User(SQLModel, table=True):

    id: int = Field(default=None, primary_key=True)
    username: str = Field(..., max_length=50)
    email: str = Field(..., unique=True)
    hashed_password: str = Field(...)

# 사용자 등록 시 사용할 모델
class UserSignUp(SQLModel):
    email: EmailStr
    password: str
    username: str

class UserSignIn(SQLModel):
    email: EmailStr
    password: str
