from time import time
from fastapi import HTTPException, status
from jose import jwt, JWTError
from board.database.connection import Settings
from board.models.roles import Role
from typing import Dict, Any

settings = Settings()

# JWT 토큰 생성
def create_jwt_token(email: str, user_id: int, role: str) -> str:
    payload = {
        "user_id": user_id, 
        "email": email,
        "role": role,
        "iat": time(), 
        "exp": time() + 3600
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token



# JWT 토큰 검증
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp = payload.get("exp")
        if exp is None: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
        if time() > exp:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token expired")
        # # 역할 검증 및 변환
        # try:
        #     payload["role"] = Role(payload["role"])  # Role Enum으로 변환
        # except ValueError:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST, 
        #         detail="유효하지 않은 역할입니다."
        #     )
        return payload
    
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    