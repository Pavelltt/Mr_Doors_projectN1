import os
import base64
import json
import re
import pytest
from openai import OpenAI


NUMBER_REGEX = r"(?:(?<!\w)-)?\d+[\.,]?\d*"


def normalize_num(token: str) -> str:
    t = str(token).strip()
    t = t.replace(',', '.')
    t = re.sub(r"\s+", "", t)
    t = re.sub(r"[^0-9\.-]", "", t)
    t = re.sub(r"\.(?!\d)", "", t)
    return t


def ask_openai_for_numbers(client: OpenAI, model: str, image_payload):
    system = (
        "Ты OCR-агент. Извлеки ВСЕ числовые значения. Верни СТРОГО JSON {\"numbers\":[\"...\"]}."
    )
    user = "Извлеки все числа. Верни только JSON."
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": [{"type": "text", "text": user}, image_payload]},
        ],
        temperature=0,
        max_tokens=800,
        response_format={"type": "json_object"}
    )
    text = resp.choices[0].message.content
    try:
        data = json.loads(text)
        raw = data.get("numbers", [])
        return [normalize_num(x) for x in raw]
    except Exception:
        return [normalize_num(n) for n in re.findall(NUMBER_REGEX, text)]


@pytest.mark.integration
def test_openai_with_schema_image():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY не задан")

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")

    # Ожидается файл с этой схемой: tests/assets/schema_sample.jpg
    path = os.path.join(os.path.dirname(__file__), "assets", "schema_sample.jpg")
    if not os.path.exists(path):
        pytest.skip("Нет входного файла tests/assets/schema_sample.jpg — добавьте изображение схемы")

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    data_url = f"data:image/jpeg;base64,{encoded}"

    numbers = ask_openai_for_numbers(
        client,
        model,
        {"type": "image_url", "image_url": {"url": data_url}}
    )

    # Базовые проверки качества: должно быть найдено достаточно чисел
    assert isinstance(numbers, list) and len(numbers) >= 10
    # Должны встречаться типичные размеры
    sample_hits = sum(1 for n in numbers if n in {"56", "300", "126", "860", "1149"})
    assert sample_hits >= 1
