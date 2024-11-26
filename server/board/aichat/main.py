from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.chat import router as chat_router  # chat 라우터 임포트

# FastAPI 앱 초기화
app = FastAPI()

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (필요에 따라 제한 가능)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 라우터 등록 (Chat API 엔드포인트)
app.include_router(chat_router, prefix="/api", tags=["Chat"])

# 기본 엔드포인트
@app.get("/")
async def root():
    """
    API 기본 엔드포인트.
    """
    return {"message": "Welcome to the AI Chat API"}
