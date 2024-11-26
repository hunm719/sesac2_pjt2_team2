from openai import OpenAI
from fastapi import APIRouter, HTTPException
from app.utils.prompts import get_default_prompt, get_role_based_prompt
import os
from dotenv import dotenv_values
from pydantic import BaseModel


# # 환경 변수 로드
# dotenv_path = os.path.join(os.path.dirname(__file__), '../env/.env')
# load_dotenv(dotenv_path)  # .env 파일을 로드합니다.

api_key = ""  # .env에서 API 키 로드

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set. Check your .env file.")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# OpenAI 요청
try:
    result = client.completions.create(
        model="gpt-3.5-turbo-instruct",  # 사용할 모델 지정
        prompt="Say this is a test",    # 프롬프트 내용
        max_tokens=7,                   # 최대 토큰 수
        temperature=0                   # 응답의 다양성 조정
    )

    print(result)
    print(result.choices[0].text)  # 응답 출력
except Exception as e:
    print(f"Error: {e}")



router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    role: str = "default"  # 기본값 지정

@router.post("/chat")
async def chat(request: ChatRequest):
    """사용자 메시지를 받아 AI 응답을 반환합니다."""
    try:
        prompt = get_role_based_prompt(request.role)
        response = client.completions.create(  # 변경된 메서드
            model="gpt-3.5-turbo",  # 사용할 모델
            prompt=prompt + "\n" + request.message,  # 역할에 맞는 프롬프트와 사용자 메시지를 합침
            max_tokens=100  # 응답의 최대 토큰 수
        )
        ai_message = response["choices"][0]["text"].strip()  # 응답에서 AI 메시지 추출
        return {"reply": ai_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 프롬프트 함수
def get_default_prompt():
    """기본 AI 프롬프트를 반환합니다."""
    return (
        "You are a friendly and knowledgeable assistant. "
        "Please provide helpful and concise answers to the user's questions."
    )

def get_role_based_prompt(role: str):
    """특정 역할에 따라 다른 프롬프트를 반환합니다."""
    prompts = {
        "friendly": "You are a cheerful and friendly assistant.",
        "professional": "You are a professional technical expert.",
        "casual": "You are a witty and casual assistant."
    }
    return prompts.get(role, get_default_prompt())
