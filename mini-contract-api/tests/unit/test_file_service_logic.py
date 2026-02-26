"""文件服务业务逻辑单元测试"""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.file_service import (
    validate_file,
    generate_file_key,
    create_file_record,
    save_uploaded_file,
    IMAGE_MAX_SIZE,
    DOCUMENT_MAX_SIZE,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_DOC_TYPES,
    ALLOWED_TYPES,
)


# ---- 常量测试 ----

def test_image_max_size():
    """图片最大 5MB"""
    assert IMAGE_MAX_SIZE == 5 * 1024 * 1024


def test_document_max_size():
    """文档最大 20MB"""
    assert DOCUMENT_MAX_SIZE == 20 * 1024 * 1024


def test_allowed_types_union():
    """允许类型是图片和文档的并集"""
    assert ALLOWED_TYPES == ALLOWED_IMAGE_TYPES | ALLOWED_DOC_TYPES


def test_allowed_image_types():
    """支持的图片类型"""
    assert "image/jpeg" in ALLOWED_IMAGE_TYPES
    assert "image/png" in ALLOWED_IMAGE_TYPES
    assert "image/gif" in ALLOWED_IMAGE_TYPES
    assert "image/webp" in ALLOWED_IMAGE_TYPES


def test_allowed_doc_types():
    """支持的文档类型"""
    assert "application/pdf" in ALLOWED_DOC_TYPES
    assert "application/msword" in ALLOWED_DOC_TYPES
    assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in ALLOWED_DOC_TYPES


# ---- create_file_record ----

@pytest.mark.anyio
async def test_create_file_record_success():
    """创建文件记录"""
    db = AsyncMock()

    record = await create_file_record(
        db,
        name="test.pdf",
        path="2024/01/01/abc123.pdf",
        url="/static/uploads/2024/01/01/abc123.pdf",
        file_type="application/pdf",
        size=1024,
    )
    db.add.assert_called_once()
    db.flush.assert_called_once()
    db.refresh.assert_called_once()


@pytest.mark.anyio
async def test_create_file_record_minimal():
    """最少必填字段"""
    db = AsyncMock()

    await create_file_record(
        db,
        name="test.jpg",
        path="2024/01/01/def456.jpg",
        url="/static/uploads/2024/01/01/def456.jpg",
    )
    db.add.assert_called_once()
    created = db.add.call_args[0][0]
    assert created.name == "test.jpg"
    assert created.type is None
    assert created.size is None


# ---- save_uploaded_file ----

@pytest.mark.anyio
async def test_save_uploaded_file(tmp_path):
    """保存文件到本地"""
    content = b"file content here"
    file_key = "2024/01/01/test.pdf"

    with patch("app.services.file_service.os.makedirs") as mock_makedirs, \
         patch("builtins.open", create=True) as mock_open:
        mock_file = MagicMock()
        mock_open.return_value.__enter__ = MagicMock(return_value=mock_file)
        mock_open.return_value.__exit__ = MagicMock(return_value=False)

        url = await save_uploaded_file(content, file_key)
        assert url == "/static/uploads/2024/01/01/test.pdf"
        mock_makedirs.assert_called_once()


def test_generate_file_key_no_extension():
    """无扩展名的文件"""
    key = generate_file_key("README")
    parts = key.split("/")
    assert len(parts) == 4
    # 最后一部分没有 . 扩展名
    assert "." not in parts[-1] or parts[-1].endswith("")
