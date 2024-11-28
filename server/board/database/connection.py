from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv
import os

class Settings:
    # 시크릿 키가 들어갈 공간을 넣습니다. .env에서 끌어오게 만들겠습니다. 시크릿키는 env에 넣으면됩니다.
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    # 데이터베이스 파일과 연결 문자열을 포함한 설정
    database_file = "database.db"
    database_connection_string = f"sqlite:///{database_file}"
    connect_args = {"check_same_thread": False}
    engine_url = create_engine(
        database_connection_string, echo=True, connect_args=connect_args
    )

def conn():
    # SQLModel을 상속받은 모든 클래스를 기반으로 데이터베이스에 테이블을 생성
    SQLModel.metadata.create_all(Settings.engine_url)

def get_session():
    # Session => 데이터베이스와 상호작용(CRUD)을 관리하는 객체
    with Session(Settings.engine_url) as session:
        yield session
