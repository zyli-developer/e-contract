"""合同签署任务服务业务逻辑单元测试（使用 mock DB）"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.exceptions import BusinessException, ForbiddenException, ValidationException
from app.services.sign_task_service import (
    create_sign_task,
    get_statistics,
    get_task_detail,
    cancel_task,
    delete_task,
    get_download_url,
    initiate_signing,
    verify_document_hash,
    validate_permission,
    record_view,
    SIGN_CODE_SCENE,
)
from app.schemas.contract import ParticipantRequest


def _make_task(id=1, name="test_contract", status=1, file_url="https://file.pdf",
               signed_file_url=None, file_hash="abc123", signed_file_hash=None,
               template_id=None, creator_id=1, remark=None, create_time=None,
               complete_time=None):
    task = MagicMock()
    task.id = id
    task.name = name
    task.status = status
    task.file_url = file_url
    task.signed_file_url = signed_file_url
    task.file_hash = file_hash
    task.signed_file_hash = signed_file_hash
    task.template_id = template_id
    task.creator_id = creator_id
    task.remark = remark
    task.create_time = create_time or datetime.now()
    task.complete_time = complete_time
    return task


def _make_participant(id=1, task_id=1, name="signer", mobile="13900139000",
                      status=0, order_num=1, member_id=None, seal_id=None):
    p = MagicMock()
    p.id = id
    p.task_id = task_id
    p.name = name
    p.mobile = mobile
    p.status = status
    p.order_num = order_num
    p.member_id = member_id
    p.seal_id = seal_id
    p.sign_time = None
    return p


def _make_db(scalar_return=None):
    db = AsyncMock()
    db.add = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_return
    db.execute.return_value = result
    return db


# ---- create_sign_task ----

@pytest.mark.anyio
async def test_create_task_success():
    """创建合同任务"""
    db = AsyncMock()
    db.add = MagicMock()
    async def _mock_refresh(obj):
        obj.id = obj.id if obj.id else 1
        if not hasattr(obj, 'create_time') or obj.create_time is None:
            obj.create_time = datetime.now()
        # Ensure SignTaskParticipant fields have defaults
        if hasattr(obj, 'task_id'):
            if obj.status is None:
                obj.status = 0
            if obj.order_num is None:
                obj.order_num = 1
        # Ensure SignTask fields
        if hasattr(obj, 'creator_id'):
            if not hasattr(obj, 'complete_time') or obj.complete_time is None:
                obj.complete_time = None
    db.refresh = _mock_refresh

    participants = [ParticipantRequest(name="Zhang", mobile="13900139000")]

    with patch("app.services.sign_task_service.log_evidence", new_callable=AsyncMock):
        result = await create_sign_task(
            db, creator_id=1, name="contract", file_url="https://file.pdf",
            participants=participants,
        )
    assert db.add.call_count >= 1


@pytest.mark.anyio
async def test_create_task_no_name():
    db = AsyncMock()
    with pytest.raises(ValidationException) as exc_info:
        await create_sign_task(db, creator_id=1, name="")
    assert "名称" in exc_info.value.msg


@pytest.mark.anyio
async def test_create_task_no_template_no_file():
    db = AsyncMock()
    with pytest.raises(ValidationException) as exc_info:
        await create_sign_task(db, creator_id=1, name="contract")
    assert "模板" in exc_info.value.msg or "文件" in exc_info.value.msg


@pytest.mark.anyio
async def test_create_task_with_template():
    db = AsyncMock()
    db.add = MagicMock()
    async def _mock_refresh(obj):
        obj.id = 1
        if hasattr(obj, 'create_time'):
            obj.create_time = datetime.now()
        if hasattr(obj, 'complete_time'):
            obj.complete_time = None
    db.refresh = _mock_refresh

    with patch("app.services.sign_task_service.log_evidence", new_callable=AsyncMock), \
         patch("app.services.template_service.increment_use_count", new_callable=AsyncMock) as mock_inc:
        await create_sign_task(db, creator_id=1, name="contract", template_id=10)
        mock_inc.assert_called_once_with(db, 10)


@pytest.mark.anyio
async def test_create_task_file_hash():
    db = AsyncMock()
    db.add = MagicMock()
    async def _mock_refresh(obj):
        obj.id = 1
        if hasattr(obj, 'create_time'):
            obj.create_time = datetime.now()
        if hasattr(obj, 'complete_time'):
            obj.complete_time = None
    db.refresh = _mock_refresh

    with patch("app.services.sign_task_service.log_evidence", new_callable=AsyncMock):
        await create_sign_task(db, creator_id=1, name="contract", file_url="https://test.pdf")
    added_task = db.add.call_args_list[0][0][0]
    assert added_task.file_hash is not None
    assert len(added_task.file_hash) == 64


# ---- get_statistics ----

@pytest.mark.anyio
async def test_get_statistics():
    db = AsyncMock()
    results = []
    for val in [10, 3, 5, 2]:
        r = MagicMock()
        r.scalar.return_value = val
        results.append(r)
    db.execute.side_effect = results

    stats = await get_statistics(db, creator_id=1)
    assert stats["totalCount"] == 10
    assert stats["draftCount"] == 3
    assert stats["signingCount"] == 5
    assert stats["completedCount"] == 2


# ---- cancel_task ----

@pytest.mark.anyio
async def test_cancel_draft_task():
    task = _make_task(status=1)
    db = _make_db(scalar_return=task)
    with patch("app.services.sign_task_service.log_evidence", new_callable=AsyncMock):
        await cancel_task(db, task_id=1, user_id=1)
    assert task.status == 4


@pytest.mark.anyio
async def test_cancel_signing_task():
    task = _make_task(status=2)
    db = _make_db(scalar_return=task)
    with patch("app.services.sign_task_service.log_evidence", new_callable=AsyncMock):
        await cancel_task(db, task_id=1, user_id=1)
    assert task.status == 4


@pytest.mark.anyio
async def test_cancel_completed_task_fails():
    task = _make_task(status=3)
    db = _make_db(scalar_return=task)
    with pytest.raises(BusinessException) as exc_info:
        await cancel_task(db, task_id=1, user_id=1)
    assert exc_info.value.code == 400


@pytest.mark.anyio
async def test_cancel_nonexistent_task():
    db = _make_db(scalar_return=None)
    with pytest.raises(BusinessException) as exc_info:
        await cancel_task(db, task_id=999, user_id=1)
    assert exc_info.value.code == 404


# ---- delete_task ----

@pytest.mark.anyio
async def test_delete_draft_task():
    task = _make_task(status=1)
    participant = _make_participant()

    db = AsyncMock()
    db.add = MagicMock()
    task_result = MagicMock()
    task_result.scalar_one_or_none.return_value = task
    p_result = MagicMock()
    p_scalars = MagicMock()
    p_scalars.all.return_value = [participant]
    p_result.scalars.return_value = p_scalars
    db.execute.side_effect = [task_result, p_result]

    await delete_task(db, task_id=1, user_id=1)
    db.delete.assert_called()


@pytest.mark.anyio
async def test_delete_cancelled_task():
    task = _make_task(status=4)
    db = AsyncMock()
    db.add = MagicMock()
    task_result = MagicMock()
    task_result.scalar_one_or_none.return_value = task
    p_result = MagicMock()
    p_scalars = MagicMock()
    p_scalars.all.return_value = []
    p_result.scalars.return_value = p_scalars
    db.execute.side_effect = [task_result, p_result]

    await delete_task(db, task_id=1, user_id=1)
    db.delete.assert_called_once()


@pytest.mark.anyio
async def test_delete_signing_task_fails():
    task = _make_task(status=2)
    db = _make_db(scalar_return=task)
    with pytest.raises(BusinessException) as exc_info:
        await delete_task(db, task_id=1, user_id=1)
    assert exc_info.value.code == 400


# ---- get_download_url ----

@pytest.mark.anyio
async def test_download_completed_task():
    task = _make_task(status=3, signed_file_url="https://signed.pdf")
    db = AsyncMock()
    db.add = MagicMock()
    task_result = MagicMock()
    task_result.scalar_one_or_none.return_value = task
    p_result = MagicMock()
    p_result.scalar_one_or_none.return_value = _make_participant(member_id=1)
    db.execute.side_effect = [task_result, p_result]

    result = await get_download_url(db, task_id=1, user_id=1)
    assert result["signed_file_url"] == "https://signed.pdf"


@pytest.mark.anyio
async def test_download_incomplete_task_fails():
    task = _make_task(status=2)
    db = AsyncMock()
    task_result = MagicMock()
    task_result.scalar_one_or_none.return_value = task
    db.execute.return_value = task_result

    with pytest.raises(BusinessException) as exc_info:
        await get_download_url(db, task_id=1, user_id=1)
    assert exc_info.value.code == 400


# ---- initiate_signing ----

@pytest.mark.anyio
async def test_initiate_signing_success():
    task = _make_task(status=1)
    db = AsyncMock()
    db.add = MagicMock()
    task_result = MagicMock()
    task_result.scalar_one_or_none.return_value = task
    count_result = MagicMock()
    count_result.scalar.return_value = 2
    p_result = MagicMock()
    p_scalars = MagicMock()
    p1 = _make_participant(mobile="13900001111")
    p_scalars.all.return_value = [p1]
    p_result.scalars.return_value = p_scalars
    db.execute.side_effect = [task_result, count_result, p_result]

    with patch("app.services.sign_task_service.log_evidence", new_callable=AsyncMock):
        await initiate_signing(db, task_id=1, user_id=1)
    assert task.status == 2


@pytest.mark.anyio
async def test_initiate_non_draft_fails():
    task = _make_task(status=2)
    db = _make_db(scalar_return=task)
    with pytest.raises(BusinessException) as exc_info:
        await initiate_signing(db, task_id=1, user_id=1)
    assert exc_info.value.code == 400


@pytest.mark.anyio
async def test_initiate_no_participants_fails():
    task = _make_task(status=1)
    db = AsyncMock()
    db.add = MagicMock()
    task_result = MagicMock()
    task_result.scalar_one_or_none.return_value = task
    count_result = MagicMock()
    count_result.scalar.return_value = 0
    db.execute.side_effect = [task_result, count_result]

    with pytest.raises(ValidationException) as exc_info:
        await initiate_signing(db, task_id=1, user_id=1)
    assert "签署方" in exc_info.value.msg


# ---- verify_document_hash ----

@pytest.mark.anyio
async def test_verify_hash_with_file():
    task = _make_task(status=3, file_hash="abc", signed_file_hash="def")
    db = AsyncMock()
    task_result = MagicMock()
    task_result.scalar_one_or_none.return_value = task
    db.execute.return_value = task_result

    result = await verify_document_hash(db, task_id=1)
    assert result["file_hash"] == "abc"
    assert result["signed_file_hash"] == "def"
    assert result["is_original_valid"] is True
    assert result["is_signed_valid"] is True


@pytest.mark.anyio
async def test_verify_hash_no_file():
    task = _make_task(status=1, file_hash=None, signed_file_hash=None)
    db = AsyncMock()
    task_result = MagicMock()
    task_result.scalar_one_or_none.return_value = task
    db.execute.return_value = task_result

    result = await verify_document_hash(db, task_id=1)
    assert result["is_original_valid"] is False


# ---- validate_permission ----

@pytest.mark.anyio
async def test_validate_permission_creator():
    task = _make_task(creator_id=1)
    db = AsyncMock()
    task_result = MagicMock()
    task_result.scalar_one_or_none.return_value = task
    p_result = MagicMock()
    p_result.scalar_one_or_none.return_value = None
    member_result = MagicMock()
    member_result.scalar_one_or_none.return_value = None
    db.execute.side_effect = [task_result, p_result, member_result]

    result = await validate_permission(db, task_id=1, user_id=1)
    assert result["is_creator"] is True


@pytest.mark.anyio
async def test_validate_permission_participant():
    task = _make_task(creator_id=99)
    participant = _make_participant(member_id=2, status=0)
    db = AsyncMock()
    task_result = MagicMock()
    task_result.scalar_one_or_none.return_value = task
    p_result = MagicMock()
    p_result.scalar_one_or_none.return_value = participant
    db.execute.side_effect = [task_result, p_result]

    result = await validate_permission(db, task_id=1, user_id=2)
    assert result["is_creator"] is False
    assert result["is_participant"] is True


# ---- record_view ----

@pytest.mark.anyio
async def test_record_view():
    db = AsyncMock()
    with patch("app.services.sign_task_service.log_evidence", new_callable=AsyncMock) as mock_log:
        await record_view(db, task_id=1, user_id=2, ip="10.0.0.1")
        mock_log.assert_called_once()


# ---- SIGN_CODE_SCENE ----

def test_sign_code_scene_value():
    assert SIGN_CODE_SCENE == 10
    assert SIGN_CODE_SCENE not in (1, 2, 3)
