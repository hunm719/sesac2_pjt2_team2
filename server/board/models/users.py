from sqlmodel import SQLModel, Field

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
    email: str  # 로그인 할 때 이메일 검증으로 할 지, id 검증으로 할 지 정해야함
