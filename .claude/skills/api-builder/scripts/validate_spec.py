#!/usr/bin/env python3
"""
OpenAPI Spec Validator

验证 OpenAPI 规范文件的格式、版本和必需字段。

Usage:
    python validate_spec.py <spec-file>
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple


def load_spec(file_path: str) -> Dict[str, Any]:
    """加载 OpenAPI spec 文件"""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Spec file not found: {file_path}")

    content = path.read_text()

    # 尝试解析
    if file_path.endswith(('.yaml', '.yml')):
        return yaml.safe_load(content)
    elif file_path.endswith('.json'):
        return json.loads(content)
    else:
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError:
            return json.loads(content)


def validate_openapi_version(spec: Dict[str, Any]) -> Tuple[bool, str]:
    """验证 OpenAPI 版本"""
    if 'openapi' not in spec:
        return False, "Missing 'openapi' field"

    version = spec['openapi']

    # 支持 OpenAPI 3.0.x 和 3.1.x
    if not version.startswith('3.'):
        return False, f"Unsupported OpenAPI version: {version} (only 3.x supported)"

    return True, f"OpenAPI version: {version}"


def validate_info(spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """验证 info 字段"""
    errors = []

    if 'info' not in spec:
        return False, ["Missing 'info' field"]

    info = spec['info']

    # 必需字段
    if 'title' not in info:
        errors.append("Missing 'info.title'")

    if 'version' not in info:
        errors.append("Missing 'info.version'")

    if errors:
        return False, errors

    return True, [f"Title: {info.get('title')}", f"Version: {info.get('version')}"]


def validate_paths(spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """验证 paths 字段"""
    if 'paths' not in spec:
        return False, ["Missing 'paths' field"]

    paths = spec['paths']

    if not paths:
        return False, ["'paths' is empty"]

    messages = [f"Found {len(paths)} path(s)"]

    # 统计 endpoints
    total_endpoints = 0
    for path, methods in paths.items():
        for method in methods:
            if method in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                total_endpoints += 1

    messages.append(f"Total endpoints: {total_endpoints}")

    return True, messages


def validate_schemas(spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """验证 schemas 定义（可选但推荐）"""
    components = spec.get('components', {})
    schemas = components.get('schemas', {})

    if not schemas:
        return True, ["Warning: No schemas defined in components.schemas"]

    messages = [f"Found {len(schemas)} schema(s)"]

    # 检查每个 schema
    for schema_name, schema_def in schemas.items():
        if 'type' not in schema_def and '$ref' not in schema_def:
            messages.append(f"Warning: Schema '{schema_name}' missing 'type' field")

    return True, messages


def validate_syntax(spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """验证基本语法结构"""
    errors = []

    # 检查 spec 是否为字典
    if not isinstance(spec, dict):
        return False, ["Spec must be an object/dictionary"]

    return True, ["Syntax valid"]


def validate_spec(spec_file: str) -> bool:
    """完整验证 OpenAPI spec"""
    print(f"🔍 Validating OpenAPI spec: {spec_file}\n")

    try:
        spec = load_spec(spec_file)
    except Exception as e:
        print(f"❌ Failed to load spec: {e}")
        return False

    all_valid = True

    # 1. 验证语法
    valid, messages = validate_syntax(spec)
    print("1️⃣ Syntax Check")
    for msg in messages:
        print(f"   {'✅' if valid else '❌'} {msg}")
    if not valid:
        all_valid = False

    # 2. 验证版本
    valid, message = validate_openapi_version(spec)
    print("\n2️⃣ OpenAPI Version")
    print(f"   {'✅' if valid else '❌'} {message}")
    if not valid:
        all_valid = False

    # 3. 验证 info
    valid, messages = validate_info(spec)
    print("\n3️⃣ Info Field")
    for msg in messages:
        print(f"   {'✅' if valid else '❌'} {msg}")
    if not valid:
        all_valid = False

    # 4. 验证 paths
    valid, messages = validate_paths(spec)
    print("\n4️⃣ Paths")
    for msg in messages:
        print(f"   {'✅' if valid else '❌'} {msg}")
    if not valid:
        all_valid = False

    # 5. 验证 schemas（警告级别）
    valid, messages = validate_schemas(spec)
    print("\n5️⃣ Schemas")
    for msg in messages:
        symbol = '⚠️ ' if 'Warning' in msg else '✅'
        print(f"   {symbol} {msg}")

    # 总结
    print("\n" + "=" * 50)
    if all_valid:
        print("✅ Validation PASSED")
        return True
    else:
        print("❌ Validation FAILED")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_spec.py <spec-file>")
        sys.exit(1)

    spec_file = sys.argv[1]

    try:
        is_valid = validate_spec(spec_file)
        sys.exit(0 if is_valid else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
