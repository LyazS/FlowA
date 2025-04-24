# app/utils/logging.py

import sys
from loguru import logger
from app.core.config import settings


def init_logging(log_path):
    # 移除默认的日志记录器
    logger.remove()

    # 添加配置
    if log_path == "sys.stdout":
        logger.add(
            sink=sys.stdout,  # 日志文件的路径
            level=settings.LOG_LEVEL,  # 日志级别
            enqueue=True,  # 异步写入日志
            backtrace=True,  # 启用回溯
            diagnose=settings.DEBUG,  # 在调试模式中记录详细的异常信息
        )
    else:
        logger.add(
            sink=log_path,  # 日志文件的路径
            level=settings.LOG_LEVEL,  # 日志级别
            format=settings.LOG_FORMAT,  # 日志格式
            rotation=settings.LOG_ROTATION,  # 日志轮换时间
            retention=settings.LOG_RETENTION,  # 日志保留时间
            compression=settings.LOG_COMPRESSION,  # 日志压缩格式
            enqueue=True,  # 异步写入日志
            backtrace=True,  # 启用回溯
            diagnose=settings.DEBUG,  # 在调试模式中记录详细的异常信息
        )

    logger.info("Logging has been initialized.")
    logger.debug(f"Log path: {log_path}")
