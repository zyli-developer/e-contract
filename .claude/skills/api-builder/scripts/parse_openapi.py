#!/usr/bin/env python3
"""
OpenAPI Spec Parser

解析 OpenAPI 3.x 规范文件，提取 schemas 和 paths 信息。
输出结构化的 JSON 数据供代码生成器使用。

Usage:
    python parse_openapi.py <spec-file> [--output parsed.json]
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


def load_spec(file_path: str) -> Dict[str, Any]:
    """加载 OpenAPI spec 文件（支持 YAML 和 JSON）"""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Spec file not found: {file_path}")

    content = path.read_text()

    # 尝试解析 YAML
    if file_path.endswith(('.yaml', '.yml')):
        return yaml.safe_load(content)

    # 尝试解析 JSON
    elif file_path.endswith('.json'):
        return json.loads(content)

    # 自动检测格式
    else:
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError:
            return json.loads(content)


def extract_schemas(spec: Dict[str, Any]) -> Dict[str, Any]:
    """从 OpenAPI spec 提取 schemas 定义"""
    components = spec.get('components', {})
    schemas = components.get('schemas', {})

    result = {}

    for schema_name, schema_def in schemas.items():
        result[schema_name] = {
            'name': schema_name,
            'type': schema_def.get('type', 'object'),
            'description': schema_def.get('description', ''),
            'properties': extract_properties(schema_def.get('properties', {})),
            'required': schema_def.get('required', []),
            'enums': extract_enums(schema_def)
        }

    return result


def extract_properties(properties: Dict[str, Any]) -> List[Dict[str, Any]]:
    """提取 schema 的 properties"""
    result = []

    for prop_name, prop_def in properties.items():
        prop_info = {
            'name': prop_name,
            'type': prop_def.get('type', 'string'),
            'format': prop_def.get('format'),
            'description': prop_def.get('description', ''),
            'nullable': prop_def.get('nullable', False),
            'default': prop_def.get('default'),
            'enum': prop_def.get('enum'),
            'minLength': prop_def.get('minLength'),
            'maxLength': prop_def.get('maxLength'),
            'minimum': prop_def.get('minimum'),
            'maximum': prop_def.get('maximum'),
            'pattern': prop_def.get('pattern'),
            'items': prop_def.get('items'),  # for arrays
            '$ref': prop_def.get('$ref'),  # for references
        }

        result.append(prop_info)

    return result


def extract_enums(schema_def: Dict[str, Any]) -> List[Dict[str, Any]]:
    """提取 enum 定义"""
    enums = []

    # 检查根级别的 enum
    if 'enum' in schema_def:
        enums.append({
            'name': schema_def.get('x-enum-name', 'Enum'),
            'values': schema_def['enum']
        })

    # 检查 properties 中的 enum
    properties = schema_def.get('properties', {})
    for prop_name, prop_def in properties.items():
        if 'enum' in prop_def:
            enums.append({
                'name': prop_def.get('x-enum-name', f"{prop_name.capitalize()}Enum"),
                'values': prop_def['enum']
            })

    return enums


def extract_paths(spec: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """从 OpenAPI spec 提取 paths（endpoints）"""
    paths = spec.get('paths', {})
    result = {}

    for path, methods in paths.items():
        for method, operation in methods.items():
            if method.startswith('x-'):  # 跳过扩展字段
                continue

            if method not in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                continue

            # 提取资源名（用于分组）
            resource = extract_resource_name(path, operation)

            if resource not in result:
                result[resource] = []

            endpoint_info = {
                'path': path,
                'method': method,
                'operationId': operation.get('operationId', f"{method}_{path.replace('/', '_')}"),
                'summary': operation.get('summary', ''),
                'description': operation.get('description', ''),
                'tags': operation.get('tags', []),
                'parameters': extract_parameters(operation.get('parameters', [])),
                'requestBody': extract_request_body(operation.get('requestBody')),
                'responses': extract_responses(operation.get('responses', {})),
            }

            result[resource].append(endpoint_info)

    return result


def extract_resource_name(path: str, operation: Dict[str, Any]) -> str:
    """从 path 和 operation 推断资源名"""
    # 优先使用 tags
    tags = operation.get('tags', [])
    if tags:
        return tags[0].lower()

    # 从 path 推断（取第一段）
    parts = [p for p in path.split('/') if p and not p.startswith('{')]
    if parts:
        return parts[0].lower()

    return 'default'


def extract_parameters(parameters: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """提取参数（path, query, header）"""
    result = {
        'path': [],
        'query': [],
        'header': [],
    }

    for param in parameters:
        param_in = param.get('in', 'query')
        param_info = {
            'name': param.get('name'),
            'type': param.get('schema', {}).get('type', 'string'),
            'required': param.get('required', False),
            'description': param.get('description', ''),
            'default': param.get('schema', {}).get('default'),
        }

        if param_in in result:
            result[param_in].append(param_info)

    return result


def extract_request_body(request_body: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """提取 request body 信息"""
    if not request_body:
        return None

    content = request_body.get('content', {})
    json_content = content.get('application/json', {})
    schema = json_content.get('schema', {})

    return {
        'required': request_body.get('required', False),
        'description': request_body.get('description', ''),
        'schema': schema.get('$ref', ''),  # Usually a $ref to components/schemas
        'schema_name': schema.get('$ref', '').split('/')[-1] if '$ref' in schema else None,
    }


def extract_responses(responses: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """提取 responses 信息"""
    result = {}

    for status_code, response in responses.items():
        content = response.get('content', {})
        json_content = content.get('application/json', {})
        schema = json_content.get('schema', {})

        result[status_code] = {
            'description': response.get('description', ''),
            'schema': schema.get('$ref', ''),
            'schema_name': schema.get('$ref', '').split('/')[-1] if '$ref' in schema else None,
        }

    return result


def parse_openapi(spec_file: str) -> Dict[str, Any]:
    """解析 OpenAPI spec 文件"""
    spec = load_spec(spec_file)

    # 提取基本信息
    info = spec.get('info', {})

    result = {
        'openapi_version': spec.get('openapi', '3.0.0'),
        'info': {
            'title': info.get('title', 'API'),
            'version': info.get('version', '1.0.0'),
            'description': info.get('description', ''),
        },
        'servers': spec.get('servers', []),
        'schemas': extract_schemas(spec),
        'paths': extract_paths(spec),
    }

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_openapi.py <spec-file> [--output parsed.json]")
        sys.exit(1)

    spec_file = sys.argv[1]
    output_file = None

    # 解析参数
    if '--output' in sys.argv:
        output_idx = sys.argv.index('--output')
        if output_idx + 1 < len(sys.argv):
            output_file = sys.argv[output_idx + 1]

    try:
        parsed = parse_openapi(spec_file)

        # 输出结果
        if output_file:
            Path(output_file).write_text(json.dumps(parsed, indent=2))
            print(f"✅ Parsed OpenAPI spec saved to: {output_file}")
        else:
            print(json.dumps(parsed, indent=2))

        # 统计信息
        print(f"\n📊 Statistics:", file=sys.stderr)
        print(f"  - Schemas: {len(parsed['schemas'])}", file=sys.stderr)
        print(f"  - Resources: {len(parsed['paths'])}", file=sys.stderr)
        total_endpoints = sum(len(endpoints) for endpoints in parsed['paths'].values())
        print(f"  - Total endpoints: {total_endpoints}", file=sys.stderr)

    except Exception as e:
        print(f"❌ Error parsing OpenAPI spec: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
