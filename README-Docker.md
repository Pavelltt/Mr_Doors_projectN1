# MrDoors Docker Deployment Guide

Этот проект полностью контейнеризован с использованием Docker и Docker Compose для легкого развертывания на сервере.

## Архитектура

Проект состоит из следующих сервисов:
- **PostgreSQL** - База данных
- **Backend** - FastAPI сервис аналитики
- **Frontend** - React приложение (аналитическая панель)
- **Telegram Bot** - Основной бот для обработки сообщений
- **Nginx** - Reverse proxy (только для production)

## Быстрый старт (Development)

1. **Клонируйте репозиторий и перейдите в директорию:**
   ```bash
   cd Mr_Doors_app
   ```

2. **Создайте файл .env из шаблона:**
   ```bash
   cp .env.production .env
   ```

3. **Заполните переменные окружения в .env:**
   ```bash
   # Обязательные переменные
   BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   POSTGRES_PASSWORD=your_secure_password
   ```

4. **Запустите все сервисы:**
   ```bash
   docker-compose up -d
   ```

5. **Проверьте статус сервисов:**
   ```bash
   docker-compose ps
   ```

## Production развертывание

### 1. Подготовка сервера

```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установите Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER
```

### 2. Настройка переменных окружения

Создайте файл `.env` с production настройками:

```bash
# Telegram Bot Configuration
BOT_TOKEN=your_real_bot_token

# OpenAI Configuration
OPENAI_API_KEY=your_real_openai_api_key
OPENAI_VISION_MODEL=gpt-4o
OPENAI_TIMEOUT=45
OPENAI_RETRIES=2

# Database Configuration
POSTGRES_PASSWORD=very_secure_password_here

# SSL Configuration (для production)
DOMAIN=yourdomain.com
SSL_EMAIL=your-email@domain.com
CORS_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO
```

### 3. Запуск production версии

```bash
# Запуск без SSL (для начального тестирования)
docker-compose -f docker-compose.prod.yml up -d

# Или с SSL сертификатами
docker-compose -f docker-compose.prod.yml --profile ssl up -d
```

### 4. Настройка SSL (Let's Encrypt)

```bash
# Получите SSL сертификат
docker-compose -f docker-compose.prod.yml run --rm certbot

# Настройте автоматическое обновление
echo "0 12 * * * /usr/local/bin/docker-compose -f /path/to/your/docker-compose.prod.yml run --rm certbot renew" | sudo crontab -
```

## Полезные команды

### Мониторинг

```bash
# Просмотр логов всех сервисов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f telegram_bot
docker-compose logs -f backend
docker-compose logs -f frontend

# Проверка статуса
docker-compose ps
```

### Управление

```bash
# Остановка всех сервисов
docker-compose down

# Остановка с удалением volumes (ОСТОРОЖНО!)
docker-compose down -v

# Перезапуск конкретного сервиса
docker-compose restart telegram_bot

# Обновление образов
docker-compose pull
docker-compose up -d
```

### Резервное копирование

```bash
# Создание бэкапа базы данных
docker-compose exec postgres pg_dump -U postgres mrdoors > backup.sql

# Восстановление из бэкапа
docker-compose exec -T postgres psql -U postgres mrdoors < backup.sql
```

## Доступ к сервисам

После запуска сервисы будут доступны по следующим адресам:

- **Frontend (Analytics Dashboard)**: http://localhost (или https://yourdomain.com)
- **Backend API**: http://localhost/api (или https://yourdomain.com/api)
- **API Documentation**: http://localhost/api/docs
- **Health Check**: http://localhost/health

## Troubleshooting

### Проблемы с запуском

1. **Проверьте логи:**
   ```bash
   docker-compose logs
   ```

2. **Проверьте доступность портов:**
   ```bash
   sudo netstat -tlnp | grep :80
   sudo netstat -tlnp | grep :443
   ```

3. **Проверьте переменные окружения:**
   ```bash
   docker-compose config
   ```

### Проблемы с базой данных

1. **Проверьте подключение к PostgreSQL:**
   ```bash
   docker-compose exec postgres psql -U postgres -c "SELECT version();"
   ```

2. **Сброс базы данных (ОСТОРОЖНО!):**
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

### Проблемы с SSL

1. **Проверьте DNS записи:**
   ```bash
   nslookup yourdomain.com
   ```

2. **Проверьте доступность порта 80 для Let's Encrypt:**
   ```bash
   curl -I http://yourdomain.com/.well-known/acme-challenge/test
   ```

## Масштабирование

Для увеличения производительности можно:

1. **Масштабировать backend:**
   ```bash
   docker-compose up -d --scale backend=3
   ```

2. **Добавить мониторинг (Prometheus + Grafana)**
3. **Настроить load balancer**
4. **Использовать внешнюю базу данных**

## Безопасность

1. **Регулярно обновляйте образы:**
   ```bash
   docker-compose pull && docker-compose up -d
   ```

2. **Используйте сильные пароли**
3. **Настройте firewall:**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

4. **Мониторьте логи на подозрительную активность**