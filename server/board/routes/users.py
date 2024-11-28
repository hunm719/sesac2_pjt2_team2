from fastapi import APIRouter, HTTPException, status, Depends
from board.models.events import User
from fastapi.security import OAuth2PasswordBearer
from board.models.users import UserSignIn, UserSignUp
from board.database.connection import get_session
from sqlmodel import select
from board.auth.jwt_handler import create_jwt_token
from board.auth.hash_password import HashPassword
from board.auth.authenticate import authenticate, get_current_user
# from board.models.permissions import Permission
from typing import List


user_router = APIRouter()
hash_password = HashPassword()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/signin")

# 이메일 중복 검사 함수
def check_duplicate_email(session, email):
    statement = select(User).where(User.email == email)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 이메일입니다."
        )

# 아이디 중복 검사 함수
def check_duplicate_user_id(session, user_id):
    statement = select(User).where(User.user_id == user_id)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 아이디입니다."
        )

# 사용자 등록
@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_new_user(data: UserSignUp, session=Depends(get_session)) -> dict:
    check_duplicate_email(session, data.email)
    check_duplicate_user_id(session, data.username)

    # 사용자 생성
    new_user = User(
        user_id=data.user_id,
        user_password=hash_password.hash_password(data.user_password),
        username=data.username,
        nickname=data.nickname,
        email=data.email,
        user_img=data.user_img,
        role="user"
    )

    # 데이터베이스에 사용자 추가
    session.add(new_user)
    session.commit()

    return {"message": "사용자가 정상적으로 등록되었습니다."}

# 로그인 처리
@user_router.post("/signin")
def sign_in(data: UserSignIn, session=Depends(get_session)) -> dict:
    statement = select(User).where(User.user_id == data.user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 사용자가 존재하지 않습니다."
        )

    if hash_password.verify_password(data.user_password, user.user_password) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치하지 않습니다."
        )

    return {
        "message": "로그인에 성공했습니다.", 
        "access_token": create_jwt_token(user.email, user.id, user.role)
    }

# 내 정보 조회
@user_router.get("/me", status_code=status.HTTP_200_OK)
async def get_my_userInfo(current_user=Depends(get_current_user)) -> dict:
    return {
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "nickname": current_user["nickname"],
        "email": current_user["email"],
        "user_img": current_user["user_img"],
        "role": current_user["role"]
    }

# 사용자 모두 조회
@user_router.get("/users", status_code=status.HTTP_200_OK)
async def get_userInfo(session=Depends(get_session)) -> List[dict]:
    statement = select(User)
    users = session.exec(statement).all()
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자가 존재하지 않습니다."
        )

    # 모든 사용자 정보를 반환
    return [
        {
            "id": user.id,
            "user_id": user.user_id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "user_img": user.user_img,
            "role": user.role
        }
        for user in users
    ]

# 사용자 정보 수정
@user_router.put("/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(
    user_id: str, 
    data: UserSignUp, 
    session=Depends(get_session)
) -> dict:
    statement = select(User).where(User.user_id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    # 업데이트
    user.user_id = data.user_id or user.user_id
    user.username = data.username or user.username
    user.nickname = data.nickname or user.nickname
    user.email = data.email or user.email
    user.user_img = data.user_img or user.user_img
    session.add(user)
    session.commit()

    return {"message": "사용자 정보가 성공적으로 수정되었습니다."}


# 사용자 삭제
@user_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, session=Depends(get_session)):
    statement = select(User).where(User.user_id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    session.delete(user)
    session.commit()

    return {"message": "사용자가 성공적으로 삭제되었습니다."}



# # 사용자 정보 수정 (user_id로 조회)
# @user_router.put("/users/{user_id}")
# async def update_user(user_id: int, data: UserSignIn, current_user: dict = Depends(get_current_user), session=Depends(get_session)):
#     # if current_user["user_id"] != user_id:
#     #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="내 사용자 정보만 수정할 수 있습니다.")
    
#     # 사용자 정보 업데이트 로직
#     statement = select(User).where(User.user_id == user_id)
#     user = session.exec(statement).first()
    
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")
    
#     # 비밀번호 등 정보 업데이트
#     user.email = data.email or user.email
#     user.username = data.username or user.username
#     if data.user_password:
#         user.user_password = hash_password.hash_password(data.user_password)
    
#     session.commit()
    
#     return {"message": "사용자 정보가 성공적으로 업데이트되었습니다."}

# # 현재 사용자 정보를 가져오기
# @user_router.get("/me")
# async def get_current_user(current_user=Depends(authenticate), token: str = Depends(oauth2_scheme)):
#     return {
#         "user_id": current_user["user_id"],
#         "username": current_user["username"],
#         "nickname": current_user["nickname"],
#         "email": current_user["email"],
#         "user_img": current_user["user_img"]
#     }

# # 사용자 조회 (user_id로 조회)
# @user_router.get("/{user_id}", status_code=status.HTTP_200_OK)
# async def get_user(
#     user_id: int,
#     session=Depends(get_session)
#     # current_user=Depends(authenticate)
# ) -> dict:
#     statement = select(User).where(User.user_id == user_id)
#     user = session.exec(statement).first()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="해당 아이디가 존재하지 않습니다."
#         )

#     # # 현재 사용자와 다른 사용자 구분
#     # if user_id == current_user["user_id"]:
#     #     return {
#     #         "user_id": user.user_id,
#     #         "username": user.username,
#     #         "nickname": user.nickname,
#     #         "email": user.email,
#     #         "user_img": user.user_img
#     #     }
#     # else:
#     return {
#             "user_id": user.user_id,
#             "nickname": user.nickname,
#             "email": user.email,
#             "user_img": user.user_img
#     }

# # 사용자 삭제 (user_id로 삭제)
# @user_router.delete("/{user_id}", status_code=status.HTTP_200_OK)
# async def delete_user(
#     user_id: int,
#     session=Depends(get_session)
#     # current_user=Depends(authenticate)
# ) -> dict:
#     statement = select(User).where(User.user_id == user_id)
#     user = session.exec(statement).first()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="해당 아이디가 존재하지 않습니다."
#         )

#     # 권한 확인
#     # Permission.can_delete_user(current_user["role"])

#     session.delete(user)
#     session.commit()

#     return {"message": "사용자 정보가 정상적으로 삭제되었습니다."}
