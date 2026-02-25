#!/usr/bin/env python3
"""
Test script for api-builder scripts

测试所有核心脚本的功能。
"""

import sys
import subprocess
import json
import shutil
from pathlib import Path


class TestRunner:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.test_dir = self.script_dir / 'test_output'
        self.passed = 0
        self.failed = 0

    def setup(self):
        """设置测试环境"""
        print("🔧 Setting up test environment...")

        # 清理旧的测试输出
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

        self.test_dir.mkdir(parents=True)
        print(f"   Created test directory: {self.test_dir}")

    def cleanup(self):
        """清理测试环境"""
        print("\n🧹 Cleaning up...")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            print("   Removed test directory")

    def run_command(self, cmd: list, description: str) -> tuple[bool, str]:
        """运行命令并返回结果"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            success = result.returncode == 0
            output = result.stdout + result.stderr
            return success, output
        except Exception as e:
            return False, str(e)

    def test_validate_spec(self):
        """测试 validate_spec.py"""
        print("\n" + "="*60)
        print("Test 1: validate_spec.py")
        print("="*60)

        validate_script = self.script_dir / "validate_spec.py"
        test_spec = self.script_dir / "test_spec.yaml"

        success, output = self.run_command(
            [sys.executable, str(validate_script), str(test_spec)],
            "Validate spec"
        )

        print(output)

        if success and "✅ Validation PASSED" in output:
            print("✅ PASSED: validate_spec.py works correctly")
            self.passed += 1
            return True
        else:
            print("❌ FAILED: validate_spec.py validation failed")
            self.failed += 1
            return False

    def test_parse_openapi(self):
        """测试 parse_openapi.py"""
        print("\n" + "="*60)
        print("Test 2: parse_openapi.py")
        print("="*60)

        parse_script = self.script_dir / "parse_openapi.py"
        test_spec = self.script_dir / "test_spec.yaml"
        parsed_output = self.test_dir / "parsed.json"

        success, output = self.run_command(
            [sys.executable, str(parse_script), str(test_spec), "--output", str(parsed_output)],
            "Parse spec"
        )

        print(output)

        if success and parsed_output.exists():
            # 验证输出内容
            parsed_data = json.loads(parsed_output.read_text())

            checks = [
                ('schemas' in parsed_data, "Has schemas"),
                ('paths' in parsed_data, "Has paths"),
                ('User' in parsed_data['schemas'], "User schema exists"),
                ('users' in parsed_data['paths'], "Users paths exist"),
            ]

            all_passed = True
            for check, description in checks:
                if check:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description}")
                    all_passed = False

            if all_passed:
                print("✅ PASSED: parse_openapi.py works correctly")
                self.passed += 1
                return True
            else:
                print("❌ FAILED: parse_openapi.py output incomplete")
                self.failed += 1
                return False
        else:
            print("❌ FAILED: parse_openapi.py failed to generate output")
            self.failed += 1
            return False

    def test_generate_code(self):
        """测试 generate_code.py"""
        print("\n" + "="*60)
        print("Test 3: generate_code.py")
        print("="*60)

        # 先解析 spec
        parse_script = self.script_dir / "parse_openapi.py"
        test_spec = self.script_dir / "test_spec.yaml"
        parsed_output = self.test_dir / "parsed.json"

        self.run_command(
            [sys.executable, str(parse_script), str(test_spec), "--output", str(parsed_output)],
            "Parse spec for code generation"
        )

        # 生成代码
        generate_script = self.script_dir / "generate_code.py"
        templates_dir = self.script_dir.parent / "assets" / "templates"
        output_dir = self.test_dir / "generated"

        success, output = self.run_command(
            [
                sys.executable, str(generate_script),
                "--parsed-data", str(parsed_output),
                "--output-dir", str(output_dir),
                "--templates-dir", str(templates_dir)
            ],
            "Generate code"
        )

        print(output)

        if success:
            # 检查生成的文件
            checks = [
                ((output_dir / "models" / "user.py").exists(), "User model generated"),
                ((output_dir / "schemas" / "user.py").exists(), "User schema generated"),
                ((output_dir / "routers" / "users.py").exists(), "Users router generated"),
            ]

            all_passed = True
            for check, description in checks:
                if check:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description}")
                    all_passed = False

            if all_passed:
                print("✅ PASSED: generate_code.py works correctly")
                self.passed += 1
                return True
            else:
                print("❌ FAILED: generate_code.py did not generate all files")
                self.failed += 1
                return False
        else:
            print("❌ FAILED: generate_code.py execution failed")
            self.failed += 1
            return False

    def test_cli(self):
        """测试 cli.py"""
        print("\n" + "="*60)
        print("Test 4: cli.py (end-to-end)")
        print("="*60)

        cli_script = self.script_dir / "cli.py"
        test_spec = self.script_dir / "test_spec.yaml"
        output_dir = self.test_dir / "cli_output"

        success, output = self.run_command(
            [
                sys.executable, str(cli_script),
                "--spec", str(test_spec),
                "--output", str(output_dir)
            ],
            "CLI end-to-end test"
        )

        print(output)

        if success and "🎉 API generation complete!" in output:
            # 检查生成的文件
            checks = [
                ((output_dir / "models" / "user.py").exists(), "CLI: User model generated"),
                ((output_dir / "schemas" / "user.py").exists(), "CLI: User schema generated"),
                ((output_dir / "routers" / "users.py").exists(), "CLI: Users router generated"),
                ((output_dir / "parsed.json").exists(), "CLI: Parsed data saved"),
            ]

            all_passed = True
            for check, description in checks:
                if check:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description}")
                    all_passed = False

            if all_passed:
                print("✅ PASSED: cli.py end-to-end test works correctly")
                self.passed += 1
                return True
            else:
                print("❌ FAILED: cli.py did not generate all files")
                self.failed += 1
                return False
        else:
            print("❌ FAILED: cli.py execution failed")
            self.failed += 1
            return False

    def test_generate_client(self):
        """测试 generate_client.py"""
        print("\n" + "="*60)
        print("Test 5: generate_client.py")
        print("="*60)

        # 先解析 spec
        parse_script = self.script_dir / "parse_openapi.py"
        test_spec = self.script_dir / "test_spec.yaml"
        parsed_output = self.test_dir / "parsed_for_client.json"

        self.run_command(
            [sys.executable, str(parse_script), str(test_spec), "--output", str(parsed_output)],
            "Parse spec for client generation"
        )

        # 生成 client
        generate_client_script = self.script_dir / "generate_client.py"
        templates_dir = self.script_dir.parent / "assets" / "templates"
        client_output = self.test_dir / "api-client.ts"

        success, output = self.run_command(
            [
                sys.executable, str(generate_client_script),
                "--parsed-data", str(parsed_output),
                "--output", str(client_output),
                "--templates-dir", str(templates_dir)
            ],
            "Generate TypeScript client"
        )

        print(output)

        if success and client_output.exists():
            # 验证生成的client内容
            client_content = client_output.read_text()

            checks = [
                ("export interface" in client_content, "TypeScript interfaces generated"),
                ("class ApiClient" in client_content, "ApiClient class generated"),
                ("async list_users" in client_content or "async get_user" in client_content, "API methods generated"),
                ("export const apiClient" in client_content, "Client instance exported"),
            ]

            all_passed = True
            for check, description in checks:
                if check:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description}")
                    all_passed = False

            if all_passed:
                print("✅ PASSED: generate_client.py works correctly")
                self.passed += 1
                return True
            else:
                print("❌ FAILED: generate_client.py output incomplete")
                self.failed += 1
                return False
        else:
            print("❌ FAILED: generate_client.py execution failed")
            self.failed += 1
            return False

    def test_cli_with_client(self):
        """测试 cli.py 带 client 生成"""
        print("\n" + "="*60)
        print("Test 6: cli.py with --generate-client")
        print("="*60)

        cli_script = self.script_dir / "cli.py"
        test_spec = self.script_dir / "test_spec.yaml"
        output_dir = self.test_dir / "cli_with_client_output"

        success, output = self.run_command(
            [
                sys.executable, str(cli_script),
                "--spec", str(test_spec),
                "--output", str(output_dir),
                "--generate-client"
            ],
            "CLI with client generation"
        )

        print(output)

        if success and "🎉 API generation complete!" in output:
            # 检查生成的文件
            checks = [
                ((output_dir / "models" / "user.py").exists(), "CLI+Client: User model generated"),
                ((output_dir / "schemas" / "user.py").exists(), "CLI+Client: User schema generated"),
                ((output_dir / "routers" / "users.py").exists(), "CLI+Client: Users router generated"),
                ((output_dir / "api-client.ts").exists(), "CLI+Client: TypeScript client generated"),
                ("TypeScript Client:" in output, "CLI+Client: Client info displayed"),
            ]

            all_passed = True
            for check, description in checks:
                if check:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description}")
                    all_passed = False

            if all_passed:
                print("✅ PASSED: cli.py with --generate-client works correctly")
                self.passed += 1
                return True
            else:
                print("❌ FAILED: cli.py with --generate-client did not generate all files")
                self.failed += 1
                return False
        else:
            print("❌ FAILED: cli.py with --generate-client execution failed")
            self.failed += 1
            return False

    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Total: {self.passed + self.failed}")

        if self.failed == 0:
            print("\n🎉 All tests passed!")
            return True
        else:
            print(f"\n⚠️  {self.failed} test(s) failed")
            return False

    def test_alembic_setup(self):
        """测试 Alembic 配置"""
        print("\n" + "="*60)
        print("Test 7: cli.py with --setup-alembic")
        print("="*60)

        cli_script = self.script_dir / "cli.py"
        test_spec = self.script_dir / "test_spec.yaml"
        output_dir = self.test_dir / "alembic_setup_output"

        success, output = self.run_command(
            [
                sys.executable, str(cli_script),
                "--spec", str(test_spec),
                "--output", str(output_dir),
                "--setup-alembic"
            ],
            "CLI with Alembic setup"
        )

        print(output)

        if success and "🎉 API generation complete!" in output:
            # 检查生成的文件
            checks = [
                ((output_dir / "alembic.ini").exists(), "Alembic: alembic.ini created"),
                ((output_dir / "alembic" / "env.py").exists(), "Alembic: env.py created"),
                ((output_dir / "alembic" / "versions").exists(), "Alembic: versions directory created"),
                ("Alembic configured" in output or "Alembic Configuration" in output, "Alembic: status message shown"),
            ]

            all_passed = True
            for check, description in checks:
                if check:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description}")
                    all_passed = False

            if all_passed:
                print("✅ PASSED: cli.py with --setup-alembic works correctly")
                self.passed += 1
                return True
            else:
                print("❌ FAILED: cli.py with --setup-alembic did not configure Alembic properly")
                self.failed += 1
                return False
        else:
            print("❌ FAILED: cli.py with --setup-alembic execution failed")
            self.failed += 1
            return False

    def run_all(self):
        """运行所有测试"""
        print("🚀 Running api-builder scripts tests\n")

        self.setup()

        try:
            self.test_validate_spec()
            self.test_parse_openapi()
            self.test_generate_code()
            self.test_cli()
            self.test_generate_client()
            self.test_cli_with_client()
            self.test_alembic_setup()

            all_passed = self.print_summary()

            return all_passed
        finally:
            self.cleanup()


def main():
    runner = TestRunner()
    all_passed = runner.run_all()

    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
