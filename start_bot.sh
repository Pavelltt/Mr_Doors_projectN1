#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 Запуск Telegram бота Mr. Doors...${NC}"

# Активируем виртуальное окружение
echo -e "${YELLOW}📦 Активирую виртуальное окружение...${NC}"
source .venv/bin/activate

# Проверяем статус бота
echo -e "${YELLOW}🔍 Проверяю статус бота...${NC}"
STATUS_OUTPUT=$(.venv/bin/python bot_manager.py status 2>&1)
echo "$STATUS_OUTPUT"

if echo "$STATUS_OUTPUT" | grep -q "Бот запущен"; then
    echo -e "${YELLOW}⚠️  Бот уже запущен. Перезапускаю...${NC}"
    .venv/bin/python bot_manager.py restart
    RESULT=$?
else
    echo -e "${YELLOW}🚀 Запускаю бота...${NC}"
    .venv/bin/python bot_manager.py start
    RESULT=$?
fi

if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Бот успешно запущен!${NC}"
    echo -e "${BLUE}📋 Доступные команды:${NC}"
    echo -e "  ${YELLOW}Остановить:${NC} .venv/bin/python bot_manager.py stop"
    echo -e "  ${YELLOW}Перезапустить:${NC} .venv/bin/python bot_manager.py restart"
    echo -e "  ${YELLOW}Статус:${NC} .venv/bin/python bot_manager.py status"
else
    echo -e "${RED}❌ Ошибка при запуске бота!${NC}"
    exit 1
fi