#!/usr/bin/env python3
"""
API Builder CLI

完整的 API 生成流程编排工具。

Usage:
    python cli.py --spec petstore.yaml --output ./generated

Options:
    --spec FILE          OpenAPI specification file (required)
    --output DIR         Output directory (default: ./generated)
    --templates DIR      Templates directory (default: ../assets/templates)
    --skip-validation    Skip spec validation
    --resources LIST     Comma-separated list of resources to generate (default: all)
"""

import sys
import argparse
import subprocess
import json
from pathlib import Path
from typing import List, Optional


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}\n")


def print_step(step_num: int, text: str):
    """打印步骤"""
    print(f"{Colors.BOLD}{Colors.CYAN}[Step {step_num}]{Colors.END} {text}")


def print_success(text: str):
    """打印成功消息"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str):
    """打印错误消息"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text: str):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def run_command(cmd: List[str], description: str) -> bool:
    """运行命令并捕获输出"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed")
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        return False
    except Exception as e:
        print_error(f"{description} failed: {e}")
        return False


def validate_spec(spec_file: str, skip_validation: bool) -> bool:
    """验证 OpenAPI spec"""
    if skip_validation:
        print_warning("Skipping validation (--skip-validation)")
        return True

    print_step(1, "Validating OpenAPI specification")

    script_dir = Path(__file__).parent
    validate_script = script_dir / "validate_spec.py"

    return run_command(
        [sys.executable, str(validate_script), spec_file],
        "Validation"
    )


def parse_spec(spec_file: str, output_file: str) -> bool:
    """解析 OpenAPI spec"""
    print_step(2, "Parsing OpenAPI specification")

    script_dir = Path(__file__).parent
    parse_script = script_dir / "parse_openapi.py"

    return run_command(
        [sys.executable, str(parse_script), spec_file, "--output", output_file],
        "Parsing"
    )


def filter_resources(parsed_file: str, resources: Optional[List[str]]) -> bool:
    """过滤指定的资源"""
    if not resources:
        return True

    print_step(3, f"Filtering resources: {', '.join(resources)}")

    # 读取解析后的数据
    data = json.loads(Path(parsed_file).read_text())

    # 过滤 paths
    filtered_paths = {
        res: endpoints
        for res, endpoints in data['paths'].items()
        if res in resources
    }

    # 过滤 schemas（只保留使用的）
    used_schemas = set()
    for endpoints in filtered_paths.values():
        for endpoint in endpoints:
            # 从 requestBody 提取 schema
            if endpoint.get('requestBody') and endpoint['requestBody'].get('schema_name'):
                used_schemas.add(endpoint['requestBody']['schema_name'])

            # 从 responses 提取 schema
            for response in endpoint.get('responses', {}).values():
                if response.get('schema_name'):
                    used_schemas.add(response['schema_name'])

    filtered_schemas = {
        name: schema
        for name, schema in data['schemas'].items()
        if name in used_schemas
    }

    # 更新数据
    data['paths'] = filtered_paths
    data['schemas'] = filtered_schemas

    # 保存
    Path(parsed_file).write_text(json.dumps(data, indent=2))

    print_success(f"Filtered to {len(filtered_paths)} resource(s), {len(filtered_schemas)} schema(s)")
    return True


def generate_code(
    parsed_file: str,
    output_dir: str,
    templates_dir: str,
    conflict_strategy: str = 'skip',
    dry_run: bool = False
) -> bool:
    """生成代码"""
    print_step(4, "Generating FastAPI code")

    script_dir = Path(__file__).parent
    generate_script = script_dir / "generate_code.py"

    cmd = [
        sys.executable, str(generate_script),
        "--parsed-data", parsed_file,
        "--output-dir", output_dir,
        "--templates-dir", templates_dir,
        "--conflict-strategy", conflict_strategy,
    ]

    if dry_run:
        cmd.append("--dry-run")

    return run_command(cmd, "Code generation")


def generate_client(parsed_file: str, output_file: str, templates_dir: str) -> bool:
    """生成 TypeScript API 客户端"""
    print_step(6, "Generating Next.js TypeScript client")

    script_dir = Path(__file__).parent
    generate_client_script = script_dir / "generate_client.py"

    return run_command(
        [
            sys.executable, str(generate_client_script),
            "--parsed-data", parsed_file,
            "--output", output_file,
            "--templates-dir", templates_dir
        ],
        "Client generation"
    )


def setup_alembic(output_dir: str, templates_dir: str) -> bool:
    """设置Alembic配置文件"""
    print_step(7, "Setting up Alembic configuration")

    output_path = Path(output_dir)
    template_path = Path(templates_dir).parent / "fastapi-template"

    # 复制alembic.ini
    alembic_ini_src = template_path / "alembic.ini"
    alembic_ini_dst = output_path / "alembic.ini"

    if alembic_ini_src.exists() and not alembic_ini_dst.exists():
        import shutil
        shutil.copy2(alembic_ini_src, alembic_ini_dst)
        print(f"  Created: {alembic_ini_dst}")

    # 复制alembic目录
    alembic_dir_src = template_path / "alembic"
    alembic_dir_dst = output_path / "alembic"

    if alembic_dir_src.exists() and not alembic_dir_dst.exists():
        import shutil
        shutil.copytree(alembic_dir_src, alembic_dir_dst)
        print(f"  Created: {alembic_dir_dst}/")

    return True


def run_migrations(output_dir: str, migration_message: str = "Auto-generated migration") -> bool:
    """运行Alembic数据库迁移"""
    print_step(8, "Running database migrations")

    output_path = Path(output_dir)

    # 检查alembic是否已配置
    if not (output_path / "alembic.ini").exists():
        print_error("Alembic not configured. Run with --setup-alembic first.")
        return False

    # 生成迁移
    print("  Generating migration...")
    result1 = run_command(
        ["alembic", "revision", "--autogenerate", "-m", migration_message],
        "Migration generation"
    )

    if not result1:
        print_warning("Migration generation failed, but continuing...")

    # 运行迁移
    print("  Applying migration...")
    result2 = run_command(
        ["alembic", "upgrade", "head"],
        "Migration execution"
    )

    if result2:
        print_success("  Migrations applied successfully")

    return result2


def create_init_files(output_dir: str):
    """创建 __init__.py 文件"""
    print_step(5, "Creating __init__.py files")

    output_path = Path(output_dir)

    for subdir in ['models', 'schemas', 'routers']:
        init_file = output_path / subdir / '__init__.py'
        if not init_file.exists():
            init_file.write_text(f'"""{ subdir.capitalize() } package"""\n')
            print(f"  Created: {init_file}")


def print_summary(output_dir: str, parsed_file: str):
    """打印生成摘要"""
    print_header("Generation Summary")

    data = json.loads(Path(parsed_file).read_text())

    print(f"{Colors.BOLD}Generated files:{Colors.END}")
    print(f"  📁 Output directory: {output_dir}")
    print(f"  📄 Models: {len(data['schemas'])} files")
    print(f"  📄 Schemas: {len(data['schemas'])} files")
    print(f"  📄 Routers: {len(data['paths'])} files")

    print(f"\n{Colors.BOLD}Next steps:{Colors.END}")
    print(f"  1. Review generated code in {output_dir}/")
    print(f"  2. Implement business logic (check TODO comments)")
    print(f"  3. Add authentication/authorization")
    print(f"  4. Configure database connection")
    print(f"  5. Run tests: pytest tests/")


def main():
    parser = argparse.ArgumentParser(
        description='API Builder - Generate FastAPI code from OpenAPI specs',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--spec',
        required=True,
        help='OpenAPI specification file (.yaml or .json)'
    )

    parser.add_argument(
        '--output',
        default='./generated',
        help='Output directory for generated code (default: ./generated)'
    )

    parser.add_argument(
        '--templates',
        help='Templates directory (default: ../assets/templates)'
    )

    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip OpenAPI spec validation'
    )

    parser.add_argument(
        '--resources',
        help='Comma-separated list of resources to generate (default: all)'
    )

    parser.add_argument(
        '--generate-client',
        action='store_true',
        help='Generate Next.js TypeScript API client'
    )

    parser.add_argument(
        '--client-output',
        help='Output file for TypeScript client (default: <output>/api-client.ts)'
    )

    parser.add_argument(
        '--setup-alembic',
        action='store_true',
        help='Copy Alembic configuration files to output directory'
    )

    parser.add_argument(
        '--run-migrations',
        action='store_true',
        help='Run Alembic database migrations (requires --setup-alembic first)'
    )

    parser.add_argument(
        '--migration-message',
        default='Auto-generated migration',
        help='Migration message (default: "Auto-generated migration")'
    )

    parser.add_argument(
        '--conflict-strategy',
        choices=['skip', 'backup', 'overwrite'],
        default='skip',
        help='How to handle existing files: skip (default) | backup | overwrite'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be generated without writing files'
    )

    args = parser.parse_args()

    # 设置路径
    script_dir = Path(__file__).parent
    templates_dir = args.templates or str(script_dir.parent / 'assets' / 'templates')
    parsed_file = Path(args.output) / 'parsed.json'

    # 解析资源列表
    resources = None
    if args.resources:
        resources = [r.strip() for r in args.resources.split(',')]

    # 设置client输出路径
    client_output = None
    if args.generate_client:
        client_output = args.client_output or str(Path(args.output) / 'api-client.ts')

    # 打印欢迎信息
    print_header("API Builder - FastAPI Code Generator")
    print(f"Spec: {args.spec}")
    print(f"Output: {args.output}")
    if resources:
        print(f"Resources: {', '.join(resources)}")
    if args.generate_client:
        print(f"Client: {client_output}")

    # 创建输出目录
    Path(args.output).mkdir(parents=True, exist_ok=True)

    # 执行步骤
    steps = [
        ("validate", lambda: validate_spec(args.spec, args.skip_validation)),
        ("parse", lambda: parse_spec(args.spec, str(parsed_file))),
        ("filter", lambda: filter_resources(str(parsed_file), resources)),
        ("generate", lambda: generate_code(
            str(parsed_file), args.output, templates_dir,
            conflict_strategy=args.conflict_strategy,
            dry_run=args.dry_run
        )),
        ("init_files", lambda: (create_init_files(args.output), True)[1]),
    ]

    # 添加client生成步骤（如果启用）
    if args.generate_client:
        steps.append(
            ("generate_client", lambda: generate_client(str(parsed_file), client_output, templates_dir))
        )

    # 添加alembic设置步骤（如果启用）
    if args.setup_alembic:
        steps.append(
            ("setup_alembic", lambda: setup_alembic(args.output, templates_dir))
        )

    # 添加migration步骤（如果启用）
    if args.run_migrations:
        if not args.setup_alembic:
            # 检查是否已有alembic配置
            if not (Path(args.output) / "alembic.ini").exists():
                print_error("--run-migrations requires --setup-alembic or existing Alembic configuration")
                sys.exit(1)
        steps.append(
            ("run_migrations", lambda: run_migrations(args.output, args.migration_message))
        )

    for step_name, step_func in steps:
        success = step_func()
        if not success:
            print_error(f"Step '{step_name}' failed. Aborting.")
            sys.exit(1)

    # 打印摘要
    print_summary(args.output, str(parsed_file))

    # 打印client信息（如果生成了）
    if args.generate_client:
        print(f"\n{Colors.GREEN}📦 TypeScript Client:{Colors.END}")
        print(f"  Generated: {client_output}")
        print(f"\n{Colors.CYAN}Next steps for frontend:{Colors.END}")
        print(f"  1. Copy {client_output} to your Next.js project (e.g., lib/api/)")
        print(f"  2. Set API_URL in frontend/.env.development or .env.local")
        print(f"  3. Import: import {{ apiClient }} from '@/lib/api/api-client'")

    # 打印migration信息（如果运行了）
    if args.run_migrations:
        print(f"\n{Colors.GREEN}🗄️  Database Migrations:{Colors.END}")
        print(f"  Status: Applied successfully")
        print(f"\n{Colors.CYAN}Next steps:{Colors.END}")
        print(f"  1. Review migration files in {args.output}/alembic/versions/")
        print(f"  2. Start your FastAPI application")
        print(f"  3. Database schema is ready!")
    elif args.setup_alembic:
        print(f"\n{Colors.YELLOW}🗄️  Alembic Configuration:{Colors.END}")
        print(f"  Alembic configured in {args.output}/")
        print(f"\n{Colors.CYAN}To run migrations manually:{Colors.END}")
        print(f"  cd {args.output}")
        print(f"  alembic revision --autogenerate -m 'Initial migration'")
        print(f"  alembic upgrade head")

    print_success("\n🎉 API generation complete!")


if __name__ == '__main__':
    main()
