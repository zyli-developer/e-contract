"""用户信息管理服务"""
import logging
import os
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException, ErrorCode, ValidationException
from app.core.security import hash_password
from app.models.member import Member
from app.schemas.member import UserInfoResponse
from app.services.ocr_service import (
    extract_id_card_info,
    extract_id_card_validity,
    check_id_card_expired,
)

logger = logging.getLogger(__name__)

# 身份证号校验码权重
_ID_WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
_ID_CHECK_CODES = "10X98765432"


def validate_id_card(id_card: str) -> bool:
    """校验 18 位身份证号格式及校验码"""
    if not re.match(r"^\d{17}[\dXx]$", id_card):
        return False
    total = sum(int(id_card[i]) * _ID_WEIGHTS[i] for i in range(17))
    expected = _ID_CHECK_CODES[total % 11]
    return id_card[-1].upper() == expected


def mask_real_name(name: str) -> str:
    """姓名脱敏：保留首尾字符，中间用 * 替换"""
    if len(name) <= 1:
        return name
    if len(name) == 2:
        return name[0] + "*"
    return name[0] + "*" * (len(name) - 2) + name[-1]


def mask_id_card(id_card: str) -> str:
    """身份证号脱敏：保留前 3 位和后 4 位"""
    if len(id_card) <= 7:
        return id_card
    return id_card[:3] + "*" * (len(id_card) - 7) + id_card[-4:]


async def get_user_info(db: AsyncSession, user_id: int) -> UserInfoResponse:
    """获取当前用户信息"""
    result = await db.execute(select(Member).where(Member.id == user_id))
    member = result.scalar_one_or_none()

    if not member:
        raise BusinessException(code=ErrorCode.USER_NOT_FOUND, msg="用户不存在")

    # 脱敏处理已认证用户的真实姓名
    masked_name = None
    if member.real_name_verified == 1 and member.real_name:
        masked_name = mask_real_name(member.real_name)

    return UserInfoResponse(
        id=member.id,
        mobile=member.mobile or "",
        nickname=member.nickname,
        avatar=member.avatar,
        real_name_verified=member.real_name_verified or 0,
        real_name=masked_name,
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
        real_name_verified=member.real_name_verified or 0,
        real_name=mask_real_name(member.real_name) if member.real_name_verified == 1 and member.real_name else None,
    )


async def update_password(
    db: AsyncSession,
    user_id: int,
    new_password: str,
    confirm_password: str,
) -> None:
    """修改密码（通过确认密码验证）"""
    result = await db.execute(select(Member).where(Member.id == user_id))
    member = result.scalar_one_or_none()

    if not member:
        raise BusinessException(code=ErrorCode.USER_NOT_FOUND, msg="用户不存在")

    if len(new_password) < 6:
        raise ValidationException("密码长度不能少于 6 位")

    if new_password != confirm_password:
        raise ValidationException("两次密码输入不一致")

    member.password = hash_password(new_password)
    await db.flush()


async def verify_real_name(
    db: AsyncSession,
    user_id: int,
    real_name: str,
    id_card: str,
    id_card_front_url: str,
    id_card_back_url: str,
) -> dict:
    """
    实名认证（身份证照片 OCR 校验）

    流程:
    1. 格式校验（姓名非空、身份证校验码）
    2. 读取正面照片，调用 OCR 提取姓名和身份证号
    3. 比对 OCR 结果与用户输入
    4. 匹配则保存认证信息
    """
    result = await db.execute(select(Member).where(Member.id == user_id))
    member = result.scalar_one_or_none()

    if not member:
        raise BusinessException(code=ErrorCode.USER_NOT_FOUND, msg="用户不存在")

    if member.real_name_verified == 1:
        raise BusinessException(code=400, msg="您已完成实名认证，无需重复认证")

    # 校验姓名
    real_name = real_name.strip()
    if not real_name:
        raise ValidationException("请输入真实姓名")

    # 校验身份证号格式
    id_card = id_card.strip()
    if not validate_id_card(id_card):
        raise ValidationException("身份证号格式不正确")

    # 从本地存储读取正面照片并 OCR 识别
    # URL 格式: /static/uploads/2025/01/01/xxx.jpg → 本地路径: uploads/2025/01/01/xxx.jpg
    front_path = id_card_front_url.replace("/static/uploads/", "uploads/")
    if not os.path.isfile(front_path):
        raise ValidationException("身份证正面照片不存在，请重新上传")

    with open(front_path, "rb") as f:
        image_bytes = f.read()

    ocr_result = extract_id_card_info(image_bytes)
    ocr_name = ocr_result.get("name")
    ocr_id_number = ocr_result.get("id_number")

    if not ocr_name and not ocr_id_number:
        raise ValidationException("无法识别身份证信息，请上传清晰的身份证正面照片")

    # 比对身份证号
    if ocr_id_number and ocr_id_number != id_card.upper():
        raise ValidationException("身份证号与身份证照片不一致")

    # 比对姓名（去空格后比较）
    if ocr_name and ocr_name.replace(" ", "") != real_name.replace(" ", ""):
        raise ValidationException("姓名与身份证照片不一致")

    # 读取背面照片，校验有效期
    back_path = id_card_back_url.replace("/static/uploads/", "uploads/")
    if not os.path.isfile(back_path):
        raise ValidationException("身份证背面照片不存在，请重新上传")

    with open(back_path, "rb") as f:
        back_bytes = f.read()

    validity = extract_id_card_validity(back_bytes)
    if check_id_card_expired(validity):
        raise ValidationException("身份证已过期，请使用有效期内的身份证")

    member.real_name = real_name
    member.id_card = id_card
    member.real_name_verified = 1
    await db.flush()

    return {
        "real_name_verified": 1,
        "real_name": mask_real_name(real_name),
        "id_card": mask_id_card(id_card),
    }
