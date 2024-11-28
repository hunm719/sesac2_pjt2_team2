from fastapi import FastAPI #, RedirectResponse, Request, HTTPException
from board.routes.events import board_router
from board.routes.users import user_router
from board.routes.admin import admin_router
from contextlib import asynccontextmanager
from board.database.connection import conn
from fastapi.middleware.cors import CORSMiddleware 
from dotenv import load_dotenv 
import os

from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn()
    yield

app = FastAPI(lifespan=lifespan)

 # .env 파일을 로드하고 secrey_key 가져오기
load_dotenv()
secret_key = os.getenv("SECRET_KEY")
if secret_key is None:
    raise ValueError("SECRET_KEY가 설정되지 않았습니다.")
else:
    print(f"SECRET_KEY: {secret_key}")  # 값 확인

app.include_router(board_router, prefix="/event", tags=["Event"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

#이미지 url 문제 해결용
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
