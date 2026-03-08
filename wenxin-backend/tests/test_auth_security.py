"""Test auth security."""
from __future__ import annotations

import os
import time
from datetime import timedelta

import pytest

# Set env vars before importing any app modules
os.environ["SECRET_KEY"] = "test-secret-key-for-ci-at-least-32-chars"


from app.core.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    pwd_context,
    verify_password,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def plain_password() -> str:
    return "correct-horse-battery-staple"


@pytest.fixture()
def hashed_password(plain_password: str) -> str:
    return get_password_hash(plain_password)


@pytest.fixture()
def valid_token() -> str:
    return create_access_token(subject="testuser")


# ---------------------------------------------------------------------------
# verify_password
# ---------------------------------------------------------------------------

class TestVerifyPassword:
    def test_correct_password_returns_true(
        self, plain_password: str, hashed_password: str
    ) -> None:
        assert verify_password(plain_password, hashed_password) is True

    def test_wrong_password_returns_false(self, hashed_password: str) -> None:
        assert verify_password("wrong-password", hashed_password) is False


# ---------------------------------------------------------------------------
# get_password_hash
# ---------------------------------------------------------------------------

class TestGetPasswordHash:
    def test_returns_bcrypt_hash(self, plain_password: str) -> None:
        h = get_password_hash(plain_password)
        # bcrypt hashes start with $2b$ (or $2a$/$2y$)
        assert h.startswith("$2b$") or h.startswith("$2a$") or h.startswith("$2y$")

    def test_hash_is_verifiable(self, plain_password: str) -> None:
        h = get_password_hash(plain_password)
        assert verify_password(plain_password, h) is True

    def test_different_calls_produce_different_hashes(
        self, plain_password: str
    ) -> None:
        h1 = get_password_hash(plain_password)
        h2 = get_password_hash(plain_password)
        assert h1 != h2  # salted → always different


# ---------------------------------------------------------------------------
# create_access_token
# ---------------------------------------------------------------------------

class TestCreateAccessToken:
    def test_returns_string(self) -> None:
        token = create_access_token(subject="user1")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_contains_sub_claim(self) -> None:
        token = create_access_token(subject="user42")
        sub = decode_token(token)
        assert sub == "user42"

    def test_integer_subject_becomes_string(self) -> None:
        token = create_access_token(subject=99)
        sub = decode_token(token)
        assert sub == "99"

    def test_custom_expiry(self) -> None:
        token = create_access_token(
            subject="exp-test", expires_delta=timedelta(hours=1)
        )
        sub = decode_token(token)
        assert sub == "exp-test"


# ---------------------------------------------------------------------------
# decode_token
# ---------------------------------------------------------------------------

class TestDecodeToken:
    def test_valid_token(self, valid_token: str) -> None:
        sub = decode_token(valid_token)
        assert sub == "testuser"

    def test_invalid_token_returns_none(self) -> None:
        assert decode_token("not-a-jwt") is None

    def test_tampered_token_returns_none(self, valid_token: str) -> None:
        # Flip last character to invalidate signature
        tampered = valid_token[:-1] + ("A" if valid_token[-1] != "A" else "B")
        assert decode_token(tampered) is None

    def test_expired_token_returns_none(self) -> None:
        token = create_access_token(
            subject="expire-me", expires_delta=timedelta(seconds=-1)
        )
        assert decode_token(token) is None


# ---------------------------------------------------------------------------
# bcrypt 4.0.x / passlib compatibility
# ---------------------------------------------------------------------------

class TestBcryptPasslibCompat:
    def test_passlib_bcrypt_context_works(self) -> None:
        """passlib CryptContext with bcrypt scheme can hash and verify."""
        h = pwd_context.hash("compat-test")
        assert pwd_context.verify("compat-test", h) is True
        assert pwd_context.verify("wrong", h) is False

    def test_roundtrip_multiple_passwords(self) -> None:
        """Hash-then-verify cycle for several passwords (regression guard)."""
        passwords = ["", "a", "password123", "ñoño-日本語", "x" * 72]
        for pw in passwords:
            h = get_password_hash(pw)
            assert verify_password(pw, h) is True, f"Failed for password: {pw!r}"
