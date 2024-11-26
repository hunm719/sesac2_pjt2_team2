from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import validates
from board.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)   # 사용자가 입력하는 아이디
    user_password = Column(String, nullable=False)  # 사용자가 입력하는 비밀번호
    name = Column(String, nullable=False)   # 실제 이름
    nickname = Column(String, nullable=True)    # 가상 이름
    email = Column(String, unique=True, index=True, nullable=False) # 인증 이메일
    user_img = Column(String, nullable=True)    # 프로필 이미지 경로
    is_admin = Column(Boolean, default=False)   # 관리자 여부

    @validates("nickname")
    def default_nickname(self, key, value): # nickname이 없으면 name을 기본값으로 사용
        return value or self.name
