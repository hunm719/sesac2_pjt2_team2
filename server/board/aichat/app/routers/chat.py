from openai import OpenAI
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
import os

# .env 파일 로드
load_dotenv()  # 환경 변수 설정
api_key = os.getenv("OPENAI_API_KEY")  # .env에서 API 키 읽기

# API 키 유효성 확인
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set. Check your .env file.")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# FastAPI 라우터 생성
router = APIRouter()

# 요청 모델 정의
class ChatRequest(BaseModel):
    message: str  # 사용자 메시지
    role: str = "default"  # 역할 (기본값: "default")

# POST 요청 처리
@router.post("/chat")
async def chat(request: ChatRequest):
    """
    사용자 메시지를 받아 OpenAI API를 호출해 응답 반환.
    :param request: 사용자 요청 (message와 role 포함)
    """
    try:
        # 역할에 따른 프롬프트 가져오기
        prompt = get_role_based_prompt(request.role)
        # OpenAI API 호출
        response = client.chat.completions.create(  # 수정된 메서드
            model="gpt-3.5-turbo",  # 최신 모델 지정
            messages=[
                {"role": "system", "content": prompt},  # 시스템 역할로 기본 프롬프트 전달
                {"role": "user", "content": request.message},  # 사용자 메시지 전달
            ],
            max_tokens=100,  # 응답의 최대 토큰 수
            temperature=0.7  # 다양성을 조절하는 옵션
        )
        # OpenAI 응답에서 텍스트 추출
        ai_message = response.choices[0].message.content.strip()
        return {"reply": ai_message}
    except Exception as e:
        # 예외 발생 시 HTTP 500 에러 반환
        raise HTTPException(status_code=500, detail=f"Error: {e}")

# 기본 프롬프트 함수
def get_default_prompt():
    """
    기본 역할 프롬프트 반환.
    """
    return (
        "You are a friendly and knowledgeable assistant. "
        "Please provide helpful and concise answers to the user's questions."
    )

# 역할 기반 프롬프트 함수
def get_role_based_prompt(role: str):
    """
    역할에 따라 프롬프트 반환.
    :param role: 사용자 역할 (예: friendly, professional)
    """
    prompts = {
        "friendly": "You are a cheerful and friendly assistant.",
        "professional": "You are a professional technical expert.",
        "casual": "You are a witty and casual assistant."
    }
    # 역할에 맞는 프롬프트 반환, 기본값은 get_default_prompt()
    return prompts.get(role, get_default_prompt())
