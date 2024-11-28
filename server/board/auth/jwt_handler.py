from time import time
from fastapi import HTTPException, status
from jose import jwt, JWTError
from board.database.connection import Settings
from board.models.roles import Role

settings = Settings()

from typing import Union

# JWT 토큰 생성
def create_jwt_token(email: str, user_id: int, role: str = "user") -> str:
    payload = {
        "user": email,
        "user_id": user_id,
        "role": role,
        "iat": time(),  # 발급 시간
        "exp": time() + 1800,  # 만료 시간 (30분)
    }
    
    # SECRET_KEY 타입 확인
    secret_key: Union[str, bytes] = settings.SECRET_KEY
    if not isinstance(secret_key, (str, bytes)):
        raise ValueError(f"SECRET_KEY는 문자열 또는 바이트여야 합니다. 현재 타입: {type(secret_key)}")
    
    # 토큰 생성
    try:
        token = jwt.encode(payload, secret_key, algorithm="HS256")
    except Exception as e:
        raise RuntimeError(f"JWT 생성 중 오류 발생: {e}")
    
    return token



# JWT 토큰 검증
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp = payload.get("exp")
        role = payload.get("role")

        if exp is None: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="유효하지 않은 토큰입니다.")
        
        if time() > exp:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="토큰이 만료되었습니다.")
        
        if role is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="역할을 찾을 수 없습니다.")
        
        try:
            role = Role(role)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="유효하지 않은 토큰입니다.")

        return payload
    
    except JWTError as jwt_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"JWT 오류: {str(jwt_error)}")
    except KeyError as key_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"필수 클레임이 누락되었습니다: {str(key_error)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"알 수 없는 오류: {str(e)}")

