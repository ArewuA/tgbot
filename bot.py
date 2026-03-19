from __future__ import annotations

import json
import logging
import os
from pathlib import Path
import time
import urllib.request
from typing import Any, Sequence

from password_generator import PasswordGenerationError, PasswordOptions, generate_password

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DEFAULT_LENGTH = 16
MAX_LENGTH = 64
HELP_TEXT = """
Я умею генерировать надёжные пароли.

Команды:
/start — приветствие
/help — показать эту справку
/generate — сгенерировать пароль длиной 16 символов
/generate 24 — пароль длиной 24 символа
/generate 20 nosymbols — без спецсимволов
/generate 12 digits — только цифры
/generate 18 letters-digits — буквы и цифры

Доступные режимы:
- all — буквы, цифры и символы
- nosymbols — буквы и цифры
- digits — только цифры
- letters — только буквы
- letters-digits — буквы и цифры
""".strip()

BOT_COMMANDS = [
    {"command": "start", "description": "Приветствие и краткая инструкция"},
    {"command": "help", "description": "Показать все доступные команды"},
    {"command": "generate", "description": "Сгенерировать пароль"},
]


class TelegramBot:
    def __init__(self, token: str) -> None:
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.offset = 0

    def api_call(self, method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url=f"{self.base_url}/{method}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=70) as response:
            return json.loads(response.read().decode("utf-8"))

    def get_updates(self, timeout: int = 30) -> list[dict[str, Any]]:
        response = self.api_call(
            "getUpdates",
            {"offset": self.offset, "timeout": timeout, "allowed_updates": ["message"]},
        )
        return response.get("result", [])

    def send_message(self, chat_id: int, text: str) -> None:
        self.api_call(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            },
        )

    def set_commands(self) -> None:
        self.api_call("setMyCommands", {"commands": BOT_COMMANDS})



def load_env_file(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", maxsplit=1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)



def parse_mode(mode: str, length: int) -> PasswordOptions:
    normalized = mode.lower().strip()

    if normalized == "all":
        return PasswordOptions(length=length)
    if normalized == "nosymbols":
        return PasswordOptions(length=length, use_symbols=False)
    if normalized == "digits":
        return PasswordOptions(
            length=length,
            use_uppercase=False,
            use_lowercase=False,
            use_digits=True,
            use_symbols=False,
        )
    if normalized == "letters":
        return PasswordOptions(
            length=length,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=False,
            use_symbols=False,
        )
    if normalized == "letters-digits":
        return PasswordOptions(
            length=length,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_symbols=False,
        )

    raise PasswordGenerationError(
        "Неизвестный режим. Используй: all, nosymbols, digits, letters, letters-digits."
    )



def parse_args(args: Sequence[str]) -> PasswordOptions:
    length = DEFAULT_LENGTH
    mode = "all"

    if len(args) >= 1 and args[0]:
        try:
            length = int(args[0])
        except ValueError as error:
            raise PasswordGenerationError(
                "Первый аргумент должен быть числом, например /generate 20"
            ) from error

    if len(args) >= 2:
        mode = args[1]

    if length > MAX_LENGTH:
        raise PasswordGenerationError(f"Максимальная длина пароля — {MAX_LENGTH} символа.")

    return parse_mode(mode, length)



def handle_command(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return "Отправь команду /generate, чтобы получить пароль."

    command, *args = stripped.split()
    command = command.split("@", maxsplit=1)[0].lower()

    if command == "/start":
        return "Привет! Я бот для генерации паролей. Используй /generate 16 или /help."
    if command == "/help":
        return HELP_TEXT
    if command == "/generate":
        try:
            options = parse_args(args)
            password = generate_password(options)
            return f"🔐 <b>Ваш пароль:</b>\n<code>{html_escape(password)}</code>"
        except PasswordGenerationError as error:
            return f"Ошибка: {error}\n\n{HELP_TEXT}"

    return "Я понимаю только команды /start, /help и /generate."



def html_escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")



def extract_message(update: dict[str, Any]) -> tuple[int, str] | None:
    message = update.get("message") or {}
    text = message.get("text")
    chat = message.get("chat") or {}
    chat_id = chat.get("id")

    if not text or chat_id is None:
        return None

    return chat_id, text.strip()



def main() -> None:
    load_env_file()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Переменная окружения TELEGRAM_BOT_TOKEN не задана.")

    bot = TelegramBot(token)
    bot.set_commands()
    logger.info("Bot started")

    while True:
        try:
            updates = bot.get_updates()
            for update in updates:
                bot.offset = update["update_id"] + 1
                extracted = extract_message(update)
                if extracted is None:
                    continue

                chat_id, text = extracted
                reply = handle_command(text)
                bot.send_message(chat_id, reply)
        except Exception:
            logger.exception("Unexpected error in polling loop")
            time.sleep(3)


if __name__ == "__main__":
    main()
