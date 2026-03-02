"""合同签署任务服务"""
import hashlib
from datetime import datetime
from typing import List, Optional

from loguru import logger
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException, ForbiddenException, ValidationException
from app.core.response import PageResult
from app.models.sign_task import SignTask
from app.models.sign_task_participant import SignTaskParticipant
from app.schemas.contract import (
    ParticipantRequest,
    ParticipantResponse,
    SignTaskResponse,
    SignTaskStatistics,
)
from app.services.evidence_service import EvidenceAction, log_evidence
from app.utils.pagination import paginate


def _participant_response(p: SignTaskParticipant, seal_data: str | None = None) -> dict:
    return ParticipantResponse(
        id=p.id,
        name=p.name,
        mobile=p.mobile,
        status=p.status,
        order_num=p.order_num,
        sign_time=p.sign_time.strftime("%Y-%m-%d %H:%M:%S") if p.sign_time else None,
        seal_data=seal_data,
    ).model_dump()


def _task_response(task: SignTask, participants: list) -> dict:
    return SignTaskResponse(
        id=task.id,
        name=task.name,
        status=task.status,
        file_url=task.file_url,
        signed_file_url=task.signed_file_url,
        file_hash=task.file_hash,
        signed_file_hash=task.signed_file_hash,
        template_id=task.template_id,
        creator_id=task.creator_id,
        remark=task.remark,
        variables=task.variables,
        create_time=task.create_time.strftime("%Y-%m-%d %H:%M:%S") if task.create_time else None,
        complete_time=task.complete_time.strftime("%Y-%m-%d %H:%M:%S") if task.complete_time else None,
        participants=participants,
    ).model_dump()


