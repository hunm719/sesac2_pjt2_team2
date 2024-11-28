from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import SQLModel, Field, Column, JSON
from sqlmodel import Relationship
from datetime import datetime, timedelta, timezone
import pytz
from sqlalchemy import DateTime, types, func, String
from sqlalchemy.orm import validates

from zoneinfo import ZoneInfo


# 게시판용으로 수정된 모델 정의
# 기존 Event 모델을 Board로 변경

class Board(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    # user_id: str = Field(..., max_length=50)  # 게시판의 작성자 ID (VARCHAR(50)) 기존 
    # user_id: int = Field(foreign_key="user.id")
    user_id: str = Field(foreign_key="user.user_id")  # user_id를 str로 변경

    title: str = Field(..., max_length=50)  # 게시판 제목 (VARCHAR(50))
    description: str = Field(..., max_length=255)  # 게시판 설명 (VARCHAR(255))
    imgUrl: str = Field(..., max_length=255)  # 게시판 이미지 URL (VARCHAR(255))
    likes: Optional[int] = Field(default=0)  # 좋아요 수 (INT)
    tag: List[str] = Field(sa_column=Column(JSON))  # 태그 (JSON 배열)
    comments: list["Comment"] = Relationship(back_populates="board")  # 댓글들
    user: Optional["User"] = Relationship(back_populates="boards")
 
    @property
    def like_count(self):
        return self.likes_count or 0  # 값이 없으면 0을 반환

#아래는 강사님이 주신 코드 #######################################################
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Seoul")))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Seoul")), sa_column=Column(DateTime, onupdate=datetime.now))
    

# 기존 EventUpdate 모델을 수정하여 Board에 맞는 수정 모델 정의
class BoardUpdate(SQLModel):
    user_id: str = Field(foreign_key="user.id")
    title: Optional[str] = None
    description: Optional[str] = None
    imgUrl: Optional[str] = None
    # likes: Optional[int] = None
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Seoul")))  # UTC 시간으로 저장

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

# 유저 계정
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(..., max_length=20)
    user_password: str = Field(...)
    username: str = Field(..., max_length=50) # name에서 username으로 변경
    nickname: str = Field(..., max_length=20)
    email: str = Field(..., unique=True)
    user_img: str = Field(...) # 이미지 등록 안 하면 기본 이미지로 설정되도록 수정하면 좋을듯
    #user_img: Optional[str] = Field(default="default_image.png")  # 기본 이미지 설정
    #나중에 user_img를 위에걸로 교체
    #role 추가
    role: str = Field(..., sa_column=Column("role", String))  # role을 문자열로 저장


    boards: List[Board] = Relationship(back_populates="user")  # Board와 양방향 관계 설정

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# 관리자 계정
class Admin(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    admin_id: str = Field(..., max_length=20)
    admin_password: str = Field(...)
    role: str = Field(..., sa_column=Column("role", String))

# 양방향 관계 설정
Comment.board = Relationship(back_populates="comments")



class Like(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id")  # 게시글의 ID (게시글 테이블의 외래키)
    user_id: int = Field(foreign_key="user.id")  # 사용자의 ID (사용자 테이블의 외래키)