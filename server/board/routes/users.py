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

@user_router.get("/me")
async def get_current_user(user_id: int = Depends(authenticate)):
    # 사용자 정보를 가져오는 로직
    return {"user_id": user_id}

# 사용자 등록
@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_new_user(data: UserSignUp, session=Depends(get_session)) -> dict:
    
    # 이메일 중복 검사
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 이메일입니다."
        )
    
    # 아이디 중복 검사
    statement = select(User).where(User.username == data.username)
    user_by_username = session.exec(statement).first()
    if user_by_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 존재하는 아이디입니다."
        )

    # 사용자 생성
    new_user = User(email=data.email, password=hash_password.hash_password(data.password), username=data.username, events=[])
    session.add(new_user)
    session.commit()
    
    return {"message": "정상적으로 등록되었습니다."}
    

# 로그인 처리
@user_router.post("/signin")
async def sign_in(data: UserSignIn, session=Depends(get_session)) -> dict:
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 아이디가 존재하지 않습니다.",
        )

    if hash_password.verify_password(data.password, user.password) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치하지 않습니다.",
        )

    return {
        "message": "로그인에 성공했습니다.", 
        "access_token": create_jwt_token(user.email, user.id)
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
