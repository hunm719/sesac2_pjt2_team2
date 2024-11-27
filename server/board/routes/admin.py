# from fastapi import APIRouter, Depends, HTTPException, status
# from board.models.users import User
# from board.auth.hash_password import HashPassword
# from board.database.connection import get_session
# from board.models.roles import Role
# from sqlmodel import select

# admin_router = APIRouter()

# hash_password = HashPassword()

# # 관리자 계정 생성
# @admin_router.post("/create-admin", status_code=status.HTTP_201_CREATED)
# async def create_admin(user_data: dict, session=Depends(get_session)):
#     # 이메일 중복 검사
#     existing_user_by_email = session.exec(select(User).where(User.email == user_data['email'])).first()
#     if existing_user_by_email:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 이메일입니다.")

#     # 아이디 중복 검사
#     existing_user_by_username = session.exec(select(User).where(User.username == user_data['username'])).first()
#     if existing_user_by_username:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 아이디입니다.")

#     # Role 객체 가져오기 (기본적으로 admin 역할 부여)
#     role = session.exec(select(Role).where(Role.name == "admin")).first()
#     if not role:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="관리자 롤을 찾을 수 없습니다.")

#     # 관리자 계정 생성
#     new_admin = User(
#         email=user_data['email'],
#         password=hash_password.hash_password(user_data['password']),
#         username=user_data['username'],
#         role=role  # Role 객체 할당
#     )
#     session.add(new_admin)
#     session.commit()

#     return {"message": "관리자 계정이 생성되었습니다."}

# # 역할 부여 API
# @admin_router.post("/assign-role")
# async def assign_role(user_id: int, role_name: str, session=Depends(get_session)):
#     # 사용자 찾기
#     user = session.exec(select(User).where(User.id == user_id)).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")
    
#     # 역할 찾기
#     role = session.exec(select(Role).where(Role.name == role_name)).first()
#     if not role:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role을 찾을 수 없습니다.")

#     # 사용자에게 역할 부여
#     user.role = role  # Role 객체 할당
#     session.commit()

#     return {"message": f"{role_name} 권한이 사용자에게 부여되었습니다."}
