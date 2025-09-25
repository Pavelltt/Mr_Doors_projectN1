import re


NUMBER_REGEX = r"(?:(?<!\w)-)?\d+[\.,]?\d*"


def normalize_num(token: str) -> str:
    t = str(token).strip()
    t = t.replace(',', '.')
    t = re.sub(r"\s+", "", t)
    t = re.sub(r"[^0-9\.-]", "", t)
    # убрать завершающую точку, если после нее нет цифры
    t = re.sub(r"\.(?!\d)", "", t)
    return t


def extract_numbers_fallback(text: str):
    # склеить пробелы внутри чисел: "1 200" -> "1200"
    pre = re.sub(r"(?<=\d)\s+(?=\d)", "", text)
    found = re.findall(NUMBER_REGEX, pre, flags=re.UNICODE)
    return [normalize_num(num) for num in found]


def test_extract_simple():
    s = "Размеры: 1200, 85-95, 3.5мм, -12, 0.75"
    nums = extract_numbers_fallback(s)
    assert "1200" in nums
    assert "85" in nums and "95" in nums
    assert "3.5" in nums
    assert "-12" in nums
    assert "0.75" in nums


def test_commas_and_spaces():
    s = "1 200, 45,6;  78 , 90мм"
    nums = extract_numbers_fallback(s)
    assert "1200" in nums
    assert "45.6" in nums
    assert "78" in nums
    assert "90" in nums


