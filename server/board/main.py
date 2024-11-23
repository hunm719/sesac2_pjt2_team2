from fastapi import FastAPI
from routes.events import event_router
from contextlib import asynccontextmanager
from database.connection import conn


@asynccontextmanager               # 애플리케이션의 시작과 종료 시점에 코드를 실행
async def lifespan(app: FastAPI):  # 함수 내부에서 FastAPI 애플리케이션의 상태나 설정에 접근하기 위해서 인자로 설정
    # 애플리케이션이 시작될 때 실행할 코드
    conn()
    yield                          # 애플리케이션이 실행되는 동안 이 지점에서 일시 중지
    # 애플리케이션 종료될 때 실행할 코드 (필요 시 추가)


app = FastAPI(lifespan=lifespan)

app.include_router(event_router, prefix="/event")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
