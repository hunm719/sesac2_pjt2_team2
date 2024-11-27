# board/schemas/post_schema.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class PostBase(BaseModel):
    title: str
    content: str
    author: str

class PostCreate(PostBase):
    pass

class PostOut(PostBase):
    id: int
    created_at: datetime
    views: int

    class Config:
        # orm_mode = True   <- Pydantic 이라는 라이브러리가 버전 2 부터는 orm_mode가 from_attributes로 변경되었음
        from_attributes = True

class CommentBase(BaseModel):
    content: str
    author: str

class CommentCreate(CommentBase):
    pass

class CommentOut(CommentBase):
    id: int
    created_at: datetime

    class Config:
        # orm_mode = True
        from_attributes = True
