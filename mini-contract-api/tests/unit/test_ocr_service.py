"""OCR 服务单元测试"""
from datetime import date
from unittest.mock import patch, MagicMock

from app.services.ocr_service import (
    extract_id_card_info,
    extract_id_card_validity,
    check_id_card_expired,
)


def _mock_ocr_result(texts: list[str]):
    """构造 RapidOCR 返回格式: [(bbox, text, score), ...]"""
    return [([0, 0, 0, 0], t, 0.99) for t in texts]


class TestExtractIdNumber:
    """身份证号提取"""

    @patch("app.services.ocr_service.ocr_engine")
    def test_normal_id_number(self, mock_engine):
        """正常 18 位身份证号"""
        mock_engine.return_value = (
            _mock_ocr_result(["姓名张三", "身份号码110101199003070070"]),
            None,
        )
        result = extract_id_card_info(b"fake_image")
        assert result["id_number"] == "110101199003070070"

    @patch("app.services.ocr_service.ocr_engine")
    def test_id_number_with_spaces(self, mock_engine):
        """身份证号中间有空格"""
        mock_engine.return_value = (
            _mock_ocr_result(["1101 0119 9003 0700 70"]),
            None,
        )
        result = extract_id_card_info(b"fake_image")
        assert result["id_number"] == "110101199003070070"

    @patch("app.services.ocr_service.ocr_engine")
    def test_id_number_with_x(self, mock_engine):
        """身份证号末尾是 X"""
        mock_engine.return_value = (
            _mock_ocr_result(["11010119900307002x"]),
            None,
        )
        result = extract_id_card_info(b"fake_image")
        assert result["id_number"] == "11010119900307002X"

    @patch("app.services.ocr_service.ocr_engine")
    def test_id_number_uppercase_x(self, mock_engine):
        """身份证号末尾是大写 X"""
        mock_engine.return_value = (
            _mock_ocr_result(["11010119900307002X"]),
            None,
        )
        result = extract_id_card_info(b"fake_image")
        assert result["id_number"] == "11010119900307002X"


class TestExtractName:
    """姓名提取"""

    @patch("app.services.ocr_service.ocr_engine")
    def test_name_same_line(self, mock_engine):
        """姓名和名字在同一行"""
        mock_engine.return_value = (
            _mock_ocr_result(["姓名李震宇", "身份号码110101199003070070"]),
            None,
        )
        result = extract_id_card_info(b"fake_image")
        assert result["name"] == "李震宇"

    @patch("app.services.ocr_service.ocr_engine")
    def test_name_next_line(self, mock_engine):
        """姓名标签单独一行，名字在下一行"""
        mock_engine.return_value = (
            _mock_ocr_result(["姓名", "李震宇", "身份号码110101199003070070"]),
            None,
        )
        result = extract_id_card_info(b"fake_image")
        assert result["name"] == "李震宇"

    @patch("app.services.ocr_service.ocr_engine")
    def test_name_with_spaces(self, mock_engine):
        """姓名标签中有空格"""
        mock_engine.return_value = (
            _mock_ocr_result(["姓 名 李 震 宇"]),
            None,
        )
        result = extract_id_card_info(b"fake_image")
        assert result["name"] == "李震宇"


class TestUnrecognizable:
    """无法识别场景"""

    @patch("app.services.ocr_service.ocr_engine")
    def test_empty_result(self, mock_engine):
        """OCR 返回空结果"""
        mock_engine.return_value = (None, None)
        result = extract_id_card_info(b"fake_image")
        assert result["name"] is None
        assert result["id_number"] is None
        assert result["raw_texts"] == []

    @patch("app.services.ocr_service.ocr_engine")
    def test_no_id_card_content(self, mock_engine):
        """非身份证图片，无相关文本"""
        mock_engine.return_value = (
            _mock_ocr_result(["这是一张风景照", "阳光明媚"]),
            None,
        )
        result = extract_id_card_info(b"fake_image")
        assert result["name"] is None
        assert result["id_number"] is None

    @patch("app.services.ocr_service.ocr_engine")
    def test_partial_recognition_name_only(self, mock_engine):
        """只识别到姓名，没有身份证号"""
        mock_engine.return_value = (
            _mock_ocr_result(["姓名张三", "性别男"]),
            None,
        )
        result = extract_id_card_info(b"fake_image")
        assert result["name"] == "张三"
        assert result["id_number"] is None

    @patch("app.services.ocr_service.ocr_engine")
    def test_partial_recognition_id_only(self, mock_engine):
        """只识别到身份证号，没有姓名"""
        mock_engine.return_value = (
            _mock_ocr_result(["110101199003070070"]),
            None,
        )
        result = extract_id_card_info(b"fake_image")
        assert result["name"] is None
        assert result["id_number"] == "110101199003070070"


