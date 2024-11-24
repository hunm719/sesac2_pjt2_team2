from fastapi import FastAPI
from routes.events import event_router
from contextlib import asynccontextmanager
from database.connection import conn
from fastapi.middleware.cors import CORSMiddleware  



@asynccontextmanager
async def lifespan(app: FastAPI):
    conn()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(event_router, prefix="/event", tags=["Event"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
