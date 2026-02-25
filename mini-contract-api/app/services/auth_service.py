"""认证服务：登录注册、Token 生成/刷新"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import (
    BusinessException,
    ErrorCode,
    UnauthorizedException,
    ValidationException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.member import Member
from app.models.member_social import MemberSocialUser
from app.models.member_token import MemberToken
from app.schemas.auth import AuthTokenResponse
from app.utils.redis_client import delete_sms_code, get_sms_code


async def _create_token_record(db: AsyncSession, member_id: int) -> AuthTokenResponse:
    """为用户创建 Token 记录并返回响应"""
    access_token = create_access_token(member_id)
    refresh_token = create_refresh_token(member_id)

    now = datetime.now(timezone.utc)
    token_record = MemberToken(
        member_id=member_id,
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expire_time=now + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
        refresh_token_expire_time=now + timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS),
    )
    db.add(token_record)
    await db.flush()

    expires_time = int((now + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)).timestamp() * 1000)

    return AuthTokenResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        userId=member_id,
        expiresTime=expires_time,
    )


async def _get_or_create_member_by_mobile(db: AsyncSession, mobile: str) -> Member:
    """根据手机号获取或创建用户（登录即注册）"""
    result = await db.execute(select(Member).where(Member.mobile == mobile))
    member = result.scalar_one_or_none()
    if member:
        if member.status == 0:
            raise BusinessException(code=1012001003, msg="账号已被禁用")
        return member

    # 自动注册
    member = Member(mobile=mobile, nickname=f"用户{mobile[-4:]}")
    db.add(member)
    await db.flush()
    await db.refresh(member)
    return member


async def login_by_password(db: AsyncSession, mobile: str, password: str) -> AuthTokenResponse:
    """密码登录"""
    result = await db.execute(select(Member).where(Member.mobile == mobile))
    member = result.scalar_one_or_none()

    if not member:
        raise BusinessException(code=ErrorCode.USER_NOT_FOUND, msg="用户不存在")
    if member.status == 0:
        raise BusinessException(code=1012001003, msg="账号已被禁用")
    if not member.password:
        raise ValidationException("该账号未设置密码，请使用短信验证码登录")
    if not verify_password(password, member.password):
        raise ValidationException("密码错误")

    return await _create_token_record(db, member.id)


async def login_by_sms(db: AsyncSession, mobile: str, code: str) -> AuthTokenResponse:
    """短信验证码登录（登录即注册）"""
    # 验证短信验证码
    stored_code = await get_sms_code(mobile, scene=1)
    if not stored_code or stored_code != code:
        raise BusinessException(code=ErrorCode.SMS_CODE_INVALID, msg="验证码错误或已过期")

    # 删除已使用的验证码
    await delete_sms_code(mobile, scene=1)

    member = await _get_or_create_member_by_mobile(db, mobile)
    return await _create_token_record(db, member.id)


async def login_by_social(db: AsyncSession, social_type: int, code: str) -> AuthTokenResponse:
    """社交登录（微信小程序）"""
    from app.services.wechat_service import code2session

    wechat_data = await code2session(code)
    openid = wechat_data["openid"]
    unionid = wechat_data.get("unionid")

    # 查找已绑定的社交账户
    result = await db.execute(
        select(MemberSocialUser).where(
            MemberSocialUser.type == social_type,
            MemberSocialUser.openid == openid,
        )
    )
    social_user = result.scalar_one_or_none()

    if social_user:
        # 已绑定：直接返回 Token
        member_result = await db.execute(select(Member).where(Member.id == social_user.member_id))
        member = member_result.scalar_one_or_none()
        if not member or member.status == 0:
            raise BusinessException(code=1012001003, msg="账号已被禁用")
        return await _create_token_record(db, member.id)

    # 未绑定：创建新用户 + 社交绑定
    member = Member(nickname="微信用户")
    db.add(member)
    await db.flush()
    await db.refresh(member)

    social_user = MemberSocialUser(
        member_id=member.id,
        type=social_type,
        openid=openid,
        unionid=unionid,
    )
    db.add(social_user)
    await db.flush()

    return await _create_token_record(db, member.id)


async def refresh_token(db: AsyncSession, refresh_token_str: str) -> AuthTokenResponse:
    """刷新 Token（Refresh Token 单次使用 + 乐观锁防重放）"""
    # 解码 refresh token
    try:
        payload = decode_token(refresh_token_str)
    except Exception:
        raise UnauthorizedException("Refresh Token 无效")

    if payload.get("type") != "refresh":
        raise UnauthorizedException("Token 类型无效")

    member_id = int(payload["sub"])

    # 查找 token 记录，乐观锁：只更新 used=0 的记录
    result = await db.execute(
        select(MemberToken).where(
            MemberToken.refresh_token == refresh_token_str,
            MemberToken.refresh_token_used == 0,
        )
    )
    token_record = result.scalar_one_or_none()

    if not token_record:
        raise UnauthorizedException("Refresh Token 已使用或不存在")

    # 标记为已使用（乐观锁防并发重放）
    stmt = (
        update(MemberToken)
        .where(MemberToken.id == token_record.id, MemberToken.refresh_token_used == 0)
        .values(refresh_token_used=1)
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise UnauthorizedException("Refresh Token 已被使用")

    return await _create_token_record(db, member_id)


async def logout(db: AsyncSession, user_id: int) -> None:
    """退出登录：标记所有 Token 为已使用"""
    await db.execute(
        update(MemberToken)
        .where(MemberToken.member_id == user_id, MemberToken.refresh_token_used == 0)
        .values(refresh_token_used=1)
    )
