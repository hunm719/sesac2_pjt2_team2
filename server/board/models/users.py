from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
# from board.models.roles import Role

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: EmailStr
    password: str
    username: str
    # role_id: int = Field(foreign_key="role.id")  # Role 모델 참조
    # role: "Role" = Relationship(back_populates="users")

# 사용자 등록 시 사용할 모델
class UserSignUp(SQLModel):
    email: EmailStr
    password: str
    username: str

class UserSignIn(SQLModel):
    email: EmailStr
    password: str
