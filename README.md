# Mr_Doors_app

Telegram-бот для автоматического распознавания чисел на технических схемах и чертежах замеров дверей с использованием OpenAI Vision API.

## Возможности

- 📷 Обработка изображений через Telegram
- 🔍 Извлечение числовых значений с технических чертежей
- 🤖 Использование OpenAI Vision API (GPT-4V)
- 🔧 Предварительная обработка изображений для улучшения OCR
- 📊 Разбиение изображений на тайлы для повышения точности
- 📋 Fallback механизм через регулярные выражения
- 📝 Подробное логирование операций

## Требования

- Python 3.8+
- Telegram Bot Token
- OpenAI API Key
- Виртуальное окружение (рекомендуется)

## Установка

1. **Клонирование репозитория:**
```bash
git clone https://github.com/Pavelltt/Mr_Doors_app.git
cd Mr_Doors_app
```

2. **Создание виртуального окружения:**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows
```

3. **Установка зависимостей:**
```bash
pip install -r requirements.txt
```

4. **Настройка переменных окружения:**
```bash
cp .env.example .env
```

Отредактируйте файл `.env` и заполните необходимые переменные:
```bash
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_VISION_MODEL=gpt-4o
OPENAI_TIMEOUT=45
OPENAI_RETRIES=2

# Logging
LOG_LEVEL=INFO
```

## Получение токенов

### Telegram Bot Token
1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен

### OpenAI API Key
1. Зарегистрируйтесь на [OpenAI Platform](https://platform.openai.com/)
2. Перейдите в раздел [API Keys](https://platform.openai.com/api-keys)
3. Создайте новый API ключ
4. Скопируйте ключ (он показывается только один раз)

## Запуск

### Основной способ:
```bash
python main.py
```

### Альтернативный способ:
```bash
python -m src.mrdoors.bot
```

## Использование

1. Запустите бота командой выше
2. Найдите своего бота в Telegram
3. Отправьте команду `/start`
4. Отправьте фото схемы или чертежа
5. Получите список найденных чисел

## Структура проекта

```
Mr_Doors_app/
├── src/
│   └── mrdoors/
│       ├── __init__.py
│       ├── bot.py          # Основная логика бота
│       ├── config.py       # Конфигурация
│       └── utils.py        # Утилиты обработки изображений
├── tests/
│   ├── test_extract_numbers.py
│   └── test_integration_openai.py
├── logs/                   # Директория логов
├── main.py                 # Точка входа
├── requirements.txt
├── .env.example
└── README.md
```

## Тестирование

Запуск всех тестов:
```bash
pytest
```

Запуск только unit тестов:
```bash
pytest tests/test_extract_numbers.py
```

Запуск интеграционных тестов (требует API ключ):
```bash
pytest tests/test_integration_openai.py -m integration
```

## Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `BOT_TOKEN` | Токен Telegram бота | Обязательно |
| `OPENAI_API_KEY` | API ключ OpenAI | Обязательно |
| `OPENAI_VISION_MODEL` | Модель OpenAI для Vision | `gpt-4o` |
| `OPENAI_TIMEOUT` | Таймаут запросов к OpenAI | `45` |
| `OPENAI_RETRIES` | Количество повторов запросов | `2` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |

### Обработка изображений

- Максимальный размер изображения: 2000px
- Разбиение на тайлы: 2x3 (6 частей)
- Поддерживаемые форматы: JPEG, PNG,
