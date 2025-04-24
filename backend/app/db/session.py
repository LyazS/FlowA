from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
from app.core.config import settings
from app.utils.logging import logger
from app.db.base import Base

# 创建异步数据库引擎
async_engine = create_async_engine(
    settings.DATABASE_URL,
    # pool_size=settings.DATABASE_POOL_SIZE,
    # max_overflow=0,
    # pool_recycle=3600,  # 每小时回收连接
    # pool_pre_ping=True,  # 预先ping连接
)

# 创建异步session工厂
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


async def get_db():
    async with AsyncSessionFactory() as session:
        try:
            yield session
            # logger.debug("Database session created")
        finally:
            await session.close()
            # logger.debug("Database session closed")


@asynccontextmanager
async def get_db_ctxmgr():
    async with AsyncSessionFactory() as session:
        try:
            yield session
            # logger.debug("Database session created")
        finally:
            await session.close()
            # logger.debug("Database session closed")


async def close_db_connection():
    await async_engine.dispose()
    logger.info("Database connection closed")
