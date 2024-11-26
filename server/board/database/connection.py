from sqlmodel import create_engine, SQLModel, Session
# from board.models.roles import Role
# from board.models.permissions import Permission

database_file = "database.db"
database_connection_string = f"sqlite:///{database_file}"
connect_args = {"check_same_thread": False}
engine_url = create_engine(
    database_connection_string, echo=True, connect_args=connect_args
)


def conn():
    # SQLModel을 상속받은 모든 클래스를 기반으로 데이터베이스에 테이블을 생성
    SQLModel.metadata.create_all(engine_url)


def get_session():
    # Session => 데이터베이스와 상호작용(CRUD)을 관리하는 객체
    with Session(engine_url) as session:
        yield session

class Settings:
    SECRET_KEY = "your_secret_key_here"
