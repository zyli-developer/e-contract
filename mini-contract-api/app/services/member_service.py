"""用户信息管理服务"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException, ErrorCode, ValidationException
from app.core.security import hash_password, verify_password
from app.models.member import Member
from app.schemas.member import UserInfoResponse
from app.utils.redis_client import delete_sms_code, get_sms_code


async def get_user_info(db: AsyncSession, user_id: int) -> UserInfoResponse:
    """获取当前用户信息"""
    result = await db.execute(select(Member).where(Member.id == user_id))
    member = result.scalar_one_or_none()

    if not member:
        raise BusinessException(code=ErrorCode.USER_NOT_FOUND, msg="用户不存在")

    return UserInfoResponse(
        id=member.id,
        mobile=member.mobile or "",
        nickname=member.nickname,
        avatar=member.avatar,
    )


async def update_user_info(
    db: AsyncSession,
    user_id: int,
    nickname: str | None = None,
    avatar: str | None = None,
) -> UserInfoResponse:
    """更新用户信息"""
    result = await db.execute(select(Member).where(Member.id == user_id))
    member = result.scalar_one_or_none()

    if not member:
        raise BusinessException(code=ErrorCode.USER_NOT_FOUND, msg="用户不存在")

    if nickname is not None:
        member.nickname = nickname
    if avatar is not None:
        member.avatar = avatar

    await db.flush()
    await db.refresh(member)

    return UserInfoResponse(
        id=member.id,
        mobile=member.mobile or "",
        nickname=member.nickname,
        avatar=member.avatar,
    )


async def update_password(
    db: AsyncSession,
    user_id: int,
    new_password: str,
    code: str,
) -> None:
    """修改密码（通过短信验证码验证身份）"""
    result = await db.execute(select(Member).where(Member.id == user_id))
    member = result.scalar_one_or_none()

    if not member:
        raise BusinessException(code=ErrorCode.USER_NOT_FOUND, msg="用户不存在")

    # 验证短信验证码（scene=3 修改密码）
    stored_code = await get_sms_code(member.mobile, scene=3)
    if not stored_code or stored_code != code:
        raise BusinessException(code=ErrorCode.SMS_CODE_INVALID, msg="验证码错误或已过期")

    await delete_sms_code(member.mobile, scene=3)

    if len(new_password) < 6:
        raise ValidationException("密码长度不能少于 6 位")

    member.password = hash_password(new_password)
    await db.flush()
