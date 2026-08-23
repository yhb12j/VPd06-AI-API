# AI API (OpenAI / Claude через ProxyAPI)

Консольный текстовый помощник на Python с подключением к [ProxyAPI](https://proxyapi.ru/).

## Возможности

- Диалог с сохранением контекста между сообщениями
- **Режим 1 (по умолчанию):** Claude 4.5 Sonnet с Extended Thinking — видны размышления модели и метрики токенов
- **Режим 2:** OpenAI Chat Completions (`gpt-4o-mini`) через ProxyAPI
- Конфигурация через `.env`
- Обработка ошибок API, таймаутов и понятные логи запуска

## Требования

- Python 3.10+
- API-ключ [ProxyAPI](https://proxyapi.ru/)

## Установка

```bash
# 1. Клонировать репозиторий
git clone <url-вашего-репозитория>
cd "VPd06 Ai API"

# 2. Создать виртуальное окружение
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить переменные окружения
copy .env.example .env   # Windows
# cp .env.example .env   # Linux / macOS
```

Откройте `.env` и вставьте свой ключ ProxyAPI:

```env
OPENAI_API_KEY=ваш_ключ_от_proxyapi
ANTHROPIC_API_KEY=ваш_ключ_от_proxyapi
```

> Один и тот же ключ ProxyAPI подходит для обоих режимов.

## Запуск

```bash
python textagent.py
```

При старте выберите режим:

| Выбор | Режим | Модель |
|-------|-------|--------|
| `1` или Enter | Думающий | Claude 4.5 Sonnet + reasoning |
| `2` | Обычный | GPT-4o mini |

### Команды в диалоге

- `exit`, `quit`, `выход` — завершить сессию и показать историю

## Структура проекта

```
VPd06 Ai API/
├── textagent.py          # Точка входа, консольный интерфейс
├── text_agent/
│   ├── agent.py          # Класс TextAgent, логика API
│   └── config.py         # Загрузка настроек из .env
├── requirements.txt
├── .env.example
└── README.md
```

## Домашнее задание (VPd06)

Реализовано:

- [x] Консольный ассистент через ProxyAPI
- [x] Хранение и подгрузка истории диалога
- [x] Переключение между обычной и думающей моделью
- [x] Отображение reasoning (Claude Extended Thinking)
- [x] Конфигурация через `.env`
- [x] Обработка ошибок и таймаутов
- [x] Понятные логи запуска

## Полезные ссылки

- [ProxyAPI — документация](https://proxyapi.ru/docs)
- [OpenAI Chat Completions через ProxyAPI](https://proxyapi.ru/docs/openai-text-generation)
- [Anthropic через ProxyAPI](https://proxyapi.ru/docs/anthropic-text-generation)
