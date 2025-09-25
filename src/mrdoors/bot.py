"""Telegram бот для распознавания чисел на схемах."""

import os
import time
import threading
import logging
from itertools import groupby
from logging.handlers import RotatingFileHandler
import telebot
from telebot import apihelper
from openai import OpenAI
from .config import BOT_TOKEN, OPENAI_API_KEY, OPENAI_TIMEOUT, OPENAI_RETRIES, LOG_LEVEL
from .utils import preprocess_and_tile, ask_openai_for_numbers
from .analytics import analytics
def format_numbers_readable(numbers: list[str], per_line: int = 10) -> str:
    """Сформировать компактный и структурированный вывод списка чисел."""

    def group_key(value: str) -> tuple:
        clean = value.lstrip('-')
        integer_part, _, fractional = clean.partition('.')
        digits = len(integer_part) if integer_part else 1
        has_fraction = bool(fractional)
        return (has_fraction, digits)

    def group_title(has_fraction: bool, digits: int) -> str:
        if has_fraction:
            return f"Дробные (целая часть {digits}-значная)"
        suffix = {
            1: "значные",
            2: "значные",
            3: "значные",
            4: "значные",
        }.get(digits, "значные")
        return f"{digits}-{suffix}"

    def chunk(iterable: list[str], size: int):
        for idx in range(0, len(iterable), size):
            yield iterable[idx: idx + size]

    lines: list[str] = []
    for (has_fraction, digits), grouped in groupby(numbers, key=group_key):
        group_list = list(grouped)
        if not group_list:
            continue
        lines.append(group_title(has_fraction, digits) + ":")
        for part in chunk(group_list, per_line):
            lines.append("  " + ", ".join(part))

    return "\n".join(lines)


logger = logging.getLogger(__name__)


class TypingIndicator:
    """Индикатор печати для Telegram бота."""
    
    def __init__(self, bot_instance: telebot.TeleBot, chat_id: int, interval_seconds: float = 4.0):
        self.bot = bot_instance
        self.chat_id = chat_id
        self.interval = interval_seconds
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        while not self._stop.is_set():
            try:
                self.bot.send_chat_action(self.chat_id, 'typing')
            except Exception as e:
                logger.debug(f"typing emit failed: {e}")
            finally:
                time.sleep(self.interval)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop.set()
        self._thread.join(timeout=1)


