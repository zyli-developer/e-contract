"""签署验证单元测试（短信验证码已移除，保留格式和工具函数测试）"""
import pytest


def test_mobile_mask():
    """手机号脱敏格式正确"""
    mobile = "13800138000"
    masked = mobile[:3] + "****" + mobile[-4:]
    assert masked == "138****8000"
    assert len(masked) == 11


def test_evidence_action_no_sms():
    """证据链操作类型不应包含短信验证码相关"""
    from app.services.evidence_service import EvidenceAction
    assert not hasattr(EvidenceAction, "SIGN_CODE_SENT")
    assert not hasattr(EvidenceAction, "SIGN_CODE_VERIFIED")
    # 应包含基本操作
    assert hasattr(EvidenceAction, "CONTRACT_CREATED")
    assert hasattr(EvidenceAction, "CONTRACT_SIGNED")
    assert hasattr(EvidenceAction, "CONTRACT_COMPLETED")


def test_sign_task_service_no_sms_functions():
    """签署服务不应包含短信验证码相关函数"""
    from app.services import sign_task_service
    assert not hasattr(sign_task_service, "send_sign_code")
    assert not hasattr(sign_task_service, "verify_sign_code")
    assert not hasattr(sign_task_service, "SIGN_CODE_SCENE")
    # 应包含核心签署函数
    assert hasattr(sign_task_service, "execute_sign")
    assert hasattr(sign_task_service, "reject_sign")


def test_auth_service_no_sms_functions():
    """认证服务不应包含短信登录相关函数"""
    from app.services import auth_service
    assert not hasattr(auth_service, "login_by_sms")
    # 应包含注册函数
    assert hasattr(auth_service, "register")
    assert hasattr(auth_service, "login_by_password")


def test_auth_schemas_no_sms():
    """认证 Schema 不应包含短信相关"""
    from app.schemas import auth
    assert not hasattr(auth, "SmsLoginRequest")
    assert not hasattr(auth, "SendSmsCodeRequest")
    # 应包含注册请求
    assert hasattr(auth, "RegisterRequest")
    assert hasattr(auth, "UpdatePasswordRequest")


def test_update_password_request_uses_confirm():
    """修改密码请求应使用 confirmPassword 而非 code"""
    from app.schemas.auth import UpdatePasswordRequest
    req = UpdatePasswordRequest(password="test123", confirmPassword="test123")
    assert req.password == "test123"
    assert req.confirmPassword == "test123"
