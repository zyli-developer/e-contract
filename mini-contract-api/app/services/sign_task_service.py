"""合同签署任务服务"""
from typing import List

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException, ValidationException
from app.core.response import PageResult
from app.models.sign_task import SignTask
from app.models.sign_task_participant import SignTaskParticipant
from app.schemas.contract import (
    ParticipantRequest,
    ParticipantResponse,
    SignTaskResponse,
    SignTaskStatistics,
)
from app.utils.pagination import paginate


def _participant_response(p: SignTaskParticipant) -> dict:
    return ParticipantResponse(
        id=p.id,
        name=p.name,
        mobile=p.mobile,
        status=p.status,
        order_num=p.order_num,
    ).model_dump()


async def create_sign_task(
    db: AsyncSession,
    creator_id: int,
    name: str,
    template_id: int | None = None,
    file_url: str | None = None,
    remark: str | None = None,
    participants: List[ParticipantRequest] | None = None,
) -> dict:
    """创建合同签署任务"""
    if not name:
        raise ValidationException("合同名称不能为空")
    if not template_id and not file_url:
        raise ValidationException("请选择模板或上传合同文件")

    # 创建签署任务
    task = SignTask(
        name=name,
        status=1,  # 草稿
        template_id=template_id,
        file_url=file_url,
        creator_id=creator_id,
        remark=remark,
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

    return SignTaskResponse(
        id=task.id,
        name=task.name,
        status=task.status,
        file_url=task.file_url,
        template_id=task.template_id,
        creator_id=task.creator_id,
        remark=task.remark,
        create_time=task.create_time.isoformat() if task.create_time else None,
        participants=participant_list,
    ).model_dump()


async def get_statistics(db: AsyncSession, creator_id: int) -> dict:
    """获取合同统计"""
    base = select(func.count()).select_from(SignTask).where(SignTask.creator_id == creator_id)

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
    query = select(SignTask).where(SignTask.creator_id == creator_id)

    if status is not None:
        query = query.where(SignTask.status == status)

    query = query.order_by(SignTask.create_time.desc())
    result = await paginate(db, query, page_no, page_size)

    task_list = []
    for task in result.list:
        # 查询签署方
        p_result = await db.execute(
            select(SignTaskParticipant)
            .where(SignTaskParticipant.task_id == task.id)
            .order_by(SignTaskParticipant.order_num)
        )
        participants = [_participant_response(p) for p in p_result.scalars().all()]

        task_list.append(SignTaskResponse(
            id=task.id,
            name=task.name,
            status=task.status,
            file_url=task.file_url,
            signed_file_url=task.signed_file_url,
            template_id=task.template_id,
            creator_id=task.creator_id,
            remark=task.remark,
            create_time=task.create_time.isoformat() if task.create_time else None,
            participants=participants,
        ).model_dump())

    result.list = task_list
    return result


async def get_task_detail(db: AsyncSession, task_id: int, user_id: int) -> dict:
    """获取合同详情"""
    result = await db.execute(select(SignTask).where(SignTask.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise BusinessException(code=404, msg="合同不存在")

    # 查询签署方
    p_result = await db.execute(
        select(SignTaskParticipant)
        .where(SignTaskParticipant.task_id == task.id)
        .order_by(SignTaskParticipant.order_num)
    )
    participants = [_participant_response(p) for p in p_result.scalars().all()]

    return SignTaskResponse(
        id=task.id,
        name=task.name,
        status=task.status,
        file_url=task.file_url,
        signed_file_url=task.signed_file_url,
        template_id=task.template_id,
        creator_id=task.creator_id,
        remark=task.remark,
        create_time=task.create_time.isoformat() if task.create_time else None,
        participants=participants,
    ).model_dump()


async def cancel_task(db: AsyncSession, task_id: int, user_id: int) -> None:
    """取消合同"""
    result = await db.execute(
        select(SignTask).where(SignTask.id == task_id, SignTask.creator_id == user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise BusinessException(code=404, msg="合同不存在")
    if task.status not in (1, 2):  # 只能取消草稿和签署中的
        raise BusinessException(code=400, msg="当前状态不允许取消")

    task.status = 4  # 已取消
    await db.flush()


async def delete_task(db: AsyncSession, task_id: int, user_id: int) -> None:
    """删除合同（只能删除草稿和已取消的）"""
    result = await db.execute(
        select(SignTask).where(SignTask.id == task_id, SignTask.creator_id == user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise BusinessException(code=404, msg="合同不存在")
    if task.status not in (1, 4):  # 只能删除草稿和已取消
        raise BusinessException(code=400, msg="当前状态不允许删除")

    await db.delete(task)
    # 删除签署方
    p_result = await db.execute(
        select(SignTaskParticipant).where(SignTaskParticipant.task_id == task_id)
    )
    for p in p_result.scalars().all():
        await db.delete(p)
    await db.flush()
