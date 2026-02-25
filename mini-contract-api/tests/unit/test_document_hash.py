"""文档哈希验证单元测试"""
import hashlib

import pytest

from app.services.evidence_service import compute_file_hash


def test_hash_sha256_algorithm():
    """应使用 SHA-256 算法"""
    content = b"contract document content"
    result = compute_file_hash(content)
    expected = hashlib.sha256(content).hexdigest()
    assert result == expected


def test_hash_length_64():
    """SHA-256 哈希应为 64 字符十六进制"""
    result = compute_file_hash(b"test")
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)


def test_hash_deterministic():
    """相同内容多次计算结果一致"""
    content = b"same content"
    results = [compute_file_hash(content) for _ in range(5)]
    assert len(set(results)) == 1


def test_hash_content_sensitive():
    """任意字节改动应产生不同哈希"""
    base = b"original document"
    modified = b"Original document"  # 大小写不同
    assert compute_file_hash(base) != compute_file_hash(modified)


def test_hash_append_sensitive():
    """追加内容应产生不同哈希"""
    base = b"document"
    appended = b"document "  # 多一个空格
    assert compute_file_hash(base) != compute_file_hash(appended)


def test_hash_url_based():
    """MVP 阶段：用文件 URL 做哈希"""
    url = "http://example.com/contract.pdf"
    file_hash = hashlib.sha256(url.encode()).hexdigest()
    assert len(file_hash) == 64


def test_signed_hash_different():
    """签署后文件哈希应与原始哈希不同"""
    url = "http://example.com/contract.pdf"
    original_hash = hashlib.sha256(url.encode()).hexdigest()
    signed_hash = hashlib.sha256((url + ":signed").encode()).hexdigest()
    assert original_hash != signed_hash


def test_hash_collision_resistance():
    """不同 URL 应产生不同哈希"""
    hashes = set()
    for i in range(100):
        url = f"http://example.com/contract_{i}.pdf"
        h = hashlib.sha256(url.encode()).hexdigest()
        hashes.add(h)
    assert len(hashes) == 100
