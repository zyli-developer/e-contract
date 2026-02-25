"""印章管理服务"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException, ValidationException
from app.core.response import PageResult
from app.models.seal_info import SealInfo
from app.schemas.seal import SealResponse
from app.utils.pagination import paginate

VALID_SEAL_TYPES = {11, 12}  # 11=个人签名, 12=个人印章


def _to_response(seal: SealInfo) -> dict:
    return SealResponse(
        id=seal.id,
        name=seal.name,
        type=seal.type,
        seal_data=seal.seal_data,
        is_default=seal.is_default,
        create_time=seal.create_time.isoformat() if seal.create_time else None,
    ).model_dump()


async def list_seals(
    db: AsyncSession, member_id: int, page_no: int = 1, page_size: int = 10
) -> PageResult:
    """分页查询用户的印章列表"""
    query = (
        select(SealInfo)
        .where(SealInfo.member_id == member_id, SealInfo.status == 1)
        .order_by(SealInfo.is_default.desc(), SealInfo.create_time.desc())
    )
    result = await paginate(db, query, page_no, page_size)
    result.list = [_to_response(s) for s in result.list]
    return result


async def create_seal(
    db: AsyncSession, member_id: int, name: str, seal_type: int, seal_data: str
) -> dict:
    """创建印章"""
    if seal_type not in VALID_SEAL_TYPES:
        raise ValidationException(f"无效的印章类型: {seal_type}，仅支持 11(签名) 和 12(印章)")

    seal = SealInfo(
        name=name,
        type=seal_type,
        seal_data=seal_data,
        member_id=member_id,
        status=1,
        is_default=0,
    )
    db.add(seal)
    await db.flush()
    await db.refresh(seal)
    return _to_response(seal)


async def update_seal(
    db: AsyncSession, member_id: int, seal_id: int, name: str | None, seal_data: str | None
) -> dict:
    """更新印章"""
    result = await db.execute(
        select(SealInfo).where(SealInfo.id == seal_id, SealInfo.member_id == member_id)
    )
    seal = result.scalar_one_or_none()
    if not seal:
        raise BusinessException(code=404, msg="印章不存在")

    if name is not None:
        seal.name = name
    if seal_data is not None:
        seal.seal_data = seal_data

    await db.flush()
    await db.refresh(seal)
    return _to_response(seal)


async def delete_seal(db: AsyncSession, member_id: int, seal_id: int) -> None:
    """删除印章（软删除）"""
    result = await db.execute(
        select(SealInfo).where(SealInfo.id == seal_id, SealInfo.member_id == member_id)
    )
    seal = result.scalar_one_or_none()
    if not seal:
        raise BusinessException(code=404, msg="印章不存在")

    seal.status = 2  # 已吊销
    await db.flush()


async def set_default_seal(db: AsyncSession, member_id: int, seal_id: int) -> None:
    """设为默认印章（同类型只能有一个默认）"""
    result = await db.execute(
        select(SealInfo).where(SealInfo.id == seal_id, SealInfo.member_id == member_id, SealInfo.status == 1)
    )
    seal = result.scalar_one_or_none()
    if not seal:
        raise BusinessException(code=404, msg="印章不存在")

    # 取消同类型的其他默认
    await db.execute(
        update(SealInfo)
        .where(
            SealInfo.member_id == member_id,
            SealInfo.type == seal.type,
            SealInfo.is_default == 1,
        )
        .values(is_default=0)
    )

    # 设置当前为默认
    seal.is_default = 1
    await db.flush()
