from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select
from board.models.admin import AdminSignUp, AdminSignIn
from board.models.events import Admin
from board.models.users import UserSignIn
# from board.models.roles import Role
from board.database.connection import get_session
from board.auth.hash_password import HashPassword
from board.auth.jwt_handler import create_jwt_token
# from board.models.permissions import Permission
from typing import List

admin_router = APIRouter()
hash_password = HashPassword()

# 아이디 중복 검사 함수
def check_duplicate_admin_id(session, admin_id):
    statement = select(Admin).where(Admin.admin_id == admin_id)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 아이디입니다."
        )

# 관리자 계정 생성
@admin_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_new_admin(data: AdminSignUp, session=Depends(get_session)) -> dict:
    check_duplicate_admin_id(session, data.admin_id)

    # 관리자 생성
    new_admin = Admin(
        admin_id=data.admin_id,
        admin_password=hash_password.hash_password(data.admin_password),
        email=data.email,
        role="admin"
    )

    # 데이터베이스에 관리자 추가
    try:
        session.add(new_admin)
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 오류 발생")

    return {"message": "관리자가 정상적으로 등록되었습니다."}
    

# 관리자 로그인
@admin_router.post("/signin")
def admin_sign_in(data: AdminSignIn, session=Depends(get_session)) -> dict:
    statement = select(Admin).where(Admin.admin_id == data.admin_id)
    admin = session.exec(statement).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="아이디가 일치하지 않습니다.",
        )

    if hash_password.verify_password(data.admin_password, admin.admin_password) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치하지 않습니다.",
        )

    return {
        "message": "로그인에 성공했습니다.",
        "access_token": create_jwt_token(admin.email, admin.id, admin.role)
    }
