"""Security-focused pytest suite for :mod:`aes_gcm`.

These tests verify functional correctness (round-trips) and, more importantly,
the security properties that make GCM safe: unique nonces, tamper detection,
AAD binding, key-length enforcement, and no plaintext leakage on failure.
"""

import base64

import pytest

from aes_gcm import AESGCMCipher, DecryptionError, KEY_SIZE, NONCE_SIZE, TAG_SIZE


@pytest.fixture
def cipher():
    return AESGCMCipher(AESGCMCipher.generate_key())


# --------------------------------------------------------------------------
# Key handling
# --------------------------------------------------------------------------

def test_generate_key_is_correct_length():
    assert len(AESGCMCipher.generate_key()) == KEY_SIZE


def test_generate_key_is_random():
    # Two freshly generated keys must (with overwhelming probability) differ.
    assert AESGCMCipher.generate_key() != AESGCMCipher.generate_key()


@pytest.mark.parametrize("bad_len", [0, 1, 15, 16, 24, 31, 33, 64])
def test_rejects_wrong_key_length(bad_len):
    with pytest.raises(ValueError):
        AESGCMCipher(b"\x00" * bad_len)


@pytest.mark.parametrize("bad_key", ["not-bytes", 12345, None, ["x"] * 32])
def test_rejects_non_bytes_key(bad_key):
    with pytest.raises(TypeError):
        AESGCMCipher(bad_key)


def test_base64_key_roundtrip():
    key_b64 = AESGCMCipher.generate_key_b64()
    c1 = AESGCMCipher.from_base64_key(key_b64)
    c2 = AESGCMCipher.from_base64_key(key_b64)
    # Same key -> c2 can decrypt what c1 encrypted.
    token = c1.encrypt(b"shared secret")
    assert c2.decrypt(token) == b"shared secret"


def test_from_base64_key_rejects_garbage():
    with pytest.raises(ValueError):
        AESGCMCipher.from_base64_key("!!!not base64!!!")


def test_from_base64_key_rejects_wrong_length_key():
    short = base64.urlsafe_b64encode(b"too short").decode()
    with pytest.raises(ValueError):
        AESGCMCipher.from_base64_key(short)


def test_repr_does_not_leak_key(cipher):
    assert "key=<hidden>" in repr(cipher)
    assert "key=<hidden>" in str(cipher)


# --------------------------------------------------------------------------
# Round-trip correctness
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "plaintext",
    [
        b"",                       # empty message
        b"a",                      # single byte
        b"hello world",
        b"\x00\x01\x02\xff\xfe",  # arbitrary binary
        b"x" * 100_000,            # large message
        "unicode: é中文 \U0001f512".encode("utf-8"),
    ],
)
def test_encrypt_decrypt_roundtrip(cipher, plaintext):
    assert cipher.decrypt(cipher.encrypt(plaintext)) == plaintext


def test_string_api_roundtrip(cipher):
    token = cipher.encrypt_to_str(b"payload")
    assert isinstance(token, str)
    assert cipher.decrypt_from_str(token) == b"payload"


def test_ciphertext_is_not_plaintext(cipher):
    pt = b"sensitive-card-number-4111111111111111"
    token = cipher.encrypt(pt)
    assert pt not in token


def test_token_layout_lengths(cipher):
    token = cipher.encrypt(b"")  # empty plaintext
    # nonce + tag with no plaintext bytes
    assert len(token) == NONCE_SIZE + TAG_SIZE
    token2 = cipher.encrypt(b"1234")
    assert len(token2) == NONCE_SIZE + TAG_SIZE + 4


# --------------------------------------------------------------------------
# Nonce uniqueness (the property that makes GCM safe)
# --------------------------------------------------------------------------

def test_nonce_is_unique_per_encryption(cipher):
    nonces = {cipher.encrypt(b"same plaintext")[:NONCE_SIZE] for _ in range(2000)}
    assert len(nonces) == 2000  # no collisions


def test_same_plaintext_yields_different_ciphertexts(cipher):
    # Because the nonce differs each time, identical plaintext must produce
    # different tokens (no deterministic leakage).
    assert cipher.encrypt(b"repeat") != cipher.encrypt(b"repeat")


# --------------------------------------------------------------------------
# Associated Authenticated Data (AAD)
# --------------------------------------------------------------------------

def test_aad_roundtrip(cipher):
    token = cipher.encrypt(b"body", aad=b"user-42")
    assert cipher.decrypt(token, aad=b"user-42") == b"body"


def test_wrong_aad_fails(cipher):
    token = cipher.encrypt(b"body", aad=b"user-42")
    with pytest.raises(DecryptionError):
        cipher.decrypt(token, aad=b"user-99")


def test_missing_aad_fails_when_required(cipher):
    token = cipher.encrypt(b"body", aad=b"context")
    with pytest.raises(DecryptionError):
        cipher.decrypt(token)  # no AAD supplied


def test_unexpected_aad_fails(cipher):
    token = cipher.encrypt(b"body")  # encrypted without AAD
    with pytest.raises(DecryptionError):
        cipher.decrypt(token, aad=b"unexpected")


def test_empty_aad_equivalent_to_none(cipher):
    # b"" and None must be interchangeable, both ways.
    token_none = cipher.encrypt(b"body", aad=None)
    assert cipher.decrypt(token_none, aad=b"") == b"body"
    token_empty = cipher.encrypt(b"body", aad=b"")
    assert cipher.decrypt(token_empty, aad=None) == b"body"


# --------------------------------------------------------------------------
# Tamper detection / integrity
# --------------------------------------------------------------------------

def test_tampered_ciphertext_fails(cipher):
    token = bytearray(cipher.encrypt(b"important data"))
    token[-1] ^= 0x01  # flip one bit in the tag
    with pytest.raises(DecryptionError):
        cipher.decrypt(bytes(token))


def test_tampered_nonce_fails(cipher):
    token = bytearray(cipher.encrypt(b"important data"))
    token[0] ^= 0x01  # flip a bit in the nonce
    with pytest.raises(DecryptionError):
        cipher.decrypt(bytes(token))


def test_tampered_body_fails(cipher):
    token = bytearray(cipher.encrypt(b"some longer body to mutate"))
    token[NONCE_SIZE + 1] ^= 0xFF  # flip a bit inside the ciphertext body
    with pytest.raises(DecryptionError):
        cipher.decrypt(bytes(token))


def test_wrong_key_fails(cipher):
    token = cipher.encrypt(b"secret")
    other = AESGCMCipher(AESGCMCipher.generate_key())
    with pytest.raises(DecryptionError):
        other.decrypt(token)


# --------------------------------------------------------------------------
# Malformed input handling
# --------------------------------------------------------------------------

@pytest.mark.parametrize("short", [b"", b"\x00", b"\x00" * (NONCE_SIZE + TAG_SIZE - 1)])
def test_too_short_token_rejected(cipher, short):
    with pytest.raises(DecryptionError):
        cipher.decrypt(short)


def test_non_bytes_plaintext_rejected(cipher):
    with pytest.raises(TypeError):
        cipher.encrypt("a string, not bytes")  # type: ignore[arg-type]


def test_non_bytes_token_rejected(cipher):
    with pytest.raises(TypeError):
        cipher.decrypt("a string, not bytes")  # type: ignore[arg-type]


def test_bad_base64_token_rejected(cipher):
    with pytest.raises(DecryptionError):
        cipher.decrypt_from_str("!!!not-base64!!!")


def test_non_bytes_aad_rejected(cipher):
    with pytest.raises(TypeError):
        cipher.encrypt(b"x", aad=123)  # type: ignore[arg-type]
