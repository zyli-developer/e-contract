"""合同模板种子数据单元测试"""
import re

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.seed_templates import (
    DEFAULT_TEMPLATES,
    LEASE_CONTRACT_HTML,
    LEASE_CONTRACT_SIGNATORIES,
    LEASE_CONTRACT_VARIABLES,
    SIMPLE_LEASE_HTML,
    SIMPLE_LEASE_VARIABLES,
    SIMPLE_LEASE_SIGNATORIES,
    seed_templates,
)


class TestLeaseContractData:
    """房屋租赁合同模板数据验证"""

    def test_template_count(self):
        """应至少有一个默认模板"""
        assert len(DEFAULT_TEMPLATES) >= 1

    def test_template_basic_fields(self):
        """模板应包含必要字段"""
        tpl = DEFAULT_TEMPLATES[0]
        assert tpl["name"] == "房屋租赁合同"
        assert tpl["description"]
        assert tpl["category"] == "lease"
        assert tpl["content"]
        assert tpl["variables"]
        assert tpl["signatories"]

    def test_html_contains_all_variable_placeholders(self):
        """HTML 内容应包含所有变量占位符 {{...}}"""
        for var in LEASE_CONTRACT_VARIABLES:
            placeholder = "{{" + var["name"] + "}}"
            assert placeholder in LEASE_CONTRACT_HTML, (
                f"HTML 中缺少占位符: {placeholder}"
            )

    def test_all_placeholders_have_variable_definitions(self):
        """HTML 中所有 {{...}} 占位符都应有对应的变量定义（签章占位符除外）"""
        signature_placeholders = {"partyASignature", "partyBSignature"}
        placeholders = set(re.findall(r"\{\{(\w+)\}\}", LEASE_CONTRACT_HTML)) - signature_placeholders
        variable_names = {v["name"] for v in LEASE_CONTRACT_VARIABLES}
        undefined = placeholders - variable_names
        assert not undefined, f"HTML 中存在未定义的占位符: {undefined}"

    def test_variables_and_placeholders_match_exactly(self):
        """变量定义与 HTML 占位符应一一对应（签章占位符除外）"""
        signature_placeholders = {"partyASignature", "partyBSignature"}
        placeholders = set(re.findall(r"\{\{(\w+)\}\}", LEASE_CONTRACT_HTML)) - signature_placeholders
        variable_names = {v["name"] for v in LEASE_CONTRACT_VARIABLES}
        assert placeholders == variable_names

    def test_variable_fields(self):
        """每个变量应有 name、label、type、party 字段"""
        for var in LEASE_CONTRACT_VARIABLES:
            assert "name" in var, f"变量缺少 name: {var}"
            assert "label" in var, f"变量缺少 label: {var}"
            assert "type" in var, f"变量缺少 type: {var}"
            assert var["type"] in ("text", "date"), (
                f"变量类型无效: {var['name']} -> {var['type']}"
            )
            assert "party" in var, f"变量缺少 party: {var}"
            assert var["party"] in ("A", "B", "common"), (
                f"变量 party 值无效: {var['name']} -> {var['party']}"
            )

    def test_party_a_variables(self):
        """甲方变量应标记为 party=A"""
        party_a = [v for v in LEASE_CONTRACT_VARIABLES if v["party"] == "A"]
        party_a_names = {v["name"] for v in party_a}
        assert "partyAName" in party_a_names
        assert "partyAIdCard" in party_a_names
        assert "partyAPhone" in party_a_names

    def test_party_b_variables(self):
        """乙方变量应标记为 party=B"""
        party_b = [v for v in LEASE_CONTRACT_VARIABLES if v["party"] == "B"]
        party_b_names = {v["name"] for v in party_b}
        assert "partyBName" in party_b_names
        assert "partyBIdCard" in party_b_names
        assert "partyBPhone" in party_b_names

    def test_common_variables(self):
        """公共变量应标记为 party=common"""
        common = [v for v in LEASE_CONTRACT_VARIABLES if v["party"] == "common"]
        common_names = {v["name"] for v in common}
        assert "houseAddress" in common_names
        assert "monthlyRent" in common_names

    def test_variable_names_unique(self):
        """变量名应唯一"""
        names = [v["name"] for v in LEASE_CONTRACT_VARIABLES]
        assert len(names) == len(set(names)), "存在重复的变量名"

    def test_signatories_contains_both_parties(self):
        """签署方应包含甲方和乙方"""
        roles = [s["role"] for s in LEASE_CONTRACT_SIGNATORIES]
        assert "甲方（出租方）" in roles
        assert "乙方（承租方）" in roles

    def test_signatories_count(self):
        """签署方应恰好两个"""
        assert len(LEASE_CONTRACT_SIGNATORIES) == 2

    def test_html_has_title(self):
        """HTML 应包含合同标题"""
        assert "房屋租赁合同" in LEASE_CONTRACT_HTML

    def test_html_has_sections(self):
        """HTML 应包含主要章节"""
        sections = [
            "出租房屋情况和租赁用途",
            "交付日期和租赁期限",
            "租金、支付方式和期限",
            "保证金和其他费用",
            "房屋使用要求和维修责任",
            "房屋返还时的状态",
            "解除本合同的条件",
            "解决争议的方式",
            "补充条款",
        ]
        for section in sections:
            assert section in LEASE_CONTRACT_HTML, f"HTML 中缺少章节: {section}"


