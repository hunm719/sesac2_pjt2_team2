from time import time
from fastapi import HTTPException, status
from jose import jwt
from board.database.connection import Settings
from board.models.roles import Role
#Role 임포트 했습니다.

settings = Settings()

# JWT 토큰 생성
def create_jwt_token(email: str, user_id: int) -> str:
    payload = {"user": email, "user_id": user_id, "role": role, "iat": time(), "exp": time() + 3600}
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
        
        role = payload.get("role")
        if role is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found in token")
        
        # 아래는 추가된 내용입니다.
        try:
            role = Role(role)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role in token")
        # 문자열을 Role Enum으로 변환합니다.



        
        return payload
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
