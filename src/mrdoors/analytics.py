"""Аналитика затрат времени и стоимости OpenAI запросов."""

import time
import json
import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Union, Optional, List
from dataclasses import dataclass

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@dataclass
class RequestStats:
    """Статистика одного запроса."""
    duration: float  # секунды
    input_tokens: int
    output_tokens: int
    cost_usd: float
    model: str
    request_id: Optional[str] = None
    chat_id: Optional[str] = None
    message_id: Optional[int] = None
    tile_id: Optional[str] = None
    status: str = "success"
    numbers: Optional[List[str]] = None
    raw_prompt: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None
    error_payload: Optional[Dict[str, Any]] = None
    originated_at: Optional[float] = None


class CostCalculator:
    """Калькулятор стоимости OpenAI API запросов."""
    
    # Цены в долларах за 1000 токенов (актуально на сентябрь 2024)
    PRICING = {
        'gpt-4o': {
            'input': 0.005,   # $0.005 за 1K input токенов
            'output': 0.015   # $0.015 за 1K output токенов
        },
        'gpt-4o-mini': {
            'input': 0.00015,  # $0.00015 за 1K input токенов
            'output': 0.0006   # $0.0006 за 1K output токенов
        }
    }
    
    @classmethod
    def calculate_cost(cls, model: str, input_tokens: int, output_tokens: int) -> float:
        """Рассчитать стоимость запроса в долларах."""
        if model not in cls.PRICING:
            # Используем цены gpt-4o как fallback для неизвестных моделей
            pricing = cls.PRICING['gpt-4o']
        else:
            pricing = cls.PRICING[model]
        
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost


