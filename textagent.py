"""Консольный текстовый помощник с ProxyAPI (OpenAI / Claude)."""

import logging
import sys

from text_agent.agent import TextAgent
from text_agent.config import (
    ANTHROPIC_BASE_URL,
    ANTHROPIC_MODEL,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    THINKING_BUDGET_TOKENS,
)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def choose_mode() -> str:
    """Выбор режима работы при запуске."""
    print("\n" + "=" * 60)
    print("  ТЕКСТОВЫЙ AI-ПОМОЩНИК (ProxyAPI)")
    print("=" * 60)
    print("\nВыберите режим работы:")
    print("  1 — Думающая модель (Claude 4.5 Sonnet + reasoning) [по умолчанию]")
    print("  2 — Обычная модель (OpenAI Chat Completions)")
    print()

    while True:
        choice = input("Ваш выбор (Enter = 1): ").strip()

        if choice in ("", "1"):
            return TextAgent.MODE_THINKING
        if choice == "2":
            return TextAgent.MODE_REGULAR

        print("Неверный выбор. Введите 1 или 2.")


def print_startup_info(mode: str) -> None:
    """Понятные логи запуска."""
    logger = logging.getLogger(__name__)

    if mode == TextAgent.MODE_THINKING:
        logger.info("Режим: думающая модель (Anthropic Extended Thinking)")
        logger.info("Модель: %s", ANTHROPIC_MODEL)
        logger.info("Base URL: %s", ANTHROPIC_BASE_URL)
        logger.info("Бюджет reasoning: %s токенов", THINKING_BUDGET_TOKENS)
    else:
        logger.info("Режим: обычная модель (OpenAI Chat Completions)")
        logger.info("Модель: %s", OPENAI_MODEL)
        logger.info("Base URL: %s", OPENAI_BASE_URL)

    print("\nКоманды:")
    print("  exit — завершить диалог и показать историю")
    print("  quit — то же самое")
    print("-" * 60)


def run_chat(agent: TextAgent) -> None:
    """Основной цикл диалога."""
    while True:
        try:
            user_input = input("\nВы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nПрерывание. Завершение работы...")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "выход"):
            print(agent.get_history_display())
            print("До свидания!")
            break

        try:
            if agent.mode == TextAgent.MODE_REGULAR:
                response = agent.generate_response(user_input)
                print(f"\nАссистент: {response}")
            else:
                agent.generate_response(user_input)
        except (TimeoutError, ConnectionError, RuntimeError, ValueError) as exc:
            print(f"\n[Ошибка] {exc}")
        except Exception as exc:
            logging.getLogger(__name__).exception("Неожиданная ошибка")
            print(f"\n[Ошибка] Неожиданная ошибка: {exc}")


def main() -> None:
    setup_logging()

    try:
        mode = choose_mode()
        print_startup_info(mode)
        agent = TextAgent(mode=mode)
    except ValueError as exc:
        print(f"\n[Ошибка конфигурации] {exc}")
        print("Создайте файл .env на основе .env.example и укажите API-ключ.")
        sys.exit(1)

    run_chat(agent)


if __name__ == "__main__":
    main()