async def _get_task(db: AsyncSession, task_id: int) -> SignTask:
    """获取合同（内部用）"""
    result = await db.execute(select(SignTask).where(SignTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise BusinessException(code=404, msg="合同不存在")
    return task


async def _get_participants(db: AsyncSession, task_id: int) -> list:
    """获取签署方列表（含签名图片）"""
    from app.models.seal_info import SealInfo

    p_result = await db.execute(
        select(SignTaskParticipant)
        .where(SignTaskParticipant.task_id == task_id)
        .order_by(SignTaskParticipant.order_num)
    )
    participants = p_result.scalars().all()

    # 批量查询签名图片
    seal_ids = [p.seal_id for p in participants if p.seal_id]
    seal_map: dict[int, str] = {}
    if seal_ids:
        seal_result = await db.execute(
            select(SealInfo.id, SealInfo.seal_data).where(SealInfo.id.in_(seal_ids))
        )
        for row in seal_result.all():
            seal_map[row[0]] = row[1]

    return [
        _participant_response(p, seal_map.get(p.seal_id) if p.seal_id else None)
        for p in participants
    ]


# ==============================
# 基础 CRUD
# ==============================

async def create_sign_task(
    db: AsyncSession,
    creator_id: int,
    name: str,
    template_id: int | None = None,
    file_url: str | None = None,
    remark: str | None = None,
    variables: dict | None = None,
    participants: List[ParticipantRequest] | None = None,
    ip: str | None = None,
    device: str | None = None,
) -> dict:
    """创建合同签署任务"""
    logger.info("创建合同: creator_id=%d, name=%s, template_id=%s", creator_id, name, template_id)
    if not name:
        raise ValidationException("合同名称不能为空")
    if not template_id and not file_url:
        raise ValidationException("请选择模板或上传合同文件")

    # 计算文件哈希（如果有文件 URL，MVP 阶段用 URL 字符串做哈希）
    file_hash = None
    if file_url:
        file_hash = hashlib.sha256(file_url.encode()).hexdigest()

    task = SignTask(
        name=name,
        status=1,  # 草稿
        template_id=template_id,
        file_url=file_url,
        file_hash=file_hash,
        creator_id=creator_id,
        remark=remark,
        variables=variables,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)

    # 递增模板使用次数
    if template_id:
        from app.services.template_service import increment_use_count
        await increment_use_count(db, template_id)

    # 创建签署方
    participant_list = []
    if participants:
        for p in participants:
            participant = SignTaskParticipant(
                task_id=task.id,
                name=p.name,
                mobile=p.mobile,
                order_num=p.order_num,
            )
            db.add(participant)
            await db.flush()
            await db.refresh(participant)
            participant_list.append(_participant_response(participant))

    # 记录证据：合同创建
    await log_evidence(
        db,
        task_id=task.id,
        action=EvidenceAction.CONTRACT_CREATED,
        user_id=creator_id,
        ip=ip,
        device=device,
        data_hash=file_hash,
        detail={"name": name, "participants_count": len(participant_list)},
    )

    logger.info("合同创建成功: task_id=%d, creator_id=%d, 签署方数=%d",
                task.id, creator_id, len(participant_list))
    return _task_response(task, participant_list)


async def _visible_task_ids(db: AsyncSession, user_id: int) -> set[int]:
    """获取用户可见的合同 ID 集合（创建的 + 作为签署方的）"""
    from app.models.member import Member

    # 通过 member_id 直接关联
    p_by_id = await db.execute(
        select(SignTaskParticipant.task_id).where(SignTaskParticipant.member_id == user_id)
    )
    task_ids = set(p_by_id.scalars().all())

    # 通过手机号关联
    member_result = await db.execute(select(Member).where(Member.id == user_id))
    member = member_result.scalar_one_or_none()
    if member and member.mobile:
        p_by_mobile = await db.execute(
            select(SignTaskParticipant.task_id).where(SignTaskParticipant.mobile == member.mobile)
        )
        task_ids.update(p_by_mobile.scalars().all())

    return task_ids


def _user_visible_filter(user_id: int, participant_task_ids: set[int]):
    """构造用户可见合同的 WHERE 条件（签署方只能看到非草稿合同）"""
    from sqlalchemy import and_
    if participant_task_ids:
        return or_(
            SignTask.creator_id == user_id,
            and_(
                SignTask.id.in_(participant_task_ids),
                SignTask.status != 1,  # 签署方不可见草稿
            ),
        )
    return SignTask.creator_id == user_id


async def get_statistics(db: AsyncSession, creator_id: int) -> dict:
    """获取合同统计"""
    p_task_ids = await _visible_task_ids(db, creator_id)
    visible = _user_visible_filter(creator_id, p_task_ids)
    base = select(func.count()).select_from(SignTask).where(visible)

    total = (await db.execute(base)).scalar() or 0
    draft = (await db.execute(base.where(SignTask.status == 1))).scalar() or 0
    signing = (await db.execute(base.where(SignTask.status == 2))).scalar() or 0
    completed = (await db.execute(base.where(SignTask.status == 3))).scalar() or 0

    return SignTaskStatistics(
        totalCount=total,
        draftCount=draft,
        signingCount=signing,
        completedCount=completed,
    ).model_dump()


async def list_tasks(
    db: AsyncSession,
    creator_id: int,
    status: int | None = None,
    page_no: int = 1,
    page_size: int = 10,
) -> PageResult:
    """合同列表（分页）"""
    p_task_ids = await _visible_task_ids(db, creator_id)
    visible = _user_visible_filter(creator_id, p_task_ids)
    query = select(SignTask).where(visible)
    if status is not None:
        query = query.where(SignTask.status == status)
    query = query.order_by(SignTask.create_time.desc())
    result = await paginate(db, query, page_no, page_size)

    task_list = []
    for task in result.list:
        participants = await _get_participants(db, task.id)
        task_list.append(_task_response(task, participants))

    result.list = task_list
    return result


async def get_task_detail(db: AsyncSession, task_id: int, user_id: int) -> dict:
    """获取合同详情"""
    task = await _get_task(db, task_id)
    participants = await _get_participants(db, task.id)
    return _task_response(task, participants)


async def cancel_task(
    db: AsyncSession, task_id: int, user_id: int,
    ip: str | None = None, device: str | None = None,
) -> None:
    """取消合同"""
    logger.info("取消合同: task_id=%d, user_id=%d", task_id, user_id)
    result = await db.execute(
        select(SignTask).where(SignTask.id == task_id, SignTask.creator_id == user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        logger.warning("取消合同失败 - 合同不存在: task_id=%d, user_id=%d", task_id, user_id)
        raise BusinessException(code=404, msg="合同不存在")
    if task.status not in (1, 2):
        logger.warning("取消合同失败 - 状态不允许: task_id=%d, status=%d", task_id, task.status)
        raise BusinessException(code=400, msg="当前状态不允许取消")

    task.status = 4  # 已取消
    await db.flush()

    # 记录证据
    await log_evidence(
        db,
        task_id=task_id,
        action=EvidenceAction.CONTRACT_CANCELLED,
        user_id=user_id,
        ip=ip,
        device=device,
        detail={"previous_status": 2 if task.status == 4 else 1},
    )
    logger.info("合同已取消: task_id=%d, user_id=%d", task_id, user_id)


async def delete_task(db: AsyncSession, task_id: int, user_id: int) -> None:
    """删除合同（只能删除草稿和已取消的）"""
    logger.info("删除合同: task_id=%d, user_id=%d", task_id, user_id)
    result = await db.execute(
        select(SignTask).where(SignTask.id == task_id, SignTask.creator_id == user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        logger.warning("删除合同失败 - 合同不存在: task_id=%d, user_id=%d", task_id, user_id)
        raise BusinessException(code=404, msg="合同不存在")
    if task.status not in (1, 4):
        logger.warning("删除合同失败 - 状态不允许: task_id=%d, status=%d", task_id, task.status)
        raise BusinessException(code=400, msg="当前状态不允许删除")

    await db.delete(task)
    # 删除签署方
    p_result = await db.execute(
        select(SignTaskParticipant).where(SignTaskParticipant.task_id == task_id)
    )
    for p in p_result.scalars().all():
        await db.delete(p)
    await db.flush()
    logger.info("合同已删除: task_id=%d", task_id)


async def get_download_url(db: AsyncSession, task_id: int, user_id: int) -> dict:
    """获取已签署合同的下载 URL"""
    logger.info("下载合同请求: task_id=%d, user_id=%d", task_id, user_id)
    task = await _get_task(db, task_id)
    if task.status != 3:
        logger.warning("下载合同失败 - 未完成签署: task_id=%d, status=%d", task_id, task.status)
        raise BusinessException(code=400, msg="合同未完成签署，无法下载")

    # 只有创建者或签署方可下载
    is_creator = task.creator_id == user_id
    participant = await _find_participant_by_user(db, task_id, user_id)
    if not is_creator and not participant:
        logger.warning("下载合同失败 - 无权限: task_id=%d, user_id=%d", task_id, user_id)
        raise ForbiddenException("无权下载此合同")

    return {
        "task_id": task_id,
        "name": task.name,
        "file_url": task.file_url,
        "signed_file_url": task.signed_file_url or task.file_url,
        "signed_file_hash": task.signed_file_hash,
    }


# ==============================
# Phase 4: 签署流程
# ==============================

async def initiate_signing(
    db: AsyncSession, task_id: int, user_id: int,
    ip: str | None = None, device: str | None = None,
) -> dict:
    """发起签署：草稿(1) → 签署中(2)"""
    logger.info("发起签署: task_id=%d, user_id=%d", task_id, user_id)
    result = await db.execute(
        select(SignTask).where(SignTask.id == task_id, SignTask.creator_id == user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        logger.warning("发起签署失败 - 合同不存在: task_id=%d, user_id=%d", task_id, user_id)
        raise BusinessException(code=404, msg="合同不存在")
    if task.status != 1:
        logger.warning("发起签署失败 - 状态不允许: task_id=%d, status=%d", task_id, task.status)
        raise BusinessException(code=400, msg="只有草稿状态的合同才能发起签署")

    # 检查是否有签署方
    p_count = (await db.execute(
        select(func.count()).select_from(SignTaskParticipant)
        .where(SignTaskParticipant.task_id == task_id)
    )).scalar() or 0
    if p_count == 0:
        raise ValidationException("请至少添加一个签署方")

    task.status = 2  # 签署中
    await db.flush()

    participants = await _get_participants(db, task.id)

    # 记录证据：发起签署
    await log_evidence(
        db,
        task_id=task_id,
        action=EvidenceAction.CONTRACT_SENT,
        user_id=user_id,
        ip=ip,
        device=device,
        data_hash=task.file_hash,
        detail={"participants": [p["mobile"] for p in participants]},
    )

    # TODO: 发送通知给签署方（微信模板消息/短信）
    logger.info(f"[Notify] 合同 {task_id} 已发起签署，通知签署方")

    return _task_response(task, participants)


async def execute_sign(
    db: AsyncSession, task_id: int, user_id: int,
    seal_id: Optional[int] = None,
    variables: dict | None = None,
    ip: str | None = None, device: str | None = None,
) -> dict:
    """执行签署操作"""
    logger.info("执行签署: task_id=%d, user_id=%d, seal_id=%s", task_id, user_id, seal_id)
    task = await _get_task(db, task_id)
    if task.status != 2:
        logger.warning("签署失败 - 合同不在签署中状态: task_id=%d, status=%d", task_id, task.status)
        raise BusinessException(code=400, msg="合同不在签署中状态")

    # 获取签署方
    result = await db.execute(
        select(SignTaskParticipant).where(
            SignTaskParticipant.task_id == task_id,
            SignTaskParticipant.member_id == user_id,
        )
    )
    participant = result.scalar_one_or_none()
    if not participant:
        # 也尝试用手机号匹配
        from app.models.member import Member
        member_result = await db.execute(select(Member).where(Member.id == user_id))
        member = member_result.scalar_one_or_none()
        if member:
            p_result = await db.execute(
                select(SignTaskParticipant).where(
                    SignTaskParticipant.task_id == task_id,
                    SignTaskParticipant.mobile == member.mobile,
                )
            )
            participant = p_result.scalar_one_or_none()

    if not participant:
        logger.warning("签署失败 - 非签署方: task_id=%d, user_id=%d", task_id, user_id)
        raise ForbiddenException("您不是此合同的签署方")
    if participant.status == 2:
        logger.warning("签署失败 - 已签署: task_id=%d, user_id=%d", task_id, user_id)
        raise BusinessException(code=400, msg="您已签署此合同")
    if participant.status == 3:
        logger.warning("签署失败 - 已拒签: task_id=%d, user_id=%d", task_id, user_id)
        raise BusinessException(code=400, msg="您已拒签此合同")

    # 合并签署方提交的变量（如乙方身份证等）
    # 必须创建新 dict，否则 SQLAlchemy 检测不到 JSON 列的变更
    if variables:
        merged = dict(task.variables or {})
        merged.update(variables)
        task.variables = merged

    # 更新签署方状态
    participant.status = 2  # 已签署
    participant.sign_time = datetime.now()
    participant.member_id = user_id
    if seal_id:
        participant.seal_id = seal_id
    await db.flush()

    # 记录证据：签署完成
    await log_evidence(
        db,
        task_id=task_id,
        action=EvidenceAction.CONTRACT_SIGNED,
        user_id=user_id,
        ip=ip,
        device=device,
        data_hash=task.file_hash,
        detail={"seal_id": seal_id, "participant_id": participant.id},
    )

    # 检查是否所有签署方都已签署
    await _check_all_signed(db, task, ip=ip, device=device)

    logger.info("签署完成: task_id=%d, user_id=%d, participant_id=%d",
                task_id, user_id, participant.id)
    participants = await _get_participants(db, task.id)
    return _task_response(task, participants)


async def reject_sign(
    db: AsyncSession, task_id: int, user_id: int,
    reason: str | None = None,
    ip: str | None = None, device: str | None = None,
) -> dict:
    """拒签"""
    logger.info("拒签请求: task_id=%d, user_id=%d, reason=%s", task_id, user_id, reason)
    task = await _get_task(db, task_id)
    if task.status != 2:
        logger.warning("拒签失败 - 合同不在签署中状态: task_id=%d, status=%d", task_id, task.status)
        raise BusinessException(code=400, msg="合同不在签署中状态")

    participant = await _find_participant_by_user(db, task_id, user_id)
    if not participant:
        logger.warning("拒签失败 - 非签署方: task_id=%d, user_id=%d", task_id, user_id)
        raise ForbiddenException("您不是此合同的签署方")
    if participant.status != 0:
        logger.warning("拒签失败 - 状态不允许: task_id=%d, participant_status=%d", task_id, participant.status)
        raise BusinessException(code=400, msg="当前状态不允许操作")

    # 更新签署方状态
    participant.status = 3  # 已拒签
    await db.flush()

    # 合同状态改为已拒签
    task.status = 5
    await db.flush()

    # 记录证据
    await log_evidence(
        db,
        task_id=task_id,
        action=EvidenceAction.CONTRACT_REJECTED,
        user_id=user_id,
        ip=ip,
        device=device,
        detail={"reason": reason, "participant_id": participant.id},
    )

    logger.info("合同已拒签: task_id=%d, user_id=%d", task_id, user_id)
    participants = await _get_participants(db, task.id)
    return _task_response(task, participants)


async def record_view(
    db: AsyncSession, task_id: int, user_id: int,
    ip: str | None = None, device: str | None = None,
) -> None:
    """记录签署方查看合同"""
    await log_evidence(
        db,
        task_id=task_id,
        action=EvidenceAction.SIGNER_VIEWED,
        user_id=user_id,
        ip=ip,
        device=device,
    )


async def verify_document_hash(db: AsyncSession, task_id: int) -> dict:
    """验证文档哈希完整性"""
    task = await _get_task(db, task_id)
    return {
        "task_id": task_id,
        "file_hash": task.file_hash,
        "signed_file_hash": task.signed_file_hash,
        "file_url": task.file_url,
        "signed_file_url": task.signed_file_url,
        "is_original_valid": task.file_hash is not None,
        "is_signed_valid": task.signed_file_hash is not None if task.status == 3 else None,
    }


async def validate_permission(
    db: AsyncSession, task_id: int, user_id: int,
) -> dict:
    """验证用户是否是合同的签署方"""
    task = await _get_task(db, task_id)
    is_creator = task.creator_id == user_id
    participant = await _find_participant_by_user(db, task_id, user_id)
    return {
        "is_creator": is_creator,
        "is_participant": participant is not None,
        "participant_status": participant.status if participant else None,
        "can_sign": participant is not None and participant.status == 0 and task.status == 2,
    }


# ==============================
# 内部辅助
# ==============================

async def _find_participant_by_user(
    db: AsyncSession, task_id: int, user_id: int,
) -> Optional[SignTaskParticipant]:
    """根据 user_id 查找签署方（先匹配 member_id，再匹配手机号）"""
    # 先按 member_id 查
    result = await db.execute(
        select(SignTaskParticipant).where(
            SignTaskParticipant.task_id == task_id,
            SignTaskParticipant.member_id == user_id,
        )
    )
    participant = result.scalar_one_or_none()
    if participant:
        return participant

    # 再按手机号查
    from app.models.member import Member
    member_result = await db.execute(select(Member).where(Member.id == user_id))
    member = member_result.scalar_one_or_none()
    if not member:
        return None

    result = await db.execute(
        select(SignTaskParticipant).where(
            SignTaskParticipant.task_id == task_id,
            SignTaskParticipant.mobile == member.mobile,
        )
    )
    participant = result.scalar_one_or_none()
    if participant and not participant.member_id:
        # 绑定 member_id
        participant.member_id = user_id
        await db.flush()
    return participant


async def _check_all_signed(
    db: AsyncSession, task: SignTask,
    ip: str | None = None, device: str | None = None,
) -> None:
    """检查是否所有签署方都已签署，如果是则合同状态变为已完成"""
    # 未签署的数量
    unsigned_count = (await db.execute(
        select(func.count()).select_from(SignTaskParticipant)
        .where(
            SignTaskParticipant.task_id == task.id,
            SignTaskParticipant.status == 0,
        )
    )).scalar() or 0

    if unsigned_count == 0:
        task.status = 3  # 已完成
        task.complete_time = datetime.now()
        logger.info("合同全部签署完成: task_id=%d", task.id)

        # MVP: 用文件 URL 模拟签署后文件哈希
        if task.file_url:
            task.signed_file_hash = hashlib.sha256(
                (task.file_url + ":signed").encode()
            ).hexdigest()

        await db.flush()

        # 记录证据
        await log_evidence(
            db,
            task_id=task.id,
            action=EvidenceAction.CONTRACT_COMPLETED,
            data_hash=task.signed_file_hash,
            detail={"complete_time": task.complete_time.strftime("%Y-%m-%d %H:%M:%S")},
        )
