from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import SQLModel, Field, Column, JSON
from sqlmodel import Relationship
from datetime import datetime, timedelta
import pytz
from sqlalchemy import DateTime, types, func
from sqlalchemy.orm import validates

# TimeZone을 처리하기 위한 커스텀 타입 정의
class KSTDateTime(types.TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            return value
        return value.astimezone(pytz.UTC)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            value = pytz.UTC.localize(value)
        return value.astimezone(pytz.timezone('Asia/Seoul'))


# 게시판용으로 수정된 모델 정의
# 기존 Event 모델을 Board로 변경

class Board(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")  # 게시판의 작성자 ID (VARCHAR(50))
    title: str = Field(..., max_length=50)  # 게시판 제목 (VARCHAR(50))
    description: str = Field(..., max_length=255)  # 게시판 설명 (VARCHAR(255))
    imgUrl: str = Field(..., max_length=255)  # 게시판 이미지 URL (VARCHAR(255))
    likes: int = Field(default=0)  # 좋아요 수 (INT)
    tag: List[str] = Field(sa_column=Column(JSON))  # 태그 (JSON 배열)
    comments: list["Comment"] = Relationship(back_populates="board")  # 댓글들
    user: Optional["User"] = Relationship(back_populates="boards")

    # 생성 시 UTC 시간으로 저장 (분 단위까지)
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow().replace(tzinfo=pytz.UTC).replace(second=0, microsecond=0))
    
    # 수정 시 자동으로 현재 시간 업데이트 (분 단위까지)
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow().replace(tzinfo=pytz.UTC).replace(second=0, microsecond=0), sa_column=Column(DateTime, onupdate=func.current_timestamp()))

    @validates('created_at', 'updated_at')
    def validate_datetime(self, key, value):
        # 문자열을 datetime 객체로 변환
        if isinstance(value, str):  # 문자열 처리
            try:
                # ISO 8601 포맷에 맞춰 datetime 객체로 변환
                value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
            except ValueError:
                raise ValueError(f"Invalid datetime string format: {value}")
        elif isinstance(value, datetime):  # 이미 datetime 객체인 경우
            if value.tzinfo is None:
                value = value.replace(tzinfo=pytz.UTC)
        return value

    # __init__에서 날짜 필드 강제로 변환
    def __init__(self, **kwargs):
        # 강제로 날짜 필드 변환 (created_at, updated_at이 문자열로 전달될 경우)
        for field in ['created_at', 'updated_at']:
            if field in kwargs and isinstance(kwargs[field], str):
                kwargs[field] = self.validate_datetime(field, kwargs[field])
        super().__init__(**kwargs)

    # 시간 출력 시 분 단위까지만 표시하도록 설정
    def formatted_created_at(self):
        return self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None

    def formatted_updated_at(self):
        return self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else None

# 기존 EventUpdate 모델을 수정하여 Board에 맞는 수정 모델 정의
class BoardUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    imgUrl: Optional[str] = None
    likes: Optional[int] = None
    tag: Optional[List[str]] = None

    def update_board(self, existing_board):
        if self.title is not None:
            existing_board.title = self.title
        if self.description is not None:
            existing_board.description = self.description
        if self.imgUrl is not None:
            existing_board.imgUrl = self.imgUrl
        if self.likes is not None:
            existing_board.likes = self.likes
        if self.tag is not None:
            existing_board.tag = self.tag
        return existing_board


# Comment 모델을 Board에 맞게 수정
class Comment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int  # 코멘트를 작성한 사용자의 ID
    content: str  # 댓글 내용 (VARCHAR(50))
    board_id: int = Field(foreign_key="board.id")  # 게시글 ID (Foreign Key)
    board: "Board" = Relationship(back_populates="comments")
    created_at: datetime = Field(sa_column=Column(KSTDateTime, default=datetime.utcnow))  # UTC 시간으로 저장

    @property
    def created_at_kst(self) -> datetime:
        """UTC로 저장된 created_at에 9시간을 더해 KST로 변환"""
        return self.created_at + timedelta(hours=9)

    @classmethod
    def from_orm(cls, obj):
        """ORM 객체에서 문자열을 처리하여 datetime 객체로 변환"""
        if isinstance(obj.created_at, str):
            # 문자열을 datetime 객체로 변환하고 UTC로 설정
            obj.created_at = datetime.strptime(obj.created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
            obj.created_at = pytz.UTC.localize(obj.created_at)
        return super().from_orm(obj)

# 유저 모델 (User 클래스)
class User(SQLModel, table=True):

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(..., max_length=20)
    user_password: str = Field(...)
    name: str = Field(..., max_length=50)
    nickname: str = Field(..., max_length=20)
    email: str = Field(..., unique=True)
    user_img: str = Field(...) # 이미지 등록 안 하면 기본 이미지로 설정되도록 수정하면 좋을듯

    boards: List[Board] = Relationship(back_populates="user")  # Board와 양방향 관계 설정

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# 양방향 관계 설정
Comment.board = Relationship(back_populates="comments")