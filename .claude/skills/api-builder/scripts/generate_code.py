#!/usr/bin/env python3
"""
Code Generator using Jinja2 Templates

使用 Jinja2 模板生成 FastAPI 代码文件。

Usage:
    python generate_code.py --parsed-data parsed.json --output-dir ./app --templates-dir ../assets/templates

Options:
    --conflict-strategy  How to handle existing files: skip | backup | overwrite (default: skip)
    --dry-run           Show what would be generated without writing files
"""

import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Literal, Set
from jinja2 import Environment, FileSystemLoader, Template


ConflictStrategy = Literal['skip', 'backup', 'overwrite']


class FileConflictError(Exception):
    """Raised when file conflicts are detected and strategy is 'error'"""
    pass


def map_openapi_type_to_python(openapi_type: str, format: str = None) -> str:
    """映射 OpenAPI 类型到 Python/Pydantic 类型"""
    type_mapping = {
        'string': 'str',
        'integer': 'int',
        'number': 'float',
        'boolean': 'bool',
        'array': 'List',
        'object': 'Dict[str, Any]',
    }

    if openapi_type == 'string' and format:
        format_mapping = {
            'date': 'date',
            'date-time': 'datetime',
            'email': 'EmailStr',
            'uri': 'AnyUrl',
            'uuid': 'UUID4',
            'password': 'SecretStr',
        }
        return format_mapping.get(format, 'str')

    return type_mapping.get(openapi_type, 'Any')


def map_openapi_type_to_sqlalchemy(openapi_type: str, format: str = None, max_length: int = None) -> str:
    """映射 OpenAPI 类型到 SQLAlchemy 类型"""
    if openapi_type == 'string':
        if format == 'date':
            return 'Date'
        elif format == 'date-time':
            return 'DateTime'
        elif format == 'uuid':
            return 'String(36)'
        elif max_length:
            return f'String({max_length})'
        else:
            return 'String'
    elif openapi_type == 'integer':
        if format == 'int64':
            return 'BigInteger'
        return 'Integer'
    elif openapi_type == 'number':
        if format == 'double':
            return 'Double'
        return 'Float'
    elif openapi_type == 'boolean':
        return 'Boolean'
    elif openapi_type == 'array':
        return 'JSON'  # SQLite doesn't have native array type
    elif openapi_type == 'object':
        return 'JSON'
    else:
        return 'String'


def prepare_model_context(schema_name: str, schema_def: Dict[str, Any]) -> Dict[str, Any]:
    """准备 model 模板的上下文数据"""
    fields = []

    for prop in schema_def.get('properties', []):
        field = {
            'name': prop['name'],
            'type': map_openapi_type_to_sqlalchemy(
                prop['type'],
                prop.get('format'),
                prop.get('maxLength')
            ),
            'nullable': prop['name'] not in schema_def.get('required', []),
            'unique': prop.get('format') == 'email',  # email 字段通常 unique
            'index': prop.get('format') == 'email',   # email 字段需要索引
            'default': prop.get('default'),
        }
        fields.append(field)

    # 提取 enums
    enums = []
    for enum_def in schema_def.get('enums', []):
        enums.append({
            'name': enum_def['name'],
            'values': enum_def['values']
        })

    context = {
        'model_name': schema_name,
        'table_name': schema_name.lower() + 's',  # 简单复数化
        'description': schema_def.get('description', f'{schema_name} model'),
        'fields': fields,
        'enums': enums,
        'has_enum': len(enums) > 0,
        'has_foreign_key': False,  # TODO: 检测外键
        'has_relationship': False,  # TODO: 检测关系
        'has_timestamps': True,  # 默认添加时间戳
        'relationships': [],
    }

    return context


