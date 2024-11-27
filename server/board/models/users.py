from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# 사용자 등록 시 사용할 모델
class UserSignUp(SQLModel):
    user_id: str
    user_password: str
    # name : str # 기존 것. 아래것은 테스트
    username: str = Field(index=True)
    nickname: str
    # email: EmailStr # 기존것, 아래것은 테스트
    email : str
    user_img: str

class UserSignIn(SQLModel):
    user_id: str
    user_password: str  #password에서 user_password로 바꿨습니다.
    email : str  #이메일 추가입니다.(라우터에 검증이 있습니다.)