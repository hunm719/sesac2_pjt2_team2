from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import SQLModel, Field, Column, JSON
from sqlmodel import Relationship

# 게시판용으로 수정
class Event(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    image: str
    description: str
    tags: List[str] = Field(sa_column=Column(JSON))
    location: str    
    comments: list["Comment"] = Relationship(back_populates="event")  # 이벤트와 연결된 댓글들


# 이벤트 수정 시 전달되는 데이터 모델을 정의
class EventUpdate(SQLModel):
    title: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None
# 이벤트 수정시 기존 내용 그대로 불러오는 코드
    def update_event(self, existing_event):
        if self.title is not None:
            existing_event.title = self.title
        if self.image is not None:
            existing_event.image = self.image
        if self.description is not None:
            existing_event.description = self.description
        if self.tags is not None:
            existing_event.tags = self.tags
        if self.location is not None:
            existing_event.location = self.location
        return existing_event

    # Comment 모델 정의
class Comment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    content: str
    user_id: int  # 코멘트를 작성한 사용자의 ID
    event_id: int = Field(foreign_key="event.id")  # 이벤트 ID
    event: "Event" = Relationship(back_populates="comments")



# 양방향 관계 설정
Comment.event = Relationship(back_populates="comments")