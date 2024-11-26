from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from board.schemas.user_schema import UserCreate, UserResponse
from board.crud.user_crud import create_user
from board.database import get_db

router = APIRouter()

# 회원가입 API
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db, user)
    if not db_user:
        raise HTTPException(status_code=400, detail="사용자 등록에 실패했습니다")
    return db_user
