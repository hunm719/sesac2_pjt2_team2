from time import time
from fastapi import HTTPException, status
from jose import jwt, JWTError
from board.database.connection import Settings
from board.models.roles import Role

settings = Settings()

# JWT 토큰 생성
def create_jwt_token(email: str, user_id: int, role: str = "user") -> str:

    payload = {"user": email, "user_id": user_id, "role": role, "iat": time(), "exp": time() + 1800}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

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