class RequestAnalytics:
    """Сборщик аналитики запросов."""

    def __init__(self):
        self.lifetime_cost_usd = 0.0
        self.lifetime_requests = 0
        self.lifetime_input_tokens = 0
        self.lifetime_output_tokens = 0
        self.lifetime_duration = 0.0
        self.load_lifetime()
        self.reset_session()
    
    def load_lifetime(self):
        """Загрузить пожизненную статистику из файла."""
        try:
            if os.path.exists("logs/lifetime_stats.json"):
                with open("logs/lifetime_stats.json", "r") as f:
                    data = json.load(f)
                    self.lifetime_cost_usd = data.get("lifetime_cost_usd", 0.0)
                    self.lifetime_requests = data.get("lifetime_requests", 0)
                    self.lifetime_input_tokens = data.get("lifetime_input_tokens", 0)
                    self.lifetime_output_tokens = data.get("lifetime_output_tokens", 0)
                    self.lifetime_duration = data.get("lifetime_duration", 0.0)
        except Exception as e:
            print(f"Failed to load lifetime stats: {e}")
    
    def save_lifetime(self):
        """Сохранить пожизненную статистику в файл."""
        try:
            data = {
                "lifetime_cost_usd": self.lifetime_cost_usd,
                "lifetime_requests": self.lifetime_requests,
                "lifetime_input_tokens": self.lifetime_input_tokens,
                "lifetime_output_tokens": self.lifetime_output_tokens,
                "lifetime_duration": self.lifetime_duration
            }
            os.makedirs("logs", exist_ok=True)
            with open("logs/lifetime_stats.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save lifetime stats: {e}")
    
    def reset_session(self):
        """Сбросить статистику сессии."""
        self.requests = []
        self.session_start = time.time()
    
    def add_request(self, stats: RequestStats, extra: Optional[Dict[str, Any]] = None):
        """Добавить статистику запроса."""
        self.requests.append(stats)
        # Обновить пожизненную статистику
        self.lifetime_cost_usd += stats.cost_usd
        self.lifetime_requests += 1
        self.lifetime_input_tokens += stats.input_tokens
        self.lifetime_output_tokens += stats.output_tokens
        self.lifetime_duration += stats.duration
        self.save_lifetime()

        payload = {
            "request_id": stats.request_id or str(int(time.time() * 1000)),
            "originated_at": datetime.fromtimestamp(stats.originated_at or time.time(), tz=timezone.utc).isoformat(),
            "model": stats.model,
            "duration_seconds": stats.duration,
            "input_tokens": stats.input_tokens,
            "output_tokens": stats.output_tokens,
            "cost_usd": stats.cost_usd,
            "status": stats.status,
            "chat_id": stats.chat_id,
            "message_id": stats.message_id,
            "tile_id": stats.tile_id,
            "numbers": stats.numbers,
            "raw_prompt": stats.raw_prompt,
            "raw_response": stats.raw_response,
            "error_payload": stats.error_payload,
        }
        if extra:
            payload.update(extra)

        try:
            analytics_client.send_event(payload)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to send analytics event: %s", exc)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Получить сводку по текущей сессии."""
        if not self.requests:
            return {
                'total_requests': 0,
                'total_cost_usd': 0.0,
                'total_cost_cents': 0.0,
                'total_duration': 0.0,
                'average_duration': 0.0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_tokens': 0,
                'session_duration': time.time() - self.session_start,
                'lifetime_cost_usd': self.lifetime_cost_usd,
                'lifetime_requests': self.lifetime_requests,
                'lifetime_tokens': self.lifetime_input_tokens + self.lifetime_output_tokens
            }
        
        total_cost = sum(r.cost_usd for r in self.requests)
        total_duration = sum(r.duration for r in self.requests)
        total_input = sum(r.input_tokens for r in self.requests)
        total_output = sum(r.output_tokens for r in self.requests)
        
        return {
            'total_requests': len(self.requests),
            'total_cost_usd': total_cost,
            'total_cost_cents': total_cost * 100,
            'total_duration': total_duration,
            'average_duration': total_duration / len(self.requests),
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
            'total_tokens': total_input + total_output,
            'session_duration': time.time() - self.session_start,
            'cost_per_request': total_cost / len(self.requests) if self.requests else 0.0,
            'lifetime_cost_usd': self.lifetime_cost_usd,
            'lifetime_requests': self.lifetime_requests,
            'lifetime_tokens': self.lifetime_input_tokens + self.lifetime_output_tokens
        }
    
    def format_summary(self, summary: Dict[str, Any]) -> str:
        """Отформатировать сводку для логов."""
        text = (
            f"📊 Статистика сессии:\n"
            f"  {summary['total_requests']} запросов, "
            f"{summary['total_duration']:.1f}с, "
            f"${summary['total_cost_usd']:.4f} ({summary['total_cost_cents']:.2f}¢), "
            f"{summary['total_tokens']} токенов"
        )
        if summary['lifetime_requests'] > 0:
            text += (
                f"\n📈 Всего за все время:\n"
                f"  {summary['lifetime_requests']} запросов, "
                f"${summary['lifetime_cost_usd']:.4f}, "
                f"{summary['lifetime_tokens']} токенов"
            )
        return text


# Глобальный экземпляр аналитики
analytics = RequestAnalytics()


class AnalyticsClient:
    """Клиент для отправки событий аналитики на внешний сервис."""

    def __init__(self):
        base_url = os.getenv("ANALYTICS_API_URL")
        token = os.getenv("ANALYTICS_API_TOKEN")
        self.enabled = bool(base_url)
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.token = token
        self._client: Optional[httpx.Client] = None

    def _get_client(self) -> httpx.Client:
        if not self._client:
            self._client = httpx.Client(base_url=self.base_url, timeout=5.0)
        return self._client

    def close(self):
        if self._client:
            self._client.close()
            self._client = None

    @retry(wait=wait_exponential(multiplier=0.4, min=0.5, max=5), stop=stop_after_attempt(3))
    def send_event(self, payload: Dict[str, Any]):
        if not self.enabled:
            return
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        client = self._get_client()
        response = client.post("/api/v1/ingestion/events", json=payload, headers=headers)
        response.raise_for_status()


analytics_client = AnalyticsClient()
