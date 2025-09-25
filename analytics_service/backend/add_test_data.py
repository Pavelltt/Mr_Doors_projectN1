import sqlite3
import json
from datetime import datetime, timedelta
import random
import uuid

# Подключение к базе данных
conn = sqlite3.connect('analytics.db')
cursor = conn.cursor()

# Модели для тестирования
models = ['gpt-4o-mini', 'gpt-4o', 'claude-3-sonnet', 'claude-3-haiku']
statuses = ['SUCCESS', 'ERROR', 'PARTIAL']

# Генерация тестовых данных за последние 30 дней
base_date = datetime.now() - timedelta(days=30)

for i in range(100):  # Создаем 100 записей
    originated_at = base_date + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    
    model = random.choice(models)
    status = random.choice(statuses)
    
    # Разные параметры в зависимости от модели
    if 'gpt-4o-mini' in model:
        input_tokens = random.randint(50, 500)
        output_tokens = random.randint(20, 200)
        cost_per_token = 0.00015
    elif 'gpt-4o' in model:
        input_tokens = random.randint(100, 1000)
        output_tokens = random.randint(50, 400)
        cost_per_token = 0.003
    elif 'claude-3-sonnet' in model:
        input_tokens = random.randint(80, 800)
        output_tokens = random.randint(40, 300)
        cost_per_token = 0.003
    else:  # claude-3-haiku
        input_tokens = random.randint(30, 300)
        output_tokens = random.randint(15, 150)
        cost_per_token = 0.00025
    
    cost_usd = (input_tokens + output_tokens) * cost_per_token
    duration_seconds = random.uniform(0.5, 5.0)
    
    cursor.execute('''
        INSERT INTO request_events (
            request_id, originated_at, chat_id, message_id, tile_id,
            model, duration_seconds, input_tokens, output_tokens,
            cost_usd, status, numbers, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        str(uuid.uuid4()),
        originated_at.isoformat(),
        f'chat_{random.randint(1000, 9999)}',
        random.randint(1, 1000),
        f'tile_{random.randint(100, 999)}',
        model,
        duration_seconds,
        input_tokens,
        output_tokens,
        cost_usd,
        status,
        json.dumps([str(random.randint(1, 100)) for _ in range(random.randint(1, 5))]),
        datetime.now().isoformat()
    ))

conn.commit()
conn.close()
print('Добавлено 100 тестовых записей в базу данных')