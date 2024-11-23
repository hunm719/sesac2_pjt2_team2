# your_project/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from board.database import get_db  # get_db 의존성 함수 임포트


# 데이터베이스 URI
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://user:password@localhost/database"  # MySQL 예시

# 엔진 및 세션 설정
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 데이터베이스 세션을 가져오는 의존성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