class TestSimpleLeaseContractData:
    """租房合同（简版）模板数据验证"""

    def test_template_in_defaults(self):
        """简版模板应在默认列表中"""
        names = [t["name"] for t in DEFAULT_TEMPLATES]
        assert "租房合同（简版）" in names

    def test_html_contains_all_variable_placeholders(self):
        """HTML 内容应包含所有变量占位符"""
        for var in SIMPLE_LEASE_VARIABLES:
            placeholder = "{{" + var["name"] + "}}"
            assert placeholder in SIMPLE_LEASE_HTML, (
                f"HTML 中缺少占位符: {placeholder}"
            )

    def test_all_placeholders_have_variable_definitions(self):
        """HTML 中所有占位符都应有对应变量定义（签章占位符除外）"""
        signature_placeholders = {"partyASignature", "partyBSignature"}
        placeholders = set(re.findall(r"\{\{(\w+)\}\}", SIMPLE_LEASE_HTML)) - signature_placeholders
        variable_names = {v["name"] for v in SIMPLE_LEASE_VARIABLES}
        undefined = placeholders - variable_names
        assert not undefined, f"存在未定义的占位符: {undefined}"

    def test_variable_fields(self):
        """每个变量应有完整字段"""
        for var in SIMPLE_LEASE_VARIABLES:
            assert "name" in var
            assert "label" in var
            assert "type" in var
            assert var["type"] in ("text", "date")
            assert "party" in var
            assert var["party"] in ("A", "B", "common")

    def test_variable_names_unique(self):
        """变量名应唯一"""
        names = [v["name"] for v in SIMPLE_LEASE_VARIABLES]
        assert len(names) == len(set(names))

    def test_signatories(self):
        """签署方应包含甲乙双方"""
        roles = [s["role"] for s in SIMPLE_LEASE_SIGNATORIES]
        assert len(roles) == 2
        assert "甲方（出租方）" in roles
        assert "乙方（承租方）" in roles

    def test_has_key_sections(self):
        """HTML 应包含关键章节"""
        sections = ["房屋及租期", "租金", "押金", "费用承担", "甲方违约", "乙方违约", "安全责任"]
        for s in sections:
            assert s in SIMPLE_LEASE_HTML, f"缺少章节: {s}"

    def test_has_address_variables(self):
        """应有细分的地址变量"""
        names = {v["name"] for v in SIMPLE_LEASE_VARIABLES}
        assert "communityName" in names
        assert "buildingNo" in names
        assert "roomNo" in names

    def test_has_fee_variables(self):
        """应有费用底数变量"""
        names = {v["name"] for v in SIMPLE_LEASE_VARIABLES}
        assert "electricReading" in names
        assert "waterReading" in names
        assert "gasReading" in names


class TestSeedTemplatesFunction:
    """seed_templates 函数测试"""

    @pytest.mark.asyncio
    async def test_creates_template_when_not_exists(self):
        """模板不存在时应创建"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        with patch("app.seed_templates.async_session_factory") as mock_factory:
            mock_factory.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            await seed_templates()
            assert mock_session.add.call_count == len(DEFAULT_TEMPLATES)

    @pytest.mark.asyncio
    async def test_skips_when_template_exists(self):
        """模板已存在时应跳过（幂等性）"""
        mock_session = AsyncMock()
        mock_template = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_template
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("app.seed_templates.async_session_factory") as mock_factory:
            mock_factory.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            await seed_templates()
            mock_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_handles_exception_gracefully(self):
        """异常时不应崩溃"""
        with patch("app.seed_templates.async_session_factory") as mock_factory:
            mock_factory.return_value.__aenter__ = AsyncMock(
                side_effect=Exception("Connection refused")
            )
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            # 不应抛异常
            await seed_templates()
