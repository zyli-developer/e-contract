import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    """多租户中间件：从请求头提取 tenant-id 并注入到 request.state"""

    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("tenant-id", "1")
        request.state.tenant_id = int(tenant_id)
        response = await call_next(request)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件：记录请求耗时"""

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round((time.time() - start) * 1000, 2)
        response.headers["X-Process-Time"] = str(duration)
        return response
