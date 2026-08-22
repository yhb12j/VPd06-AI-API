"""Модуль для работы с AI-моделями через ProxyAPI."""

import logging
from typing import Any

import anthropic
from anthropic import Anthropic
from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError

from text_agent.config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_BASE_URL,
    ANTHROPIC_MODEL,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    REQUEST_TIMEOUT,
    SYSTEM_PROMPT,
    THINKING_BUDGET_TOKENS,
)

logger = logging.getLogger(__name__)


class TextAgent:
    """Консольный текстовый агент с поддержкой обычного и думающего режимов."""

    MODE_REGULAR = "regular"
    MODE_THINKING = "thinking"

    def __init__(self, mode: str = MODE_THINKING) -> None:
        if mode not in (self.MODE_REGULAR, self.MODE_THINKING):
            raise ValueError(f"Неизвестный режим: {mode}")

        self.mode = mode
        self.system_prompt = SYSTEM_PROMPT
        self.conversation_history: list[dict[str, Any]] = []

        if mode == self.MODE_REGULAR:
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY не задан в .env")
            self._openai_client = OpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL,
                timeout=REQUEST_TIMEOUT,
            )
        else:
            if not ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY не задан в .env")
            self._anthropic_client = Anthropic(
                api_key=ANTHROPIC_API_KEY,
                base_url=ANTHROPIC_BASE_URL,
                timeout=REQUEST_TIMEOUT,
            )

    @property
    def model_name(self) -> str:
        if self.mode == self.MODE_REGULAR:
            return OPENAI_MODEL
        return ANTHROPIC_MODEL

    def generate_response(self, user_message: str) -> str:
        """Отправляет сообщение в модель и возвращает текст ответа."""
        user_message = user_message.strip()
        if not user_message:
            raise ValueError("Сообщение не может быть пустым")

        if self.mode == self.MODE_REGULAR:
            return self._generate_openai(user_message)
        return self._generate_anthropic(user_message)

    def _generate_openai(self, user_message: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})

        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history)

        try:
            response = self._openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
            )
        except APITimeoutError as exc:
            self.conversation_history.pop()
            logger.error("Таймаут запроса к OpenAI API")
            raise TimeoutError("Превышено время ожидания ответа от модели") from exc
        except APIConnectionError as exc:
            self.conversation_history.pop()
            logger.error("Ошибка соединения с OpenAI API: %s", exc)
            raise ConnectionError("Не удалось подключиться к API") from exc
        except RateLimitError as exc:
            self.conversation_history.pop()
            logger.error("Превышен лимит запросов: %s", exc)
            raise RuntimeError("Превышен лимит запросов к API") from exc
        except Exception as exc:
            self.conversation_history.pop()
            logger.error("Ошибка OpenAI API: %s", exc)
            raise RuntimeError(f"Ошибка API: {exc}") from exc

        assistant_message = response.choices[0].message.content or ""
        self.conversation_history.append(
            {"role": "assistant", "content": assistant_message}
        )

        usage = response.usage
        if usage:
            logger.info(
                "Токены — вход: %s, выход: %s, всего: %s",
                usage.prompt_tokens,
                usage.completion_tokens,
                usage.total_tokens,
            )

        return assistant_message

    def _generate_anthropic(self, user_message: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})

        try:
            response = self._anthropic_client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=4096,
                system=self.system_prompt,
                thinking={
                    "type": "enabled",
                    "budget_tokens": THINKING_BUDGET_TOKENS,
                },
                messages=self.conversation_history,
            )
        except anthropic.APITimeoutError as exc:
            self.conversation_history.pop()
            logger.error("Таймаут запроса к Anthropic API")
            raise TimeoutError("Превышено время ожидания ответа от модели") from exc
        except anthropic.APIConnectionError as exc:
            self.conversation_history.pop()
            logger.error("Ошибка соединения с Anthropic API: %s", exc)
            raise ConnectionError("Не удалось подключиться к API") from exc
        except anthropic.RateLimitError as exc:
            self.conversation_history.pop()
            logger.error("Превышен лимит запросов: %s", exc)
            raise RuntimeError("Превышен лимит запросов к API") from exc
        except Exception as exc:
            self.conversation_history.pop()
            logger.error("Ошибка Anthropic API: %s", exc)
            raise RuntimeError(f"Ошибка API: {exc}") from exc

        self._print_thinking_response(response)

        assistant_text = ""
        assistant_content: list[dict[str, Any]] = []

        for block in response.content:
            block_type = getattr(block, "type", None)
            if block_type == "thinking":
                thinking_block: dict[str, Any] = {
                    "type": "thinking",
                    "thinking": block.thinking,
                }
                signature = getattr(block, "signature", None)
                if signature:
                    thinking_block["signature"] = signature
                assistant_content.append(thinking_block)
            elif block_type == "text":
                assistant_text = block.text
                assistant_content.append({"type": "text", "text": block.text})

        self.conversation_history.append(
            {"role": "assistant", "content": assistant_content}
        )

        return assistant_text

    def _print_thinking_response(self, response: Any) -> None:
        """Красивый вывод размышлений и метрик использования."""
        print("\n" + "=" * 60)
        print("РЕЖИМ REASONING (Claude Extended Thinking)")
        print("=" * 60)

        for block in response.content:
            block_type = getattr(block, "type", None)
            if block_type == "thinking":
                print("\n--- Размышления модели ---")
                print(block.thinking)
            elif block_type == "text":
                print("\n--- Ответ ---")
                print(block.text)

        usage = response.usage
        if usage:
            print("\n--- Использование токенов ---")
            print(f"  Входные токены:  {usage.input_tokens}")
            print(f"  Выходные токены: {usage.output_tokens}")

            cache_read = getattr(usage, "cache_read_input_tokens", None)
            cache_creation = getattr(usage, "cache_creation_input_tokens", None)
            if cache_read:
                print(f"  Cache read:      {cache_read}")
            if cache_creation:
                print(f"  Cache creation:  {cache_creation}")

        print("=" * 60 + "\n")

    def get_history_display(self) -> str:
        """Форматирует историю диалога для вывода при выходе."""
        if not self.conversation_history:
            return "История диалога пуста."

        lines = ["\n" + "=" * 60, "ИСТОРИЯ ДИАЛОГА", "=" * 60]

        for message in self.conversation_history:
            role = "Вы" if message["role"] == "user" else "Ассистент"
            content = message["content"]

            if isinstance(content, list):
                text_parts = [
                    block.get("text", block.get("thinking", ""))
                    for block in content
                    if block.get("type") in ("text", "thinking")
                ]
                content = "\n".join(part for part in text_parts if part)
            elif not content:
                content = "(пусто)"

            lines.append(f"\n[{role}]")
            lines.append(str(content))

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
