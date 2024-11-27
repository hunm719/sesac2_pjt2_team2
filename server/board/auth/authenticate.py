from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from board.auth.jwt_handler import verify_jwt_token


# 요청이 들어올 때, Authorization 헤더에 토큰을 추출
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/signin")

async def authenticate(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="액세스 토큰이 누락되었습니다.")
    
    payload = verify_jwt_token(token)
    return payload["user_id"]

# 현재 사용자 정보와 역할을 가져오는 함수
def get_current_user_role(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )
    try:
        payload = verify_jwt_token(token)
        role = payload.get("role")
        if role is None:
            raise credentials_exception
        return role
    except JWTError:
        raise credentials_exception