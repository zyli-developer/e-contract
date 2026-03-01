"""身份证 OCR 识别服务（基于 RapidOCR）"""
import re
from datetime import date

from rapidocr_onnxruntime import RapidOCR

ocr_engine = RapidOCR()


def extract_id_card_info(image_bytes: bytes) -> dict:
    """
    识别身份证正面照片，提取姓名和身份证号。

    Returns:
        {"name": str | None, "id_number": str | None, "raw_texts": list[str]}
    """
    result, _ = ocr_engine(image_bytes)
    texts = [item[1] for item in result] if result else []

    # 提取身份证号：18 位数字（最后一位可能是 X）
    id_number = None
    for t in texts:
        m = re.search(r"\d{17}[\dXx]", t.replace(" ", ""))
        if m:
            id_number = m.group().upper()
            break

    # 提取姓名："姓名" 标签后的文本
    name = None
    for i, t in enumerate(texts):
        if "姓名" in t.replace(" ", ""):
            # "姓名李震宇" — 姓名和名字在同一行
            clean = t.replace(" ", "").replace("姓名", "")
            if clean:
                name = clean
            elif i + 1 < len(texts):
                # "姓名" 单独一行，名字在下一行
                name = texts[i + 1].strip()
            break

    return {"name": name, "id_number": id_number, "raw_texts": texts}


def extract_id_card_validity(image_bytes: bytes) -> dict:
    """
    识别身份证背面（国徽面），提取有效期限。

    有效期格式：
    - "2015.01.01-2035.01.01"（固定期限）
    - "2015.01.01-长期"（长期有效）

    Returns:
        {
            "start_date": date | None,
            "end_date": date | None,   # 长期有效时为 None
            "is_long_term": bool,
            "raw_texts": list[str],
        }
    """
    result, _ = ocr_engine(image_bytes)
    texts = [item[1] for item in result] if result else []

    start_date = None
    end_date = None
    is_long_term = False

    # 将所有文本拼接后去空格，方便匹配跨行的有效期
    joined = " ".join(texts)
    clean = joined.replace(" ", "").replace(".", ".")

    # 匹配有效期日期：YYYY.MM.DD-YYYY.MM.DD 或 YYYY.MM.DD-长期
    m = re.search(
        r"(\d{4})[.\-年](\d{2})[.\-月](\d{2})日?[—\-~至]"
        r"(?:(\d{4})[.\-年](\d{2})[.\-月](\d{2})日?|(长期))",
        clean,
    )
    if m:
        try:
            start_date = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

        if m.group(7):  # "长期"
            is_long_term = True
        else:
            try:
                end_date = date(int(m.group(4)), int(m.group(5)), int(m.group(6)))
            except ValueError:
                pass

    return {
        "start_date": start_date,
        "end_date": end_date,
        "is_long_term": is_long_term,
        "raw_texts": texts,
    }


def check_id_card_expired(validity: dict) -> bool:
    """检查身份证是否已过期。返回 True 表示已过期。"""
    if validity["is_long_term"]:
        return False
    if validity["end_date"] is None:
        # 无法识别到结束日期，不做过期判断
        return False
    return date.today() > validity["end_date"]
