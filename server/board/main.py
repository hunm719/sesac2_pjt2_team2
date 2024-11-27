from fastapi import FastAPI
from board.routes.events import board_router
from board.routes.users import user_router
from contextlib import asynccontextmanager
from board.database.connection import conn
from fastapi.middleware.cors import CORSMiddleware  

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(board_router, prefix="/event", tags=["Event"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["*"],
)

# User 관련 라우터 추가
app.include_router(user_router, prefix="/user", tags=["User"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
