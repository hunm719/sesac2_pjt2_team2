from fastapi import Depends, HTTPException, status
from board.auth.jwt_handler import verify_jwt_token
from fastapi.security import OAuth2PasswordBearer

# 요청이 들어올 때, Authorization 헤더에 토큰을 추출
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/signin")

def authenticate(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_jwt_token(token)
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

# JWT 토큰에서 사용자 정보를 추출하는 함수
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_jwt_token(token)  # JWT 검증 함수
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
        return {
            "user_id": user_id, 
            "role": payload["role"], 
            "username": payload["username"], 
            "email": payload["email"], 
            "nickname": payload["nickname"], 
            "user_img": payload["user_img"]
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")