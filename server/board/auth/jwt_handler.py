from time import time
from fastapi import HTTPException, status
import jwt
from board.database.connection import Settings

settings = Settings()

# JWT 토큰 생성
def create_jwt_token(email: str, user_id: str, role: str) -> str:
    payload = {
        "user_id": user_id, 
        "email": email,
        "role": role,
        "iat": time(),
        "exp": time() + 3600
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token



def verify_jwt_token(token: str):
    try:
        # JWT 디코딩
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], options={"require": ["exp"]})
        print('payload::::::::::::::::::::::::::::', payload)

        # 만료 시간 검증
        exp = payload.get("exp")
        print('exp::::::::::::::::::::::::::::', exp)
        if exp is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="exp가 없어서 유효하지 않은 토큰입니다.")

        if time() > exp:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="토큰이 만료되었습니다.")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="토큰이 만료되었습니다.")
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="유효하지 않은 토큰입니다.")
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="유효하지 않은 토큰입니다.")
    