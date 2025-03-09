# app/core/config.py

from typing import List
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings
from decimal import Decimal


class Settings(BaseSettings):
    # Loguru日志配置
    LOG_FILE_PATH: str = Field(default="logs/app.log", description="日志文件路径")
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FORMAT: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="日志格式",
    )
    LOG_ROTATION: str = Field(default="1 week", description="日志轮换时间")
    LOG_RETENTION: str = Field(default="1 month", description="日志保留时间")
    LOG_COMPRESSION: str = Field(default="zip", description="日志压缩格式")

    # 服务器配置
    SERVER_HOST: str = Field(default="0.0.0.0", description="服务器主机地址")
    SERVER_PORT: int = Field(default=9981, description="服务器端口号")
    CORS_ORIGINS: List[str] = Field(default=["*"], description="允许跨域请求的源")

    # 其他配置
    DEBUG: bool = Field(default=False, description="是否开启调试模式")

    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///data.db", description="数据库连接字符串"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, description="数据库连接池大小")

    # SSE回传最多消息
    SSE_MAX_MSG: int = Field(default=2, description="SSE回传最多消息")

    class Config:
        env_file = ".env"  # 读取.env文件中的环境变量
        case_sensitive = True  # 环境变量区分大小写


settings = Settings()
pass
