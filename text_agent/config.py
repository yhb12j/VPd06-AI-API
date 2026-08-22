"""Загрузка конфигурации из переменных окружения."""

import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", OPENAI_API_KEY)
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.proxyapi.ru/openai/v1")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.proxyapi.ru/anthropic")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
THINKING_BUDGET_TOKENS = int(os.getenv("THINKING_BUDGET_TOKENS", "1500"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "60"))
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "Вы полезный ассистент, отвечайте на русском языке.",
)
