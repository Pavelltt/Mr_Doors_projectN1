"""Конфигурация приложения."""

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv('BOT_TOKEN')

# OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PREFERRED_MODEL = os.getenv('OPENAI_VISION_MODEL', 'gpt-4o')
OPENAI_TIMEOUT = float(os.getenv('OPENAI_TIMEOUT', '45'))
OPENAI_RETRIES = int(os.getenv('OPENAI_RETRIES', '2'))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Validation
if not BOT_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не задана. Создайте .env и укажите BOT_TOKEN=<ваш токен>.")
if not OPENAI_API_KEY:
    raise ValueError("Переменная окружения OPENAI_API_KEY не задана. Создайте .env и укажите OPENAI_API_KEY=<ваш ключ>.")