def setup_logging():
    """Настройка логирования."""
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("mrdoors.bot")
    logger.setLevel(LOG_LEVEL)
    fmt = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    fh = RotatingFileHandler("logs/bot.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(LOG_LEVEL)
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    
    return logger


def create_bot():
    """Создание и настройка бота."""
    logger = setup_logging()
    
    bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
    # Увеличим таймауты HTTP для Telegram API
    apihelper.READ_TIMEOUT = 60
    apihelper.CONNECT_TIMEOUT = 15

    client = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_TIMEOUT, max_retries=OPENAI_RETRIES)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "Привет! Отправь фото схемы замера — найду на ней числа (OpenAI Vision).")

    @bot.message_handler(commands=['stats'])
    def send_stats(message):
        summary = analytics.get_session_summary()
        formatted = analytics.format_summary(summary)
        bot.reply_to(message, f"Статистика сессии:\n{formatted}")

    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        req_id = f"{message.chat.id}:{message.message_id}"
        logger.info(f"[{req_id}] Received photo set sizes={len(message.photo)}")
        bot.reply_to(message, "Получил фото. Распознаю (подготовка → разбиение → OpenAI)...")

        try:
            with TypingIndicator(bot, message.chat.id):
                # Самое большое фото
                file_id = message.photo[-1].file_id
                
                try:
                    file_info = bot.get_file(file_id)
                    file_path = file_info.file_path
                    logger.info(f"[{req_id}] TG file_path={file_path}")
                except Exception as e:
                    logger.error(f"[{req_id}] Failed to get file info: {e}")
                    bot.send_message(message.chat.id, "Ошибка при получении файла. Попробуйте отправить фото еще раз.")
                    return

                try:
                    # Скачиваем файл и делаем локальный лёгкий препроцессинг + разбиение
                    original_bytes = bot.download_file(file_path)
                    tiles = preprocess_and_tile(original_bytes, max_side=2000, cols=2, rows=3)
                    logger.info(f"[{req_id}] Prepared {len(tiles)} tiles")
                except Exception as e:
                    logger.error(f"[{req_id}] Failed to process image: {e}")
                    bot.send_message(message.chat.id, "Ошибка при обработке изображения. Убедитесь, что это корректный файл изображения.")
                    return

                numbers_set = set()
                old_requests_len = len(analytics.requests)

                for idx, data_url in enumerate(tiles, start=1):
                    try:
                        got = ask_openai_for_numbers(
                            {"type": "image_url", "image_url": {"url": data_url}},
                            f"{req_id}#t{idx}",
                            client
                        )
                        for n in got:
                            numbers_set.add(n)
                    except Exception as e:
                        logger.warning(f"[{req_id}] Tile {idx} failed: {e}")

                successful_tiles = len(analytics.requests) - old_requests_len
                if successful_tiles == 0:
                    logger.error(f"[{req_id}] All tiles failed to process")
                    bot.send_message(message.chat.id, "Ошибка при обращении к OpenAI API. Попробуйте позже.")
                    return

            # Суммировать время и стоимость по обработанным тайлам
            total_time = 0.0
            cents = 0
            if successful_tiles > 0:
                recent_requests = analytics.requests[-successful_tiles:]
                total_time = sum(r.duration for r in recent_requests)
                total_cost = sum(r.cost_usd for r in recent_requests)
                cents = int(total_cost * 100)
                logger.info(f"[{req_id}] Total time: {total_time:.1f}s, cents: {cents}")

            numbers = sorted(numbers_set, key=lambda x: (len(x), x))
            logger.info(f"[{req_id}] Extracted numbers: {numbers}")
            if numbers:
                response_text = "Нашел следующие числа на схеме:\n\n" + format_numbers_readable(numbers)
                if successful_tiles > 0:
                    response_text += f"\n\nЗатрачено времени: {total_time:.1f} сек, затрата: {cents} центов"
                bot.send_message(message.chat.id, response_text)
                logger.info(f"[{req_id}] Successfully extracted {len(numbers)} numbers from {successful_tiles}/{len(tiles)} tiles")
            else:
                response_text = "К сожалению, не смог найти числа на этом изображении."
                if successful_tiles > 0:
                    response_text += f"\n\nЗатрачено времени: {total_time:.1f} сек, затрата: {cents} центов"
                bot.send_message(message.chat.id, response_text)
                logger.warning(f"[{req_id}] No numbers found after processing {successful_tiles}/{len(tiles)} tiles")

        except Exception as e:
            logger.exception(f"[{req_id}] Fatal error while handling photo: {e}")
            bot.send_message(message.chat.id, "Произошла неожиданная ошибка. Попробуйте отправить фото еще раз.")

    # Защита от нерелевантных сообщений
    @bot.message_handler(func=lambda m: True, content_types=['text', 'document', 'video', 'audio', 'sticker'])
    def fallback_handler(message):
        bot.reply_to(message, "Отправьте, пожалуйста, фото (jpeg/png/webp). Команды: /start, /stats.")

    return bot, logger


def run_bot():
    """Запуск бота с перезапуском при ошибках."""
    bot, logger = create_bot()
    
    logger.info("Bot starting...")
    print("Бот запущен...")

    # Устойчивый цикл polling с перезапуском при сетевых таймаутах
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=60, skip_pending=True)
            consecutive_errors = 0  # Сброс счетчика при успешном запуске
        except Exception as poll_err:
            consecutive_errors += 1
            error_msg = str(poll_err)
            
            # Специальная обработка для 409 ошибок (конфликт)
            if "409" in error_msg and "Conflict" in error_msg:
                logger.error(f"Bot conflict detected (409 error). Another bot instance may be running. Stopping this instance.")
                print("❌ Обнаружен конфликт ботов (409 ошибка). Возможно, запущен другой экземпляр бота.")
                break
            
            # Если слишком много ошибок подряд - останавливаем
            if consecutive_errors >= max_consecutive_errors:
                logger.error(f"Too many consecutive errors ({consecutive_errors}). Stopping bot.")
                print(f"❌ Слишком много ошибок подряд ({consecutive_errors}). Остановка бота.")
                break
                
            logger.warning(f"Polling crashed (attempt {consecutive_errors}/{max_consecutive_errors}): {poll_err}. Restarting in 5s...")
            time.sleep(5)
            continue


if __name__ == "__main__":
    run_bot()
