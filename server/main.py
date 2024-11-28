from fastapi import FastAPI #, RedirectResponse, Request, HTTPException
from board.routes.events import board_router
from board.routes.users import user_router
from board.routes.admin import admin_router
from contextlib import asynccontextmanager
from board.database.connection import conn
from fastapi.middleware.cors import CORSMiddleware 
from dotenv import load_dotenv 
import os
# from kakao_auth import get_access_token, get_kakao_user_info

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

# KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
# KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")

# @app.get("/login")
# async def login():
#     kakao_login_url = f"https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={KAKAO_CLIENT_ID}&redirect_uri={KAKAO_REDIRECT_URI}"
#     return RedirectResponse(kakao_login_url)

# @app.get("/login/callback")
# async def callback(code: str):
#     try:
#         token_info = await get_access_token(code)  
#         access_token = token_info["access_token"]

#         user_info = await get_kakao_user_info(access_token)

#         return {"user_info": user_info}
#     except HTTPException as e:
#         raise e

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
