import time
import uuid

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件：记录请求耗时、方法、路径、状态码，附带 request_id"""

    async def dispatch(self, request: Request, call_next):
        request_id = uuid.uuid4().hex[:12]
        # 存入 request.state 供后续使用
        request.state.request_id = request_id

        start = time.time()
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "-"

        logger.info(
            "[%s] --> %s %s from %s",
            request_id, method, path, client_ip,
        )

        try:
            response = await call_next(request)
        except Exception:
            duration = round((time.time() - start) * 1000, 2)
            logger.error(
                "[%s] <-- %s %s 500 (unhandled exception) %.2fms",
                request_id, method, path, duration,
            )
            raise

        duration = round((time.time() - start) * 1000, 2)
        response.headers["X-Process-Time"] = str(duration)
        response.headers["X-Request-Id"] = request_id

        log_fn = logger.info if response.status_code < 400 else logger.warning
        log_fn(
            "[%s] <-- %s %s %d %.2fms",
            request_id, method, path, response.status_code, duration,
        )

        return response
