# board/routes/post_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from board.services.post_service import create_post, get_post, create_comment
from board.schemas.post_schema import PostCreate, PostOut, CommentCreate
from sqlalchemy import get_db

router = APIRouter()

# 게시글 작성 API
@router.post("/", response_model=PostOut)
def create_post_route(post: PostCreate, db: Session = Depends(get_db)):
    return create_post(db=db, post=post)

# 게시글 조회 API
@router.get("/{post_id}", response_model=PostOut)
def read_post(post_id: int, db: Session = Depends(get_db)):
    db_post = get_post(db=db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

# 댓글 작성 API
@router.post("/{post_id}/comments", response_model=CommentCreate)
def create_comment_route(post_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    return create_comment(db=db, comment=comment, post_id=post_id)
