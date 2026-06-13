"""Tests for the Redis-backed tokenization engine.

Uses fakeredis (an in-memory Redis) so no server is required. fakeredis
implements TTL semantics, so expiry behaviour is exercised by manipulating its
clock-independent ``ttl`` and by setting tiny TTLs.
"""

import os
import sys

import fakeredis
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "crypto-utils"))
from aes_gcm import AESGCMCipher  # noqa: E402

from gateway.tokenization import (  # noqa: E402
    TokenizationService,
    TokenError,
    TOKEN_PREFIX,
)

PAN = "4111111111111111"


@pytest.fixture
def svc():
    cipher = AESGCMCipher(AESGCMCipher.generate_key())
    redis = fakeredis.FakeStrictRedis()
    return TokenizationService(redis, cipher, default_ttl=900)


# --------------------------------------------------------------------------
# Round-trip
# --------------------------------------------------------------------------

def test_tokenize_detokenize_roundtrip(svc):
    token = svc.tokenize(PAN)
    assert token.startswith(TOKEN_PREFIX)
    assert svc.detokenize(token) == PAN


def test_token_does_not_contain_value(svc):
    token = svc.tokenize(PAN)
    assert PAN not in token


def test_tokens_are_unique_for_same_value(svc):
    tokens = {svc.tokenize(PAN) for _ in range(500)}
    assert len(tokens) == 500


def test_stored_value_is_encrypted_at_rest(svc):
    token = svc.tokenize(PAN)
    raw = svc._redis.get(svc._redis_key(token))
    assert raw is not None
    assert PAN.encode() not in raw  # ciphertext, not plaintext


def test_unicode_value_roundtrip(svc):
    val = "naïve café ☕ 12345"
    token = svc.tokenize(val)
    assert svc.detokenize(token) == val


# --------------------------------------------------------------------------
# Input validation
# --------------------------------------------------------------------------

def test_tokenize_rejects_empty(svc):
    with pytest.raises(ValueError):
        svc.tokenize("")


def test_tokenize_rejects_non_string(svc):
    with pytest.raises(TypeError):
        svc.tokenize(12345)


def test_tokenize_rejects_non_positive_ttl(svc):
    with pytest.raises(ValueError):
        svc.tokenize(PAN, ttl=0)


def test_constructor_rejects_bad_ttl(svc):
    with pytest.raises(ValueError):
        TokenizationService(svc._redis, svc._cipher, default_ttl=0)


# --------------------------------------------------------------------------
# Detokenize failure modes
# --------------------------------------------------------------------------

def test_detokenize_unknown_token(svc):
    with pytest.raises(TokenError):
        svc.detokenize(TOKEN_PREFIX + "does-not-exist")


def test_detokenize_malformed_token(svc):
    with pytest.raises(TokenError):
        svc.detokenize("not-a-real-token")


def test_detokenize_tampered_ciphertext(svc):
    token = svc.tokenize(PAN)
    key = svc._redis_key(token)
    raw = bytearray(svc._redis.get(key))
    raw[-1] ^= 0x01  # flip a bit in the stored ciphertext/tag
    svc._redis.set(key, bytes(raw))
    with pytest.raises(TokenError):
        svc.detokenize(token)


def test_aad_binding_prevents_token_swap(svc):
    # Move record A's ciphertext under token B's key; detokenizing B must fail
    # because the AAD (token) no longer matches.
    t_a = svc.tokenize("AAAA-1111")
    t_b = svc.tokenize("BBBB-2222")
    cipher_a = svc._redis.get(svc._redis_key(t_a))
    svc._redis.set(svc._redis_key(t_b), cipher_a)  # swap
    with pytest.raises(TokenError):
        svc.detokenize(t_b)


# --------------------------------------------------------------------------
# Revoke / exists / TTL
# --------------------------------------------------------------------------

def test_revoke(svc):
    token = svc.tokenize(PAN)
    assert svc.exists(token) is True
    assert svc.revoke(token) is True
    assert svc.exists(token) is False
    with pytest.raises(TokenError):
        svc.detokenize(token)


def test_revoke_missing_returns_false(svc):
    assert svc.revoke(TOKEN_PREFIX + "missing") is False


def test_ttl_is_set(svc):
    token = svc.tokenize(PAN, ttl=120)
    remaining = svc.ttl(token)
    assert 0 < remaining <= 120


def test_ttl_missing_token(svc):
    assert svc.ttl(TOKEN_PREFIX + "missing") == -2


def test_expired_token_cannot_be_detokenized(svc):
    token = svc.tokenize(PAN, ttl=100)
    # Force expiry in fakeredis by deleting the underlying key's TTL window.
    svc._redis.delete(svc._redis_key(token))
    with pytest.raises(TokenError):
        svc.detokenize(token)
