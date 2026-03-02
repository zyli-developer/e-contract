"""
集中式日志配置模块（基于 Loguru）

功能：
- 控制台彩色输出 + 文件双输出
- 日志文件按大小自动轮转（单文件 10MB，保留 5 个备份）
- 拦截标准库 logging，让 uvicorn / sqlalchemy 等第三方日志统一走 loguru
- 异步安全（enqueue=True）
"""
import logging
import os
import sys

from loguru import logger


class _InterceptHandler(logging.Handler):
    """拦截标准库 logging，转发到 loguru"""

    def emit(self, record: logging.LogRecord) -> None:
        # 映射标准库级别到 loguru 级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 找到实际的调用帧，跳过 logging 内部帧
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(*, debug: bool = False, log_dir: str = "logs") -> None:
    """初始化全局日志配置

    Args:
        debug: 是否启用 DEBUG 级别日志
        log_dir: 日志文件存放目录
    """
    os.makedirs(log_dir, exist_ok=True)

    log_level = "DEBUG" if debug else "INFO"

    # 清除 loguru 默认 handler，重新配置
    logger.remove()

    # 控制台 handler — 彩色输出
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <7}</level> | "
               "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        enqueue=True,
    )

    # 文件 handler — 全量日志
    logger.add(
        os.path.join(log_dir, "app.log"),
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <7} | {name}:{line} | {message}",
        rotation="10 MB",
        retention=5,
        encoding="utf-8",
        enqueue=True,
    )

    # 文件 handler — 仅错误日志（含完整堆栈）
    logger.add(
        os.path.join(log_dir, "error.log"),
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <7} | {name}:{line} | {message}",
        rotation="10 MB",
        retention=5,
        encoding="utf-8",
        enqueue=True,
        backtrace=True,
        diagnose=debug,
    )

    # 拦截标准库 logging → loguru
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)

    # 降低第三方库日志噪声
    for lib in ("uvicorn.access", "uvicorn.error", "sqlalchemy.engine",
                "httpx", "httpcore", "passlib"):
        logging.getLogger(lib).setLevel(
            logging.DEBUG if debug and lib == "sqlalchemy.engine" else logging.WARNING
        )
