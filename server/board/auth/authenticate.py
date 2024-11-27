from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from board.auth.jwt_handler import verify_jwt_token, create_jwt_token
from board.auth.session_store import session_store

# OAuth2PasswordBearer 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/signin")

# 세션 저장소 (메모리 기반)
session_store = {}

# 세션에 JWT 저장
def set_jwt_in_session(session_id: str, user_email: str, user_id: int):
    jwt_token = create_jwt_token(user_email, user_id)
    session_store[session_id] = jwt_token
    return jwt_token

# 세션에서 JWT 가져오기
def get_jwt_from_session(session_id: str):
    jwt_token = session_store.get(session_id)
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Invalid session")
    return jwt_token

# JWT 인증 함수
async def authenticate(request: Request, token: str = Depends(oauth2_scheme)):
    session_id = request.cookies.get("session_id")
    if session_id:
        jwt_token = get_jwt_from_session(session_id)
        payload = verify_jwt_token(jwt_token)  # 세션에서 JWT 검증
        return payload["user_id"]
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="세션이 없습니다.")

# 현재 사용자 정보와 역할을 가져오는 함수
def get_current_user_role(request: Request, token: str = Depends(oauth2_scheme)) -> str:
    session_id = request.cookies.get("session_id")
    credentials_exception = HTTPException(
        status_code=401,
        detail="JWT에 역할 정보가 없습니다.",
    )

    if session_id:
        jwt_token = get_jwt_from_session(session_id)
        payload = verify_jwt_token(jwt_token)
        role = payload.get("role")
        if role is None:
            raise credentials_exception
        return role
    else:
        raise credentials_exception
