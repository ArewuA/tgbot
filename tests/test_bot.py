import os
from pathlib import Path

import pytest

from bot import handle_command, load_env_file, parse_args
from password_generator import PasswordGenerationError


def test_handle_start_command() -> None:
    assert "бот для генерации паролей" in handle_command("/start")


def test_handle_generate_command() -> None:
    response = handle_command("/generate 12 digits")

    assert "Ваш пароль" in response
    assert "<code>" in response


def test_handle_blank_command() -> None:
    assert "Отправь команду /generate" in handle_command("   ")



def test_parse_args_rejects_non_numeric_length() -> None:
    with pytest.raises(PasswordGenerationError, match="Первый аргумент должен быть числом"):
        parse_args(["abc"])



def test_load_env_file_sets_missing_variables(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_BOT_TOKEN=test-token\nCUSTOM_VALUE=42\n", encoding="utf-8")

    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("CUSTOM_VALUE", raising=False)

    load_env_file(str(env_file))

    assert os.environ["TELEGRAM_BOT_TOKEN"] == "test-token"
    assert os.environ["CUSTOM_VALUE"] == "42"
