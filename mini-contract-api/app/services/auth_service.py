"""认证服务：登录注册、Token 生成/刷新"""
from datetime import datetime, timedelta, timezone

from loguru import logger
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
from app.models.member_token import MemberToken
from app.schemas.auth import AuthTokenResponse


async def _create_token_record(db: AsyncSession, member_id: int, role: str = "landlord") -> AuthTokenResponse:
    """为用户创建 Token 记录并返回响应"""
    access_token = create_access_token(member_id)
    refresh_token = create_refresh_token(member_id)

    # 使用 UTC 时间但不带时区信息，与数据库 TIMESTAMP WITHOUT TIME ZONE 列匹配
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    token_record = MemberToken(
        member_id=member_id,
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expire_time=now + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
        refresh_token_expire_time=now + timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS),
    )
    db.add(token_record)
    await db.flush()

    expires_time = int((now + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)).replace(tzinfo=timezone.utc).timestamp() * 1000)

    return AuthTokenResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        userId=member_id,
        expiresTime=expires_time,
        role=role,
    )


async def login_by_password(db: AsyncSession, mobile: str, password: str) -> AuthTokenResponse:
    """密码登录"""
    logger.info("用户登录请求: mobile=%s", mobile)
    result = await db.execute(select(Member).where(Member.mobile == mobile))
    member = result.scalar_one_or_none()

    if not member:
        logger.warning("登录失败 - 用户不存在: mobile=%s", mobile)
        raise BusinessException(code=ErrorCode.USER_NOT_FOUND, msg="用户不存在")
    if member.status == 0:
        logger.warning("登录失败 - 账号已禁用: user_id=%d, mobile=%s", member.id, mobile)
        raise BusinessException(code=1012001003, msg="账号已被禁用")
    if not member.password:
        logger.warning("登录失败 - 未设置密码: user_id=%d, mobile=%s", member.id, mobile)
        raise ValidationException("该账号未设置密码")
    if not verify_password(password, member.password):
        logger.warning("登录失败 - 密码错误: user_id=%d, mobile=%s", member.id, mobile)
        raise ValidationException("密码错误")

    logger.info("登录成功: user_id=%d, mobile=%s, role=%s", member.id, mobile, member.role)
    return await _create_token_record(db, member.id, role=member.role or "landlord")


async def register(db: AsyncSession, mobile: str, password: str, nickname: str | None = None, role: str | None = None) -> AuthTokenResponse:
    """用户注册"""
    logger.info("用户注册请求: mobile=%s, role=%s", mobile, role)
    if len(mobile) != 11:
        logger.warning("注册失败 - 手机号格式不正确: mobile=%s", mobile)
        raise ValidationException("手机号格式不正确")
    if len(password) < 6:
        raise ValidationException("密码长度不能少于 6 位")

    # 校验角色值
    valid_role = role if role in ("landlord", "tenant") else "landlord"

    # 检查手机号是否已注册
    result = await db.execute(select(Member).where(Member.mobile == mobile))
    existing = result.scalar_one_or_none()
    if existing:
        logger.warning("注册失败 - 手机号已注册: mobile=%s", mobile)
        raise BusinessException(code=ErrorCode.MOBILE_ALREADY_EXISTS, msg="该手机号已注册")

    member = Member(
        mobile=mobile,
        password=hash_password(password),
        nickname=nickname or f"用户{mobile[-4:]}",
        role=valid_role,
    )
    db.add(member)
    await db.flush()
    await db.refresh(member)

    logger.info("注册成功: user_id=%s, mobile=%s, role=%s", member.id, mobile, valid_role)
    return await _create_token_record(db, member.id, role=member.role or "landlord")


async def refresh_token(db: AsyncSession, refresh_token_str: str) -> AuthTokenResponse:
    """刷新 Token（Refresh Token 单次使用 + 乐观锁防重放）"""
    logger.info("刷新 Token 请求")
    # 解码 refresh token
    try:
        payload = decode_token(refresh_token_str)
    except Exception:
        logger.warning("刷新 Token 失败 - Token 解码失败")
        raise UnauthorizedException("Refresh Token 无效")

    if payload.get("type") != "refresh":
        logger.warning("刷新 Token 失败 - Token 类型无效: type=%s", payload.get("type"))
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
        logger.warning("刷新 Token 失败 - Token 已使用或不存在: user_id=%d", member_id)
        raise UnauthorizedException("Refresh Token 已使用或不存在")

    # 标记为已使用（乐观锁防并发重放）
    stmt = (
        update(MemberToken)
        .where(MemberToken.id == token_record.id, MemberToken.refresh_token_used == 0)
        .values(refresh_token_used=1)
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        logger.warning("刷新 Token 失败 - 并发重放检测: user_id=%d", member_id)
        raise UnauthorizedException("Refresh Token 已被使用")

    # 查询 member role
    member_result = await db.execute(select(Member.role).where(Member.id == member_id))
    member_role = member_result.scalar_one_or_none() or "landlord"

    logger.info("刷新 Token 成功: user_id=%d", member_id)
    return await _create_token_record(db, member_id, role=member_role)


async def logout(db: AsyncSession, user_id: int) -> None:
    """退出登录：标记所有 Token 为已使用"""
    logger.info("用户登出: user_id=%d", user_id)
    await db.execute(
        update(MemberToken)
        .where(MemberToken.member_id == user_id, MemberToken.refresh_token_used == 0)
        .values(refresh_token_used=1)
    )
