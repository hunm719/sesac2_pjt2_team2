# import httpx
# import os
# from fastapi import HTTPException
# from dotenv import load_dotenv

# # .env 파일에서 환경 변수 로드
# load_dotenv()

# KAKAO_API_URL = "https://kauth.kakao.com/oauth/token"
# KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"  # 사용자 정보 요청 URL

# KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
# KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")

# async def get_access_token(code: str) -> dict:
#     """카카오 로그인 후 전달받은 code로 액세스 토큰을 요청하는 비동기 함수"""
#     data = {
#         "grant_type": "authorization_code",
#         "client_id": KAKAO_CLIENT_ID,
#         "redirect_uri": KAKAO_REDIRECT_URI,
#         "code": code,
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.post(KAKAO_API_URL, data=data)
#         if response.status_code != 200:
#             raise HTTPException(status_code=400, detail="카카오 로그인 실패")
#         return response.json()  # 반환된 JSON 데이터 (액세스 토큰 포함)


# async def get_kakao_user_info(access_token: str) -> dict:
#     """액세스 토큰을 이용해 카카오 사용자 정보를 요청하는 비동기 함수"""
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.get(KAKAO_USER_INFO_URL, headers=headers)
#         if response.status_code != 200:
#             raise HTTPException(status_code=400, detail="사용자 정보 요청 실패")
#         return response.json()  # 반환된 사용자 정보 (예: id, email 등)
