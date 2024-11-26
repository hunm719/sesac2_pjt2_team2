# board/services/post_service.py
from sqlalchemy.orm import Session
from board.models.events import Post, Comment
from board.schemas.post_schema import PostCreate, CommentCreate
from fastapi import HTTPException

def create_post(db: Session, post: PostCreate):
    try:
        db_post = Post(title=post.title, content=post.content, author=post.author)
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating post: {str(e)}")


def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()

def create_comment(db: Session, comment: CommentCreate, post_id: int):
    db_comment = Comment(content=comment.content, author=comment.author, post_id=post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment
