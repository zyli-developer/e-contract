from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ApiResponse
from app.database import get_db
from app.dependencies import get_current_user_id
from app.schemas.contract import (
    RejectRequest,
    SignRequest,
    SignTaskCreateRequest,
)
from app.services import sign_task_service
from app.services.evidence_service import get_evidence_list

router = APIRouter(prefix="/seal/sign-task", tags=["合同签署"])


def _client_ip(request: Request) -> str | None:
    """提取客户端 IP"""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _client_device(request: Request) -> str | None:
    """提取设备信息"""
    return request.headers.get("user-agent", "")[:255]


# --- 基础 CRUD ---

@router.get("/statistics")
async def get_statistics(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """合同统计"""
    result = await sign_task_service.get_statistics(db, user_id)
    return ApiResponse.success(data=result)


@router.get("/page")
async def list_tasks(
    status: int | None = None,
    pageNo: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=50),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """合同列表（分页）"""
    result = await sign_task_service.list_tasks(db, user_id, status, pageNo, pageSize)
    return ApiResponse.success(data=result.model_dump())


@router.get("/get")
async def get_task(
    request: Request,
    id: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """合同详情（同时记录查看证据）"""
    result = await sign_task_service.get_task_detail(db, id, user_id)

    # 记录签署方查看合同
    await sign_task_service.record_view(
        db, id, user_id,
        ip=_client_ip(request),
        device=_client_device(request),
    )
    await db.commit()

    return ApiResponse.success(data=result)


@router.post("/create")
async def create_task(
    req: SignTaskCreateRequest,
    request: Request,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """创建合同"""
    result = await sign_task_service.create_sign_task(
        db,
        creator_id=user_id,
        name=req.name,
        template_id=req.template_id,
        file_url=req.file_url,
        remark=req.remark,
        variables=req.variables,
        participants=req.participants,
        ip=_client_ip(request),
        device=_client_device(request),
    )
    return ApiResponse.success(data=result)


@router.delete("/cancel")
async def cancel_task(
    request: Request,
    id: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """取消合同"""
    await sign_task_service.cancel_task(
        db, id, user_id,
        ip=_client_ip(request),
        device=_client_device(request),
    )
    return ApiResponse.success()


@router.delete("/delete")
async def delete_task(
    id: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """删除合同"""
    await sign_task_service.delete_task(db, id, user_id)
    return ApiResponse.success()


# --- Phase 4: 签署流程 ---

@router.post("/{task_id}/initiate")
async def initiate_signing(
    task_id: int,
    request: Request,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """发起签署（草稿 → 签署中）"""
    result = await sign_task_service.initiate_signing(
        db, task_id, user_id,
        ip=_client_ip(request),
        device=_client_device(request),
    )
    return ApiResponse.success(data=result)


@router.post("/{task_id}/sign")
async def execute_sign(
    task_id: int,
    req: SignRequest,
    request: Request,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """执行签署"""
    result = await sign_task_service.execute_sign(
        db, task_id, user_id,
        seal_id=req.seal_id,
        variables=req.variables,
        ip=_client_ip(request),
        device=_client_device(request),
    )
    return ApiResponse.success(data=result)


@router.post("/{task_id}/reject")
async def reject_sign(
    task_id: int,
    req: RejectRequest,
    request: Request,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """拒签"""
    result = await sign_task_service.reject_sign(
        db, task_id, user_id,
        reason=req.reason,
        ip=_client_ip(request),
        device=_client_device(request),
    )
    return ApiResponse.success(data=result)


@router.get("/{task_id}/verify-hash")
async def verify_hash(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """校验文档哈希"""
    result = await sign_task_service.verify_document_hash(db, task_id)
    return ApiResponse.success(data=result)


@router.get("/{task_id}/evidence")
async def get_evidence(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取证据链"""
    result = await get_evidence_list(db, task_id)
    return ApiResponse.success(data=result)


@router.get("/validate-permission")
async def validate_permission(
    id: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """验证用户权限"""
    result = await sign_task_service.validate_permission(db, id, user_id)
    return ApiResponse.success(data=result)


@router.get("/{task_id}/download")
async def download_contract(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """下载已签署合同文件"""
    result = await sign_task_service.get_download_url(db, task_id, user_id)
    return ApiResponse.success(data=result)


@router.post("/{task_id}/urge")
async def urge_sign(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
):
    """催签（MVP 阶段仅返回成功）"""
    # TODO: 接入通知服务
    return ApiResponse.success(msg="催签通知已发送")
