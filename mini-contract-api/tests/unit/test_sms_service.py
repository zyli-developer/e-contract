"""短信服务单元测试"""
import pytest
from unittest.mock import AsyncMock, patch

from app.core.exceptions import BusinessException
from app.services.sms_service import _generate_code, send_sms_code


def test_generate_code_default_length():
    code = _generate_code()
    assert len(code) == 6
    assert code.isdigit()


def test_generate_code_custom_length():
    code = _generate_code(length=4)
    assert len(code) == 4
    assert code.isdigit()

    code8 = _generate_code(length=8)
    assert len(code8) == 8
    assert code8.isdigit()


def test_generate_code_randomness():
    codes = {_generate_code() for _ in range(20)}
    assert len(codes) > 1


@pytest.mark.anyio
async def test_send_sms_code_success():
    with patch("app.services.sms_service.check_sms_rate_limit", new_callable=AsyncMock, return_value=True), \
         patch("app.services.sms_service.set_sms_code", new_callable=AsyncMock) as mock_set:
        await send_sms_code("13800138000", scene=1)
        mock_set.assert_called_once()
        stored_code = mock_set.call_args[0][2]
        assert len(stored_code) == 6
        assert stored_code.isdigit()


@pytest.mark.anyio
async def test_send_sms_code_rate_limited():
    with patch("app.services.sms_service.check_sms_rate_limit", new_callable=AsyncMock, return_value=False):
        with pytest.raises(BusinessException) as exc_info:
            await send_sms_code("13800138000", scene=1)
        assert exc_info.value.code == 1012002003


@pytest.mark.anyio
async def test_send_sms_code_different_scenes():
    with patch("app.services.sms_service.check_sms_rate_limit", new_callable=AsyncMock, return_value=True), \
         patch("app.services.sms_service.set_sms_code", new_callable=AsyncMock) as mock_set:
        await send_sms_code("13800138000", scene=1)
        await send_sms_code("13800138000", scene=3)
        assert mock_set.call_count == 2
        assert mock_set.call_args_list[0][0][1] == 1
        assert mock_set.call_args_list[1][0][1] == 3