def prepare_schema_context(schema_name: str, schema_def: Dict[str, Any]) -> Dict[str, Any]:
    """准备 schema 模板的上下文数据"""
    base_fields = []
    required_create_fields = []
    update_fields = []

    for prop in schema_def.get('properties', []):
        python_type = map_openapi_type_to_python(prop['type'], prop.get('format'))

        # 检查是否需要特殊导入
        has_email = python_type == 'EmailStr'
        has_url = python_type == 'AnyUrl'
        has_uuid = python_type == 'UUID4'

        is_required = prop['name'] in schema_def.get('required', [])

        field_config = []
        if prop.get('minLength'):
            field_config.append(f"min_length={prop['minLength']}")
        if prop.get('maxLength'):
            field_config.append(f"max_length={prop['maxLength']}")
        if prop.get('minimum') is not None:
            field_config.append(f"ge={prop['minimum']}")
        if prop.get('maximum') is not None:
            field_config.append(f"le={prop['maximum']}")

        field = {
            'name': prop['name'],
            'type': python_type,
            'optional': not is_required,
            'field_config': ', '.join(field_config) if field_config else None,
        }

        base_fields.append(field)

        if is_required:
            required_create_fields.append(field)

        update_fields.append(field)

    # 提取 enums
    enums = []
    for enum_def in schema_def.get('enums', []):
        enums.append({
            'name': enum_def['name'],
            'values': enum_def['values'],
            'description': f'{enum_def["name"]} enum'
        })

    context = {
        'model_name': schema_name,
        'base_fields': base_fields,
        'required_create_fields': required_create_fields,
        'update_fields': update_fields,
        'enums': enums,
        'has_email': any(f['type'] == 'EmailStr' for f in base_fields),
        'has_url': any(f['type'] == 'AnyUrl' for f in base_fields),
        'has_uuid': any(f['type'] == 'UUID4' for f in base_fields),
        'has_field_validator': any(f.get('field_config') for f in base_fields),
        'has_date': any(f['type'] == 'date' for f in base_fields),
        'has_list': any('List' in f['type'] for f in base_fields),
        'has_timestamps': True,
        'has_updated_at': True,
    }

    return context


