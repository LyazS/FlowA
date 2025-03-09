import uvicorn
from contextlib import asynccontextmanager
import tracemalloc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiofiles import os as aiofiles_os
from app.utils.logging import init_logging
from app.api import api_router
from app.core.config import settings
from app.db.session import init_db, close_db_connection

if settings.DEBUG:
    tracemalloc.start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logging(settings.LOG_FILE_PATH)
    await init_db()
    yield
    # 这里可以放置清理代码
    await close_db_connection()
    pass


app = FastAPI(
    lifespan=lifespan,
    version="1.0.0",
    # docs_url=None,
    # redoc_url=None,
)
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头
)
if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.SERVER_HOST, port=settings.SERVER_PORT)
