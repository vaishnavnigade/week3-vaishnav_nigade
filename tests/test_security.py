
from datetime import timedelta

import jwt
import pytest

from app.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_can_be_verified() -> None:
    password = "TestPassword123!"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password) is True
    assert verify_password("WrongPassword", hashed_password) is False


def test_access_token_contains_subject_and_role() -> None:
    token = create_access_token(
        subject="14",
        role="customer",
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "14"
    assert payload["role"] == "customer"
    assert "exp" in payload
    assert "iat" in payload


def test_expired_access_token_is_rejected() -> None:
    token = create_access_token(
        subject="14",
        role="customer",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)
