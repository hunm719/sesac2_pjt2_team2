from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from board.models.admin import Admin
from board.models.events import User
from board.models.users import UserSignUp, UserSignIn
from board.database.connection import get_session
from board.auth.hash_password import HashPassword
from board.auth.jwt_handler import create_jwt_token
from board.auth.authenticate import get_current_user_role
from board.models.permissions import Permission
from typing import List

admin_router = APIRouter()
hash_password = HashPassword()

# 관리자 계정 생성
@admin_router.post("/create-admin", response_model=Admin)
def create_admin(admin: Admin, db: Session = Depends(get_session)):
    db_admin = db.query(Admin).filter(Admin.email == admin.email).first()
    if db_admin:
        raise HTTPException(status_code=400, detail="Admin with this email already exists")
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

# 관리자 로그인
@admin_router.post("/signin", response_model=dict)
async def admin_sign_in(data: UserSignIn, session=Depends(get_session)) -> dict:
    statement = select(Admin).where(Admin.email == data.email)
    admin = session.exec(statement).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 이메일이 없습니다.",
        )

    if hash_password.verify_password(data.password, admin.password) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치하지 않습니다.",
        )

    return {
        "message": "로그인에 성공했습니다.",
        "access_token": create_jwt_token(admin.email, admin.id)
    }

# 사용자 전체 조회 (관리자만 접근)
@admin_router.get("/users", response_model=List[User])
def retrieve_all_users(session=Depends(get_session), user_role: str = Depends(get_current_user_role)) -> List[User]:
    Permission.can_view_users(user_role)  # 관리자가 아닌 사용자는 접근 불가

    statement = select(User)
    users = session.exec(statement)
    return users

# 사용자 조회 (username으로 조회)
@admin_router.get("/users/{username}", response_model=User)
def get_user(username: str, session=Depends(get_session), user_role: str = Depends(get_current_user_role)) -> dict:
    Permission.can_view_user(user_role)  # 관리자가 아닌 사용자는 접근 불가

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 아이디가 존재하지 않습니다."
        )
    
    return {"email": user.email, "username": user.username}

# 사용자 정보 수정 (username으로 조회)
@admin_router.put("/users/{username}", status_code=status.HTTP_200_OK)
async def update_user(username: str, data: UserSignUp, session=Depends(get_session), user_role: str = Depends(get_current_user_role)):
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

# 사용자 삭제 (username으로 삭제)
@admin_router.delete("/users/{username}", status_code=status.HTTP_200_OK)
async def delete_user(username: str, session=Depends(get_session), user_role: str = Depends(get_current_user_role)) -> dict:
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
