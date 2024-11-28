from fastapi import APIRouter, HTTPException, status, Depends
from board.models.events import User
from board.models.users import UserSignIn, UserSignUp
from board.database.connection import get_session
from sqlmodel import select, delete
from board.auth.hash_password import HashPassword
from board.auth.jwt_handler import create_jwt_token
from board.auth.authenticate import authenticate, get_current_user_role
from board.models.roles import Role
from board.models.permissions import Permission
from typing import List

user_router = APIRouter()
hash_password = HashPassword()


# 이메일 중복 검사 함수
def check_duplicate_email(session, email):

   statement = select(User).where(User.email == email)
   if session.exec(statement).first():
     raise HTTPException(
         status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 이메일입니다."
    )

# 아이디 중복 검사 함수 
def check_duplicate_username(session, username):
    
    statement = select(User).where(User.username == username)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 아이디입니다."
        )

# 현재 사용자 정보를 가져오기
@user_router.get("/me")
async def get_current_user(user_id: int = Depends(authenticate)):

    return {"user_id": user_id}

# 사용자 등록
@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_new_user(data: UserSignUp, session=Depends(get_session)) -> dict:
    check_duplicate_email(session, data.email)
    check_duplicate_username(session, data.username)

     # 비밀번호 해싱
    hashed_password = hash_password.hash_password(data.user_password)

     # 사용자 생성
    new_user = User(
        user_id=data.user_id,  # user_id는 필수
        user_password=hashed_password,  # 비밀번호는 해시화하여 저장
        username=data.username,
        nickname=data.nickname,
        email=data.email,
        user_img=data.user_img  # user_img 추가
    )
    
    # 데이터베이스에 사용자 추가
    session.add(new_user)
    session.commit()
    
    return {"message": "사용자가 정상적으로 등록되었습니다."}

# 로그인 처리
@user_router.post("/signin")
async def sign_in(data: UserSignIn, session=Depends(get_session)) -> dict:
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()

    # 아이디 확인
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 아이디가 존재하지 않습니다.",
        )

    # 패스워드 확인
    if not hash_password.verify_password(data.user_password, user.user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치하지 않습니다.",
        )

    # 토큰 생성
    try:
        token = create_jwt_token(user.email, user.id, user.role)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"토큰 생성 중 오류가 발생했습니다: {str(e)}",
        )

    #아래에 토큰부분에 user.role을 추가했습니다.
    return {
        "message": "로그인에 성공했습니다.",
        "access_token": token
    }

# 사용자 정보 수정 (username으로 조회)
@user_router.put("/{username}", status_code=status.HTTP_200_OK)
async def update_user(username: str, data: UserSignUp, session=Depends(get_session), user_role: Role = Depends(get_current_user_role)):
    Permission.can_update_user(user_role, username, user_role)

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 아이디가 존재하지 않습니다."
        )

    if data.email != user.email:
        user.email = data.email
    if data.username != user.username:
        user.username = data.username
    if data.password:
        user.password = hash_password.hash_password(data.password)

    session.commit()
    return {"message": "사용자 정보가 성공적으로 업데이트되었습니다."}

# 사용자 조회 (username으로 조회)
@user_router.get("/{username}", status_code=status.HTTP_200_OK)
async def get_user(username: str, session=Depends(get_session), user_role: Role = Depends(get_current_user_role)) -> dict:
    Permission.can_view_user(user_role)

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 아이디가 존재하지 않습니다"
        )
    
    return {"email": user.email, "username": user.username}

# 사용자 삭제 (username으로 삭제)
@user_router.delete("/{username}", status_code=status.HTTP_200_OK)
async def delete_user(username: str, session=Depends(get_session), user_role: Role = Depends(get_current_user_role)) -> dict:
    Permission.can_delete_user(user_role)

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 아이디가 존재하지 않습니다."
        )
    
    session.delete(user)
    session.commit()
    
    return {"message": "사용자 정보가 정상적으로 삭제되었습니다."}
