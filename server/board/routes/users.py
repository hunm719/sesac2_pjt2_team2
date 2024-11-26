from fastapi import APIRouter, HTTPException, status, Depends
from board.models.users import User, UserSignIn, UserSignUp
from board.database.connection import get_session
from sqlmodel import select, delete
from board.auth.hash_password import HashPassword
from board.auth.jwt_handler import create_jwt_token

user_router = APIRouter()
hash_password = HashPassword()

# 사용자 등록
@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_new_user(data: UserSignUp, session=Depends(get_session)) -> dict:
    
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 아이디입니다."
        )

    new_user = User(email=data.email, password=hash_password.hash_password(data.password), username=data.username, events=[])
    session.add(new_user)
    session.commit()
    
    return {"message": "정상적으로 등록되었습니다."}
    

# 로그인 처리
@user_router.post("/signin")
async def sign_in(data: UserSignIn, session=Depends(get_session)) -> dict:
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 아이디가 존재하지 않습니다.",
        )

    if hash_password.verify_password(data.password, user.password) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치하지 않습니다.",
        )

    return {
        "message": "로그인에 성공했습니다.", 
        "access_token": create_jwt_token(user.email, user.id)
    }

@user_router.put("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: int, data: UserSignUp, session=Depends(get_session)):
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 아이디가 존재하지 않습니다."
        )

    if data.email != user.email:
        user.email = data.email
    if data.username != user.username:
        user.username = data.username
    if data.password:
        user.password = hash_password.hash_password(data.password)

    session.commit()
    return {"message": "사용자 정보가 성공적으로 업데이트되었습니다."}

# 사용자 조회 (user_id로 조회)
@user_router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(user_id: int, session=Depends(get_session)) -> dict:
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 아이디가 존재하지 않습니다"
        )
    
    return {"email": user.email, "username": user.username}

# 사용자 삭제 (user_id로 삭제)
@user_router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, session=Depends(get_session)) -> dict:
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 아이디가 존재하지 않습니다."
        )
    
    session.delete(user)
    session.commit()
    
    return {"message": "사용자 정보가 정상적으로 삭제되었습니다."}
