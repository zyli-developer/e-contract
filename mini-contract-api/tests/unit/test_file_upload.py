"""文件上传测试"""
import pytest

from app.services.file_service import validate_file, generate_file_key
from app.core.exceptions import ValidationException


def test_validate_image_within_limit():
    """5MB 以内的图片应通过校验"""
    validate_file("test.jpg", "image/jpeg", 1024 * 1024)  # 1MB


def test_validate_image_exceeds_limit():
    """超过 5MB 的图片应被拒绝"""
    with pytest.raises(ValidationException, match="5MB"):
        validate_file("test.jpg", "image/jpeg", 6 * 1024 * 1024)


def test_validate_document_within_limit():
    """20MB 以内的文档应通过校验"""
    validate_file("test.pdf", "application/pdf", 10 * 1024 * 1024)  # 10MB


def test_validate_document_exceeds_limit():
    """超过 20MB 的文档应被拒绝"""
    with pytest.raises(ValidationException, match="20MB"):
        validate_file("test.pdf", "application/pdf", 21 * 1024 * 1024)


def test_validate_unsupported_type():
    """不支持的文件类型应被拒绝"""
    with pytest.raises(ValidationException, match="不支持"):
        validate_file("test.exe", "application/x-executable", 1024)


def test_validate_all_allowed_image_types():
    """所有允许的图片类型都应通过"""
    for mime in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
        validate_file("test.img", mime, 1024)


def test_validate_all_allowed_doc_types():
    """所有允许的文档类型都应通过"""
    for mime in ["application/pdf", "application/msword",
                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        validate_file("test.doc", mime, 1024)


def test_generate_file_key_unique():
    """生成的文件路径应唯一"""
    key1 = generate_file_key("test.jpg")
    key2 = generate_file_key("test.jpg")
    assert key1 != key2


def test_generate_file_key_preserves_extension():
    """文件路径应保留原始扩展名"""
    key = generate_file_key("report.pdf")
    assert key.endswith(".pdf")

    key = generate_file_key("photo.png")
    assert key.endswith(".png")


def test_generate_file_key_has_date_prefix():
    """文件路径应包含日期前缀"""
    key = generate_file_key("test.jpg")
    parts = key.split("/")
    # 格式: YYYY/MM/DD/uuid.ext
    assert len(parts) == 4
    assert len(parts[0]) == 4  # year
    assert len(parts[1]) == 2  # month
    assert len(parts[2]) == 2  # day
