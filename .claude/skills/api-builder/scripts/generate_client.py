#!/usr/bin/env python3
"""
生成 Next.js TypeScript API Client

从解析后的 OpenAPI 数据生成 TypeScript 客户端代码。
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader


def map_openapi_type_to_typescript(openapi_type: str, format: Optional[str] = None, items: Optional[Dict] = None) -> str:
    """
    映射 OpenAPI 类型到 TypeScript 类型

    Args:
        openapi_type: OpenAPI 类型（string, integer, boolean等）
        format: 格式（email, date-time等）
        items: 数组元素类型（仅当openapi_type为array时）

    Returns:
        TypeScript 类型字符串
    """
    if openapi_type == "string":
        # 所有string格式在TypeScript中都是string
        return "string"
    elif openapi_type == "integer" or openapi_type == "number":
        return "number"
    elif openapi_type == "boolean":
        return "boolean"
    elif openapi_type == "array":
        if items and items.get("type"):
            item_type = map_openapi_type_to_typescript(
                items.get("type"),
                items.get("format"),
                items.get("items")
            )
            return f"Array<{item_type}>"
        return "Array<any>"
    elif openapi_type == "object":
        return "Record<string, any>"
    else:
        # 未知类型，使用any
        return "any"


def extract_typescript_interfaces(schemas: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    从schemas提取TypeScript接口定义

    Args:
        schemas: 解析后的schemas字典

    Returns:
        接口定义列表
    """
    interfaces = []

    for schema_name, schema in schemas.items():
        fields = []

        for prop in schema.get("properties", []):
            prop_name = prop["name"]
            prop_type = prop["type"]
            prop_format = prop.get("format")
            prop_items = prop.get("items")
            prop_nullable = prop.get("nullable", False)
            is_required = prop_name in schema.get("required", [])

            # 映射类型
            ts_type = map_openapi_type_to_typescript(prop_type, prop_format, prop_items)

            # 处理nullable
            if prop_nullable:
                ts_type = f"{ts_type} | null"

            fields.append({
                "name": prop_name,
                "type": ts_type,
                "optional": not is_required,
                "description": prop.get("description", "")
            })

        interfaces.append({
            "name": schema_name,
            "fields": fields,
            "description": schema.get("description", "")
        })

    return interfaces


def extract_typescript_enums(schemas: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    从schemas提取TypeScript枚举定义

    Args:
        schemas: 解析后的schemas字典

    Returns:
        枚举定义列表
    """
    enums = []

    for schema_name, schema in schemas.items():
        for enum_def in schema.get("enums", []):
            enum_values = []
            for value in enum_def.get("values", []):
                # 将枚举值转换为合法的TypeScript标识符
                name = value.upper().replace("-", "_").replace(" ", "_")
                enum_values.append({
                    "name": name,
                    "value": value
                })

            enums.append({
                "name": enum_def["name"],
                "values": enum_values
            })

    return enums


def extract_endpoints(paths: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    从paths提取API端点定义

    Args:
        paths: 解析后的paths字典

    Returns:
        端点定义列表
    """
    endpoints = []

    for resource, operations in paths.items():
        for operation in operations:
            method = operation["method"]
            path = operation["path"]
            operation_id = operation.get("operationId", f"{method}_{path.replace('/', '_')}")

            # 生成函数名（camelCase）
            function_name = operation_id.replace("__", "_").replace("-", "_")

            # 提取路径参数
            path_params = []
            for param in operation.get("parameters", {}).get("path", []):
                param_type = map_openapi_type_to_typescript(param["type"])
                path_params.append({
                    "name": param["name"],
                    "type": param_type,
                    "optional": not param.get("required", True)
                })

            # 提取查询参数
            query_params = []
            for param in operation.get("parameters", {}).get("query", []):
                param_type = map_openapi_type_to_typescript(param["type"])
                query_params.append({
                    "name": param["name"],
                    "type": param_type,
                    "optional": not param.get("required", False)
                })

            # 提取请求体
            body = None
            request_body = operation.get("requestBody")
            if request_body:
                schema_name = request_body.get("schema_name")
                if schema_name:
                    body = {
                        "type": schema_name,
                        "required": request_body.get("required", True)
                    }

            # 提取响应类型
            return_type = "void"
            responses = operation.get("responses", {})
            # 优先使用2xx响应
            for status_code in ["200", "201", "204"]:
                if status_code in responses:
                    schema_name = responses[status_code].get("schema_name")
                    if schema_name:
                        return_type = schema_name
                    elif status_code == "200" or status_code == "201":
                        # 检查是否是数组响应
                        if "array" in responses[status_code].get("schema", "").lower():
                            # 尝试从描述中推断数组类型
                            return_type = "any[]"
                    break

            endpoints.append({
                "function_name": function_name,
                "method": method,
                "path": path,
                "description": operation.get("summary", ""),
                "path_params": path_params,
                "query_params": query_params,
                "body": body,
                "return_type": return_type,
                "params": path_params  # 用于模板
            })

    return endpoints


def generate_client(parsed_data_file: str, output_file: str, templates_dir: str):
    """
    生成TypeScript API客户端

    Args:
        parsed_data_file: 解析后的JSON数据文件路径
        output_file: 输出的TypeScript文件路径
        templates_dir: Jinja2模板目录路径
    """
    # 读取解析后的数据
    parsed_data_path = Path(parsed_data_file)
    if not parsed_data_path.exists():
        print(f"❌ Error: Parsed data file not found: {parsed_data_file}")
        sys.exit(1)

    with open(parsed_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取数据
    schemas = data.get("schemas", {})
    paths = data.get("paths", {})
    api_name = data.get("info", {}).get("title", "API")

    # 生成TypeScript定义
    interfaces = extract_typescript_interfaces(schemas)
    enums = extract_typescript_enums(schemas)
    endpoints = extract_endpoints(paths)

    # 加载模板
    templates_path = Path(templates_dir)
    if not templates_path.exists():
        print(f"❌ Error: Templates directory not found: {templates_dir}")
        sys.exit(1)

    env = Environment(loader=FileSystemLoader(str(templates_path)))
    template = env.get_template("client.ts.j2")

    # 渲染模板
    content = template.render(
        api_name=api_name,
        interfaces=interfaces,
        enums=enums,
        endpoints=endpoints
    )

    # 写入文件
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="生成 Next.js TypeScript API Client"
    )
    parser.add_argument(
        "--parsed-data",
        required=True,
        help="解析后的OpenAPI数据文件（JSON格式）"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="输出的TypeScript文件路径"
    )
    parser.add_argument(
        "--templates-dir",
        default=None,
        help="Jinja2模板目录路径"
    )

    args = parser.parse_args()

    # 默认模板目录
    if args.templates_dir is None:
        script_dir = Path(__file__).parent
        args.templates_dir = str(script_dir.parent / "assets" / "templates")

    generate_client(args.parsed_data, args.output, args.templates_dir)

    print(f"\n✅ Client generation complete!")
    print(f"\n📝 Next steps:")
    print(f"  1. Copy {args.output} to your Next.js project")
    print(f"  2. Configure API_URL in frontend/.env.development or .env.local")
    print(f"  3. Import and use: import {{ apiClient }} from './api-client'")


if __name__ == "__main__":
    main()
