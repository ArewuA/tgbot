from __future__ import annotations

from dataclasses import dataclass
import secrets
import string


@dataclass(frozen=True)
class PasswordOptions:
    length: int = 16
    use_uppercase: bool = True
    use_lowercase: bool = True
    use_digits: bool = True
    use_symbols: bool = True


class PasswordGenerationError(ValueError):
    """Raised when password options are invalid."""


def generate_password(options: PasswordOptions) -> str:
    if options.length < 4:
        raise PasswordGenerationError("Минимальная длина пароля — 4 символа.")

    pools: list[str] = []

    if options.use_uppercase:
        pools.append(string.ascii_uppercase)
    if options.use_lowercase:
        pools.append(string.ascii_lowercase)
    if options.use_digits:
        pools.append(string.digits)
    if options.use_symbols:
        pools.append("!@#$%^&*()-_=+[]{};:,.?/")

    if not pools:
        raise PasswordGenerationError("Нужно выбрать хотя бы один набор символов.")

    if options.length < len(pools):
        raise PasswordGenerationError(
            "Длина пароля должна быть не меньше количества выбранных наборов символов."
        )

    password_chars = [secrets.choice(pool) for pool in pools]
    all_characters = "".join(pools)

    password_chars.extend(
        secrets.choice(all_characters) for _ in range(options.length - len(password_chars))
    )
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)
