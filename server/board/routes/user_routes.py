from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from board.schemas.user_schema import UserCreate, UserResponse
from board.crud.user_crud import create_user
from board.crud.user_crud import get_user_by_user_id
from board.core.hashing import verify_password
from board.core.jwt import create_access_token
from board.schemas.user_schema import UserLogin
from board.database import get_db

router = APIRouter()

# 회원가입 API
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db, user)
    if not db_user:
        raise HTTPException(status_code=400, detail="사용자 등록에 실패했습니다")
    return db_user

# 로그인 API
@router.post("/login")
def login(user_login: UserLogin, db: Session = Depends(get_db)):

    # 1. 입력된 user_id로 사용자 조회
    user = get_user_by_user_id(db, user_login.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # 2. 비밀번호 검증
    if not verify_password(user_login.password, user.user_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # 3. JWT 토큰 생성
    access_token = create_access_token(data={"sub": user.user_id})
    
    return {"access_token": access_token, "token_type": "bearer"}