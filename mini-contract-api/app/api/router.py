from fastapi import APIRouter

from app.api.v1 import auth, file, member, seal_info, seal_template, sign_task

api_router = APIRouter(prefix="/api/v1")

# 认证模块
api_router.include_router(auth.router)
api_router.include_router(member.router)

# 印章管理
api_router.include_router(seal_info.router)

# 合同签署
api_router.include_router(sign_task.router)

# 合同模板
api_router.include_router(seal_template.router)

# 文件管理
api_router.include_router(file.router)
