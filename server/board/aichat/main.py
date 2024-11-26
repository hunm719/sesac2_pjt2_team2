from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat

app = FastAPI()


# CORS 미들웨어 설정
origins = [
    "http://localhost:8000",  # 프론트엔드가 실행되는 주소
    "http://127.0.0.1:8000",  # 다른 주소도 추가 가능
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 허용할 출처 리스트
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 라우터 등록
app.include_router(chat.router, prefix="/api", tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Chat API"}
