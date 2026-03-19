import string

import pytest

from password_generator import PasswordGenerationError, PasswordOptions, generate_password


def test_generate_password_contains_all_selected_groups() -> None:
    password = generate_password(PasswordOptions(length=20))

    assert len(password) == 20
    assert any(char in string.ascii_uppercase for char in password)
    assert any(char in string.ascii_lowercase for char in password)
    assert any(char in string.digits for char in password)
    assert any(char in "!@#$%^&*()-_=+[]{};:,.?/" for char in password)


def test_generate_digits_only_password() -> None:
    password = generate_password(
        PasswordOptions(
            length=10,
            use_uppercase=False,
            use_lowercase=False,
            use_digits=True,
            use_symbols=False,
        )
    )

    assert len(password) == 10
    assert all(char in string.digits for char in password)


@pytest.mark.parametrize(
    ("options", "message"),
    [
        (PasswordOptions(length=3), "Минимальная длина пароля"),
        (
            PasswordOptions(
                length=8,
                use_uppercase=False,
                use_lowercase=False,
                use_digits=False,
                use_symbols=False,
            ),
            "Нужно выбрать хотя бы один набор символов",
        ),
        (
            PasswordOptions(
                length=2,
                use_uppercase=True,
                use_lowercase=True,
                use_digits=True,
                use_symbols=False,
            ),
            "Минимальная длина пароля",
        ),
    ],
)
def test_generate_password_raises_for_invalid_options(
    options: PasswordOptions, message: str
) -> None:
    with pytest.raises(PasswordGenerationError, match=message):
        generate_password(options)
