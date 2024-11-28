from sqlmodel import SQLModel, Field
from pydantic import BaseModel


# 사용자 등록 시 사용할 모델
class UserSignUp(SQLModel):
    user_id: str    
    user_password: str
    username: str = Field(index=True)
    nickname: str
    email: str
    user_img: str

class UserSignIn(SQLModel):
    user_id: str
    user_password: str