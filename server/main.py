# main.py
from fastapi import FastAPI
from board.routes import post_routes
from board.database import engine, Base

# 데이터베이스 초기화
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 게시글 관련 라우터 추가
app.include_router(post_routes.router, prefix="/posts", tags=["posts"])

# User 관련 라우터 추가
app.include_router(user.router, prefix="/api/users", tags=["Users"])

# 응답 예시
@app.get("/")
def read_root():
    return {"message": "fastapi가 잘 작동됩니다"}