def prepare_router_context(resource: str, endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
    """准备 router 模板的上下文数据"""
    processed_endpoints = []

    for endpoint in endpoints:
        # 提取路径参数
        path_params = [
            {'name': p['name'], 'type': map_openapi_type_to_python(p['type'])}
            for p in endpoint['parameters']['path']
        ]

        # 提取查询参数
        query_params = [
            {
                'name': p['name'],
                'type': map_openapi_type_to_python(p['type']),
                'default': p.get('default', '0' if p['type'] == 'integer' else '""'),
                'ge': p.get('minimum'),
                'le': p.get('maximum'),
            }
            for p in endpoint['parameters']['query']
        ]

        # 请求体
        request_body = None
        if endpoint.get('requestBody'):
            request_body = {
                'name': f"{resource}_in",
                'type': endpoint['requestBody'].get('schema_name', f"{resource.capitalize()}Create"),
            }

        # 响应模型
        response_200 = endpoint['responses'].get('200', {})
        response_model = response_200.get('schema_name') if response_200 else None

        # 生成函数名
        function_name = endpoint['operationId'].replace('-', '_').replace(' ', '_').lower()

        processed_endpoints.append({
            'method': endpoint['method'],
            'path': endpoint['path'],
            'function_name': function_name,
            'description': endpoint.get('description') or endpoint.get('summary', ''),
            'summary': endpoint.get('summary', ''),
            'path_params': path_params,
            'query_params': query_params,
            'request_body': request_body,
            'response_model': f"schemas.{response_model}" if response_model else None,
            'status_code': 'HTTP_201_CREATED' if endpoint['method'] == 'post' else None,
            'return_type': response_model or 'Any',
            'tags': endpoint.get('tags', []),
        })

    context = {
        'resource_name': resource,
        'endpoints': processed_endpoints,
        'crud_name': resource.lower(),
        'has_query_params': any(e['query_params'] for e in processed_endpoints),
        'has_optional': True,
    }

    return context


def detect_existing_files(output_dir: str, parsed: Dict[str, Any]) -> Dict[str, List[Path]]:
    """
    检测将要生成的文件中哪些已存在。

    Returns:
        Dict with keys 'models', 'schemas', 'routers' containing lists of existing file paths
    """
    output_path = Path(output_dir)
    existing = {
        'models': [],
        'schemas': [],
        'routers': [],
    }

    # 检查 models
    models_dir = output_path / 'models'
    if models_dir.exists():
        for schema_name in parsed['schemas'].keys():
            model_file = models_dir / f"{schema_name.lower()}.py"
            if model_file.exists():
                existing['models'].append(model_file)

    # 检查 schemas
    schemas_dir = output_path / 'schemas'
    if schemas_dir.exists():
        for schema_name in parsed['schemas'].keys():
            schema_file = schemas_dir / f"{schema_name.lower()}.py"
            if schema_file.exists():
                existing['schemas'].append(schema_file)

    # 检查 routers
    routers_dir = output_path / 'routers'
    if routers_dir.exists():
        for resource in parsed['paths'].keys():
            router_file = routers_dir / f"{resource}.py"
            if router_file.exists():
                existing['routers'].append(router_file)

    return existing


def backup_file(file_path: Path) -> Path:
    """
    备份文件，添加时间戳后缀。

    Returns:
        Path to backup file
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = file_path.with_suffix(f'.{timestamp}.bak')
    shutil.copy2(file_path, backup_path)
    return backup_path


def write_file_with_strategy(
    file_path: Path,
    content: str,
    strategy: ConflictStrategy,
    dry_run: bool = False
) -> str:
    """
    根据策略写入文件。

    Returns:
        Status message describing what happened
    """
    if file_path.exists():
        if strategy == 'skip':
            return f"⏭️  Skipped (exists): {file_path}"
        elif strategy == 'backup':
            if not dry_run:
                backup_path = backup_file(file_path)
                file_path.write_text(content)
                return f"✅ Generated (backup: {backup_path.name}): {file_path}"
            else:
                return f"[DRY-RUN] Would backup and overwrite: {file_path}"
        elif strategy == 'overwrite':
            if not dry_run:
                file_path.write_text(content)
                return f"⚠️  Overwritten: {file_path}"
            else:
                return f"[DRY-RUN] Would overwrite: {file_path}"
    else:
        if not dry_run:
            file_path.write_text(content)
            return f"✅ Generated: {file_path}"
        else:
            return f"[DRY-RUN] Would create: {file_path}"


def generate_files(
    parsed_data_file: str,
    output_dir: str,
    templates_dir: str,
    conflict_strategy: ConflictStrategy = 'skip',
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    生成所有代码文件。

    Returns:
        Dict with generation statistics
    """
    # 加载解析后的数据
    parsed = json.loads(Path(parsed_data_file).read_text())

    # 设置 Jinja2 环境
    env = Environment(loader=FileSystemLoader(templates_dir))

    output_path = Path(output_dir)

    stats = {
        'created': 0,
        'skipped': 0,
        'overwritten': 0,
        'backed_up': 0,
        'errors': 0,
    }

    # 检测现有文件
    existing = detect_existing_files(output_dir, parsed)
    total_existing = sum(len(v) for v in existing.values())

    if total_existing > 0:
        print(f"\n⚠️  Detected {total_existing} existing file(s):")
        for event, files in existing.items():
            if files:
                print(f"   {event}: {len(files)} file(s)")
        print(f"   Strategy: {conflict_strategy}\n")

    if not dry_run:
        output_path.mkdir(parents=True, exist_ok=True)

    # 生成 models
    models_dir = output_path / 'models'
    if not dry_run:
        models_dir.mkdir(exist_ok=True)

    for schema_name, schema_def in parsed['schemas'].items():
        context = prepare_model_context(schema_name, schema_def)
        template = env.get_template('model.py.j2')
        content = template.render(**context)

        model_file = models_dir / f"{schema_name.lower()}.py"
        msg = write_file_with_strategy(model_file, content, conflict_strategy, dry_run)
        print(msg)

        if 'Skipped' in msg:
            stats['skipped'] += 1
        elif 'Overwritten' in msg:
            stats['overwritten'] += 1
        elif 'backup' in msg:
            stats['backed_up'] += 1
        else:
            stats['created'] += 1

    # 生成 schemas
    schemas_dir = output_path / 'schemas'
    if not dry_run:
        schemas_dir.mkdir(exist_ok=True)

    for schema_name, schema_def in parsed['schemas'].items():
        context = prepare_schema_context(schema_name, schema_def)
        template = env.get_template('schema.py.j2')
        content = template.render(**context)

        schema_file = schemas_dir / f"{schema_name.lower()}.py"
        msg = write_file_with_strategy(schema_file, content, conflict_strategy, dry_run)
        print(msg)

        if 'Skipped' in msg:
            stats['skipped'] += 1
        elif 'Overwritten' in msg:
            stats['overwritten'] += 1
        elif 'backup' in msg:
            stats['backed_up'] += 1
        else:
            stats['created'] += 1

    # 生成 routers
    routers_dir = output_path / 'routers'
    if not dry_run:
        routers_dir.mkdir(exist_ok=True)

    for resource, endpoints in parsed['paths'].items():
        context = prepare_router_context(resource, endpoints)
        template = env.get_template('router.py.j2')
        content = template.render(**context)

        router_file = routers_dir / f"{resource}.py"
        msg = write_file_with_strategy(router_file, content, conflict_strategy, dry_run)
        print(msg)

        if 'Skipped' in msg:
            stats['skipped'] += 1
        elif 'Overwritten' in msg:
            stats['overwritten'] += 1
        elif 'backup' in msg:
            stats['backed_up'] += 1
        else:
            stats['created'] += 1

    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate FastAPI code from parsed OpenAPI data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Conflict Strategies:
  skip      - Do not overwrite existing files (default, safest)
  backup    - Backup existing files before overwriting
  overwrite - Overwrite existing files without backup (dangerous!)

Examples:
  # Safe generation (skip existing files)
  python generate_code.py --parsed-data parsed.json --output-dir ./app --templates-dir ../assets/templates

  # Preview what would be generated
  python generate_code.py --parsed-data parsed.json --output-dir ./app --templates-dir ../assets/templates --dry-run

  # Overwrite with backup
  python generate_code.py --parsed-data parsed.json --output-dir ./app --templates-dir ../assets/templates --conflict-strategy backup
"""
    )
    parser.add_argument('--parsed-data', required=True, help='Path to parsed OpenAPI JSON file')
    parser.add_argument('--output-dir', required=True, help='Output directory for generated code')
    parser.add_argument('--templates-dir', required=True, help='Directory containing Jinja2 templates')
    parser.add_argument(
        '--conflict-strategy',
        choices=['skip', 'backup', 'overwrite'],
        default='skip',
        help='How to handle existing files (default: skip)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be generated without writing files'
    )

    args = parser.parse_args()

    try:
        if args.dry_run:
            print("🔍 DRY RUN MODE - No files will be written\n")

        stats = generate_files(
            args.parsed_data,
            args.output_dir,
            args.templates_dir,
            conflict_strategy=args.conflict_strategy,
            dry_run=args.dry_run
        )

        print(f"\n📊 Generation Statistics:")
        print(f"   Created:    {stats['created']}")
        print(f"   Skipped:    {stats['skipped']}")
        print(f"   Backed up:  {stats['backed_up']}")
        print(f"   Overwritten:{stats['overwritten']}")

        if stats['skipped'] > 0:
            print(f"\n💡 Tip: Use --conflict-strategy=backup to update existing files safely")

        print("\n✅ Code generation complete!")
    except Exception as e:
        print(f"\n❌ Error generating code: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
