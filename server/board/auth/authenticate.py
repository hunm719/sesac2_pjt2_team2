from fastapi import Depends, HTTPException, status
from board.auth.jwt_handler import verify_jwt_token
from fastapi.security import OAuth2PasswordBearer

# 요청이 들어올 때, Authorization 헤더에 토큰을 추출
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/signin")

def authenticate(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_jwt_token(token)
        print(f"Authenticated payload: {payload}")  # 디버깅
        return payload
    except Exception as e:
        print(f"Authentication error: {e}")  # 디버깅
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

# JWT 토큰에서 사용자 정보를 추출하는 함수
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_jwt_token(token)  # JWT 검증 함수

        return {
            "user_id": payload["user_id"], 
            "role": payload["role"], 
            "email": payload["email"], 
            
        }
    except Exception as e:
        
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    