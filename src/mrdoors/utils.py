"""Утилиты для обработки изображений и извлечения чисел."""

import re
import base64
import json
import logging
import time
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
from openai import OpenAI
from .config import PREFERRED_MODEL, OPENAI_TIMEOUT, OPENAI_RETRIES
from .analytics import analytics, analytics_client, CostCalculator, RequestStats

logger = logging.getLogger(__name__)

NUMBER_REGEX = r"(?:(?<!\w)-)?\d+[\.,]?\d*"

SYSTEM_PROMPT = (
    "Ты OCR-агент. Извлеки ВСЕ числовые значения с технического листа/чертежа (включая рукописные). "
    "Возвращай СТРОГО JSON {\"numbers\":[\"...\"]} без лишнего текста. "
    "Числа: целые/десятичные (разделитель точка). Диапазоны вида 65-85 верни как \"65\" и \"85\". "
    "Игнорируй подписи/единицы/символы. Порядок слева-направо, сверху-вниз."
)

USER_INSTRUCTION = (
    "Извлеки все числа с изображения. Верни только JSON {\"numbers\":[\"...\"]}."
)


def normalize_num(token: str) -> str:
    """Нормализация числового токена."""
    t = str(token).strip()
    t = t.replace(',', '.')
    t = re.sub(r"\s+", "", t)
    t = re.sub(r"[^0-9\.-]", "", t)
    # убрать завершающую точку, если после нее нет цифры
    t = re.sub(r"\.(?!\d)", "", t)
    return t


def preprocess_and_tile(jpeg_bytes: bytes, max_side: int = 1800, cols: int = 2, rows: int = 3) -> list:
    """Лёгкий препроцессинг без GPU и разбиение на тайлы. Возвращает список data URLs."""
    img = Image.open(BytesIO(jpeg_bytes)).convert('RGB')
    # Масштабирование с сохранением соотношения
    w, h = img.size
    k = max(w, h) / max_side if max(w, h) > max_side else 1.0
    if k > 1.0:
        img = img.resize((int(w / k), int(h / k)), Image.LANCZOS)
    # Повышаем контраст/резкость
    img = ImageEnhance.Contrast(img).enhance(1.3)
    img = ImageEnhance.Sharpness(img).enhance(1.4)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

    W, H = img.size
    tile_w = max(W // cols, 1)
    tile_h = max(H // rows, 1)

    tiles = []
    for r in range(rows):
        for c in range(cols):
            left = c * tile_w
            top = r * tile_h
            right = W if c == cols - 1 else min((c + 1) * tile_w, W)
            bottom = H if r == rows - 1 else min((r + 1) * tile_h, H)
            tile = img.crop((left, top, right, bottom))
            if tile.width == 0 or tile.height == 0:
                logger.debug(f"Skipping empty tile {r=} {c=}")
                continue
            # Лёгкое увеличение каждого тайла для читаемости
            tile = tile.resize((tile.width * 2, tile.height * 2), Image.LANCZOS)
            buf = BytesIO()
            tile.save(buf, format='JPEG', quality=92)
            encoded = base64.b64encode(buf.getvalue()).decode('ascii')
            tiles.append(f"data:image/jpeg;base64,{encoded}")
    return tiles


def ask_openai_for_numbers(image_payload, req_id: str, client: OpenAI):
    """Запрос к OpenAI для извлечения чисел с изображения."""
    models_to_try = [PREFERRED_MODEL, 'gpt-4o-mini'] if PREFERRED_MODEL != 'gpt-4o-mini' else ['gpt-4o-mini']
    last_text = ""
    
    for model in models_to_try:
        start_time = time.time()
        try:
            logger.info(f"[{req_id}] OpenAI call model={model} payload_type={image_payload.get('type')}")
            
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": [
                        {"type": "text", "text": USER_INSTRUCTION},
                        image_payload
                    ]},
                ],
                temperature=0,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            duration = time.time() - start_time
            text = resp.choices[0].message.content
            last_text = text
            
            # Извлечение статистики использования токенов
            usage = resp.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            
            # Расчет стоимости
            cost = CostCalculator.calculate_cost(model, input_tokens, output_tokens)
            
            # Сохранение статистики
            stats = RequestStats(
                duration=duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
                model=model,
                request_id=req_id,
                chat_id=req_id.split(":")[0] if ":" in req_id else None,
                message_id=int(req_id.split(":")[1].split("#")[0]) if ":" in req_id else None,
                tile_id=req_id.split("#")[-1] if "#" in req_id else None,
                raw_prompt={"system": SYSTEM_PROMPT, "instruction": USER_INSTRUCTION},
                raw_response={"content": text},
                status="success",
                originated_at=start_time,
            )
            analytics.add_request(
                stats,
                extra={
                    "numbers": [normalize_num(x) for x in raw] if isinstance(raw, list) else None,
                },
            )
            
            # Логирование с деталями стоимости
            logger.info(f"[{req_id}] OpenAI response: {duration:.2f}s, "
                       f"{input_tokens + output_tokens} tokens, "
                       f"${cost:.4f} ({cost * 100:.2f}¢)")
            
            logger.debug(f"[{req_id}] OpenAI raw: {text[:500]}")

            data = json.loads(text)
            raw = data.get("numbers", [])
            if isinstance(raw, list) and raw:
                nums = [normalize_num(x) for x in raw]
                nums = [n for n in nums if re.fullmatch(NUMBER_REGEX, n)]
                if nums:
                    logger.info(f"[{req_id}] OpenAI extracted {len(nums)} numbers")
                    return nums
        except Exception as e:
            duration = time.time() - start_time
            logger.warning(f"[{req_id}] OpenAI error on model {model} after {duration:.2f}s: {e}")
            continue
    
    # Регэксп по последнему тексту (как крайняя мера)
    fallback = [normalize_num(n) for n in re.findall(NUMBER_REGEX, last_text, flags=re.UNICODE)]
    if fallback:
        try:
            analytics.add_request(
                RequestStats(
                    duration=time.time() - start_time,
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=0.0,
                    model=models_to_try[-1],
                    request_id=req_id,
                    status="partial",
                    raw_prompt={"system": SYSTEM_PROMPT, "instruction": USER_INSTRUCTION},
                    raw_response={"content": last_text},
                    numbers=fallback,
                    originated_at=start_time,
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("Analytics fallback event failed: %s", exc)
    logger.info(f"[{req_id}] Fallback extracted {len(fallback)} numbers")
    return [n for n in fallback if n]


def extract_numbers_fallback(text: str):
    """Fallback извлечение чисел через регулярные выражения."""
    # склеить пробелы внутри чисел: "1 200" -> "1200"
    pre = re.sub(r"(?<=\d)\s+(?=\d)", "", text)
    found = re.findall(NUMBER_REGEX, pre, flags=re.UNICODE)
    return [normalize_num(num) for num in found]
