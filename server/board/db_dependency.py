from sqlalchemy.orm import sessionmaker
from board.database import SessionLocal  # SessionLocal을 임포트합니다.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
