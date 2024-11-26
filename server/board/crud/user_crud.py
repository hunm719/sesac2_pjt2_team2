from sqlalchemy.orm import Session
from board.models.user_model import User
from board.schemas.user_schema import UserCreate
from board.core.hashing import hash_password

def create_user(db: Session, user: UserCreate):
    hashed_pw = hash_password(user.password)  # 비밀번호 해싱
    db_user = User(
        user_id=user.user_id,
        user_password=hashed_pw,
        name=user.name,
        nickname=user.nickname or user.name,  # nickname 기본값 처리
        email=user.email,
        user_img=user.user_img,  # 프로필 이미지 경로 처리 # or None
        is_admin=False  # 일반 사용자
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