class TestExtractValidity:
    """有效期限提取"""

    @patch("app.services.ocr_service.ocr_engine")
    def test_normal_validity(self, mock_engine):
        """正常有效期：2015.01.01-2035.01.01"""
        mock_engine.return_value = (
            _mock_ocr_result(["中华人民共和国", "有效期限", "2015.01.01-2035.01.01"]),
            None,
        )
        result = extract_id_card_validity(b"fake_image")
        assert result["start_date"] == date(2015, 1, 1)
        assert result["end_date"] == date(2035, 1, 1)
        assert result["is_long_term"] is False

    @patch("app.services.ocr_service.ocr_engine")
    def test_long_term_validity(self, mock_engine):
        """长期有效"""
        mock_engine.return_value = (
            _mock_ocr_result(["有效期限", "2005.06.15-长期"]),
            None,
        )
        result = extract_id_card_validity(b"fake_image")
        assert result["start_date"] == date(2005, 6, 15)
        assert result["end_date"] is None
        assert result["is_long_term"] is True

    @patch("app.services.ocr_service.ocr_engine")
    def test_validity_with_chinese_separators(self, mock_engine):
        """年月日分隔符"""
        mock_engine.return_value = (
            _mock_ocr_result(["2015年01月01日-2035年01月01日"]),
            None,
        )
        result = extract_id_card_validity(b"fake_image")
        assert result["start_date"] == date(2015, 1, 1)
        assert result["end_date"] == date(2035, 1, 1)

    @patch("app.services.ocr_service.ocr_engine")
    def test_validity_with_em_dash(self, mock_engine):
        """使用全角破折号 —"""
        mock_engine.return_value = (
            _mock_ocr_result(["2015.01.01—2035.01.01"]),
            None,
        )
        result = extract_id_card_validity(b"fake_image")
        assert result["start_date"] == date(2015, 1, 1)
        assert result["end_date"] == date(2035, 1, 1)

    @patch("app.services.ocr_service.ocr_engine")
    def test_validity_with_spaces(self, mock_engine):
        """OCR 识别结果含空格"""
        mock_engine.return_value = (
            _mock_ocr_result(["2015.01.01 - 2035.01.01"]),
            None,
        )
        result = extract_id_card_validity(b"fake_image")
        assert result["start_date"] == date(2015, 1, 1)
        assert result["end_date"] == date(2035, 1, 1)

    @patch("app.services.ocr_service.ocr_engine")
    def test_validity_split_across_lines(self, mock_engine):
        """有效期跨两行 OCR 文本"""
        mock_engine.return_value = (
            _mock_ocr_result(["有效期限2015.01.01", "-2035.01.01"]),
            None,
        )
        result = extract_id_card_validity(b"fake_image")
        assert result["start_date"] == date(2015, 1, 1)
        assert result["end_date"] == date(2035, 1, 1)

    @patch("app.services.ocr_service.ocr_engine")
    def test_unrecognizable_validity(self, mock_engine):
        """无法识别有效期"""
        mock_engine.return_value = (
            _mock_ocr_result(["中华人民共和国", "居民身份证"]),
            None,
        )
        result = extract_id_card_validity(b"fake_image")
        assert result["start_date"] is None
        assert result["end_date"] is None
        assert result["is_long_term"] is False


class TestCheckExpired:
    """有效期过期判断"""

    def test_not_expired(self):
        """未过期"""
        validity = {
            "start_date": date(2020, 1, 1),
            "end_date": date(2040, 1, 1),
            "is_long_term": False,
        }
        assert check_id_card_expired(validity) is False

    def test_expired(self):
        """已过期"""
        validity = {
            "start_date": date(2010, 1, 1),
            "end_date": date(2020, 1, 1),
            "is_long_term": False,
        }
        assert check_id_card_expired(validity) is True

    def test_long_term_never_expires(self):
        """长期有效永不过期"""
        validity = {
            "start_date": date(2005, 1, 1),
            "end_date": None,
            "is_long_term": True,
        }
        assert check_id_card_expired(validity) is False

    def test_no_end_date_not_expired(self):
        """无法识别结束日期时不判定过期"""
        validity = {
            "start_date": None,
            "end_date": None,
            "is_long_term": False,
        }
        assert check_id_card_expired(validity) is False
