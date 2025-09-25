#!/usr/bin/env python3
"""
Менеджер для безопасного запуска и управления Telegram ботом.
Предотвращает запуск нескольких экземпляров одновременно.
"""

import os
import sys
import time
import signal
import psutil
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Настройка логирования с ротацией
os.makedirs("logs", exist_ok=True)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Создаем форматтер
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

# Консольный обработчик
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Файловый обработчик с ротацией (максимум 5MB, 3 файла)
file_handler = RotatingFileHandler(
    'logs/bot_manager.log', 
    maxBytes=5*1024*1024,  # 5MB
    backupCount=3,
    encoding='utf-8'
)
file_handler.setFormatter(formatter)

# Добавляем обработчики только если они еще не добавлены
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

class BotManager:
    def __init__(self):
        self.pid_file = Path("logs/bot.pid")
        self.bot_process = None
        
    def is_bot_running(self):
        """Проверяет, запущен ли бот."""
        if not self.pid_file.exists():
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Проверяем, существует ли процесс
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                # Проверяем, что это действительно наш бот
                if 'python' in proc.name().lower() and any('main.py' in arg or 'bot.py' in arg for arg in proc.cmdline()):
                    return True
            
            # Если процесс не найден, удаляем pid файл
            self.pid_file.unlink()
            return False
            
        except (ValueError, psutil.NoSuchProcess, PermissionError):
            # Если не можем прочитать pid или процесс не существует
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False
    
    def kill_existing_bots(self):
        """Завершает все запущенные экземпляры бота."""
        killed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline'] or []
                    if any('main.py' in arg or 'bot.py' in arg for arg in cmdline):
                        logger.info(f"Завершаю процесс бота: PID {proc.info['pid']}")
                        proc.terminate()
                        killed_count += 1
                        
                        # Ждем завершения процесса
                        try:
                            proc.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            logger.warning(f"Принудительно завершаю процесс: PID {proc.info['pid']}")
                            proc.kill()
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if killed_count > 0:
            logger.info(f"Завершено {killed_count} процессов бота")
            time.sleep(2)  # Даем время на очистку ресурсов
        
        # Очищаем pid файл
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def start_bot(self):
        """Запускает бота."""
        # Создаем директорию для логов
        os.makedirs("logs", exist_ok=True)
        
        # Проверяем, не запущен ли уже бот
        if self.is_bot_running():
            logger.warning("Бот уже запущен! Используйте 'stop' для остановки или 'restart' для перезапуска.")
            return False
        
        # Завершаем все существующие процессы бота
        self.kill_existing_bots()
        
        logger.info("Запускаю бота...")
        
        # Запускаем бота
        import subprocess
        try:
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Сохраняем PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            logger.info(f"Бот запущен с PID: {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
            return False
    
    def stop_bot(self):
        """Останавливает бота."""
        if not self.is_bot_running():
            logger.info("Бот не запущен")
            return True
        
        logger.info("Останавливаю бота...")
        self.kill_existing_bots()
        logger.info("Бот остановлен")
        return True
    
    def restart_bot(self):
        """Перезапускает бота."""
        logger.info("Перезапускаю бота...")
        self.stop_bot()
        time.sleep(1)
        return self.start_bot()
    
    def status(self, silent=False):
        """Показывает статус бота."""
        if self.is_bot_running():
            with open(self.pid_file, 'r') as f:
                pid = f.read().strip()
            if not silent:
                logger.info(f"Бот запущен (PID: {pid})")
            return True, pid
        else:
            if not silent:
                logger.info("Бот не запущен")
            return False, None

def main():
    manager = BotManager()
    
    if len(sys.argv) < 2:
        print("Использование: python bot_manager.py [start|stop|restart|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        success = manager.start_bot()
        sys.exit(0 if success else 1)
    elif command == "stop":
        success = manager.stop_bot()
        sys.exit(0 if success else 1)
    elif command == "restart":
        success = manager.restart_bot()
        sys.exit(0 if success else 1)
    elif command == "status":
        manager.status()
        sys.exit(0)
    else:
        print("Неизвестная команда. Используйте: start, stop, restart, status")
        sys.exit(1)

if __name__ == "__main__":
    main()