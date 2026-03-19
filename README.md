# Telegram bot для генерации паролей

Простой Telegram-бот на Python, который генерирует случайные надёжные пароли и умеет запускаться без сторонних Telegram-библиотек.

## Возможности

- генерация паролей длиной от 4 до 64 символов;
- режимы `all`, `nosymbols`, `digits`, `letters`, `letters-digits`;
- безопасная генерация через модуль `secrets`;
- автозагрузка токена из `.env`;
- автоматическая регистрация команд в интерфейсе Telegram.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Создай бота через [@BotFather](https://t.me/BotFather), получи токен и вставь его в `.env`:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

## Запуск

```bash
python bot.py
```

Бот автоматически прочитает `.env` из корня проекта. Можно также передать токен через переменную окружения `TELEGRAM_BOT_TOKEN`.

## Команды

- `/start` — приветствие;
- `/help` — справка;
- `/generate` — пароль на 16 символов;
- `/generate 24` — пароль на 24 символа;
- `/generate 20 nosymbols` — без спецсимволов;
- `/generate 12 digits` — только цифры;
- `/generate 18 letters` — только буквы;
- `/generate 18 letters-digits` — буквы и цифры.

## Примеры

```text
/generate
/generate 24
/generate 16 nosymbols
/generate 12 digits
/generate 18 letters-digits
```

## Тесты

```bash
pytest
```
