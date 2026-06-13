"""Tests for the validation layer: per-field rules, SQLi/XSS screening,
and the FastAPI middleware integration."""

import copy

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from gateway.validation import (
    FIELD_RULES,
    PayloadValidator,
    ValidationError,
    find_sqli,
    find_xss,
)
from gateway.middleware import PayloadValidationMiddleware


# A fully valid payload covering all 20 fields.
VALID = {
    "email": "jane.doe@example.com",
    "username": "jane_doe",
    "password": "sup3r-secret-pw",
    "full_name": "Jane Doe",
    "phone": "+1 555-123-4567",
    "address_line1": "221B Baker Street",
    "address_line2": "Flat 2",
    "city": "London",
    "state": "Greater London",
    "postal_code": "NW1 6XE",
    "country": "GB",
    "card_number": "4111111111111111",
    "card_holder": "Jane Doe",
    "card_expiry": "12/29",
    "card_cvv": "123",
    "amount": 49.99,
    "currency": "USD",
    "order_id": "ord-2026-0001",
    "coupon_code": "SAVE10",
    "comment": "Please leave at the front desk.",
}


@pytest.fixture
def validator():
    return PayloadValidator()


def test_valid_payload_passes(validator):
    cleaned = validator.validate(VALID)
    assert cleaned["email"] == "jane.doe@example.com"
    assert cleaned["amount"] == 49.99


def test_field_rules_count():
    # The spec calls for 20 distinct fields.
    assert len(FIELD_RULES) == 20


# --------------------------------------------------------------------------
# Per-field validation — one parametrised test exercising every field
# --------------------------------------------------------------------------

# (field, bad_value, substring expected in the error message)
BAD_CASES = [
    ("email", "not-an-email", "format"),
    ("username", "ab", "short"),
    ("username", "has spaces", "format"),
    ("password", "short", "short"),
    ("full_name", "Jane123", "format"),
    ("phone", "abc", "format"),
    ("address_line1", "", "short"),
    ("city", "City99", "format"),
    ("postal_code", "!!", "format"),
    ("country", "USA", "format"),         # must be 2-letter
    ("card_number", "12ab", "format"),
    ("card_holder", "Jane9", "format"),
    ("card_expiry", "13/29", "format"),   # month 13 invalid
    ("card_cvv", "12", "format"),
    ("currency", "usd", "format"),        # must be uppercase 3-letter
    ("order_id", "x", "format"),          # too short for pattern
    ("coupon_code", "bad code!", "format"),
]


@pytest.mark.parametrize("field,bad,msg", BAD_CASES)
def test_field_rejects_bad_value(validator, field, bad, msg):
    payload = copy.deepcopy(VALID)
    payload[field] = bad
    with pytest.raises(ValidationError) as ei:
        validator.validate(payload)
    errs = {e["field"]: e["error"] for e in ei.value.errors}
    assert field in errs
    assert msg in errs[field]


# Numeric bounds for `amount`.
@pytest.mark.parametrize("amount", [0, -5, 1_000_001])
def test_amount_out_of_bounds(validator, amount):
    payload = copy.deepcopy(VALID)
    payload["amount"] = amount
    with pytest.raises(ValidationError):
        validator.validate(payload)


def test_amount_must_be_number_not_bool(validator):
    payload = copy.deepcopy(VALID)
    payload["amount"] = True  # bool must be rejected even though it's int-ish
    with pytest.raises(ValidationError) as ei:
        validator.validate(payload)
    assert any(e["field"] == "amount" for e in ei.value.errors)


def test_string_field_rejects_non_string(validator):
    payload = copy.deepcopy(VALID)
    payload["city"] = 12345
    with pytest.raises(ValidationError) as ei:
        validator.validate(payload)
    assert any(e["field"] == "city" for e in ei.value.errors)


# --------------------------------------------------------------------------
# Required / optional / unknown
# --------------------------------------------------------------------------

def test_missing_required_field(validator):
    payload = copy.deepcopy(VALID)
    del payload["email"]
    with pytest.raises(ValidationError) as ei:
        validator.validate(payload)
    assert {"field": "email", "error": "required"} in ei.value.errors


def test_optional_fields_may_be_absent(validator):
    payload = copy.deepcopy(VALID)
    for opt in ("address_line2", "state", "coupon_code", "comment"):
        payload.pop(opt, None)
    cleaned = validator.validate(payload)
    assert "address_line2" not in cleaned


def test_unknown_field_rejected(validator):
    payload = copy.deepcopy(VALID)
    payload["evil_extra"] = "x"
    with pytest.raises(ValidationError) as ei:
        validator.validate(payload)
    assert {"field": "evil_extra", "error": "unknown field"} in ei.value.errors


def test_allow_unknown_mode():
    v = PayloadValidator(allow_unknown=True)
    payload = copy.deepcopy(VALID)
    payload["extra"] = "ok"
    cleaned = v.validate(payload)  # should not raise
    assert "extra" not in cleaned  # unknown fields aren't in cleaned output


def test_collects_all_errors_at_once(validator):
    payload = copy.deepcopy(VALID)
    payload["email"] = "bad"
    payload["country"] = "USA"
    payload["amount"] = -1
    with pytest.raises(ValidationError) as ei:
        validator.validate(payload)
    fields = {e["field"] for e in ei.value.errors}
    assert {"email", "country", "amount"} <= fields


def test_non_dict_payload(validator):
    with pytest.raises(ValidationError):
        validator.validate(["not", "a", "dict"])


# --------------------------------------------------------------------------
# SQL-injection screening
# --------------------------------------------------------------------------

SQLI_SAMPLES = [
    "' OR '1'='1",
    "1; DROP TABLE users",
    "admin'--",
    "UNION SELECT password FROM users",
    "1 OR 1=1",
    "'; DELETE FROM accounts; --",
    "SELECT * FROM secrets",
    "'; WAITFOR DELAY '0:0:5'--",
    "1 AND SLEEP(5)",
]


@pytest.mark.parametrize("sample", SQLI_SAMPLES)
def test_find_sqli_detects(sample):
    assert find_sqli(sample) is not None


SQLI_BENIGN = [
    "I would like to order 2 items",
    "My name is O'Brien",          # apostrophe alone is fine
    "Deliver from 9am to 5pm",
]


@pytest.mark.parametrize("sample", SQLI_BENIGN)
def test_find_sqli_no_false_positive(sample):
    assert find_sqli(sample) is None


def test_sqli_in_field_is_rejected(validator):
    payload = copy.deepcopy(VALID)
    payload["comment"] = "'; DROP TABLE orders; --"
    with pytest.raises(ValidationError) as ei:
        validator.validate(payload)
    assert any("SQL" in e["error"] for e in ei.value.errors)


# --------------------------------------------------------------------------
# XSS screening
# --------------------------------------------------------------------------

XSS_SAMPLES = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(document.cookie)",
    "<svg/onload=alert(1)>",
    "<iframe src='evil'></iframe>",
    "<a href='#' onclick='steal()'>",
]


@pytest.mark.parametrize("sample", XSS_SAMPLES)
def test_find_xss_detects(sample):
    assert find_xss(sample) is not None


@pytest.mark.parametrize("sample", ["Just a normal comment.", "Price < 100 > 50"])
def test_find_xss_no_false_positive(sample):
    # Note: "< 100 >" has no tag name after '<', so it should not match.
    assert find_xss(sample) is None


def test_xss_in_field_is_rejected(validator):
    payload = copy.deepcopy(VALID)
    payload["comment"] = "<script>steal()</script>"
    with pytest.raises(ValidationError) as ei:
        validator.validate(payload)
    assert any("XSS" in e["error"] for e in ei.value.errors)


def test_password_is_not_screened(validator):
    # Passwords may legitimately contain odd characters; we must not screen or
    # regex them. A password that "looks" like SQL must still pass.
    payload = copy.deepcopy(VALID)
    payload["password"] = "p' OR '1'='1--xY"
    cleaned = validator.validate(payload)
    assert cleaned["password"] == "p' OR '1'='1--xY"


def test_screen_all_recurses():
    v = PayloadValidator()
    hits = v.screen_all({"a": {"b": ["ok", "<script>x</script>"]}})
    assert any("XSS" in h["error"] for h in hits)
    assert hits[0]["field"].startswith("a.b")


# --------------------------------------------------------------------------
# Middleware integration
# --------------------------------------------------------------------------

@pytest.fixture
def client():
    app = FastAPI()
    app.add_middleware(PayloadValidationMiddleware, paths=["/pay"])

    @app.post("/pay")
    async def pay(body: dict):
        return {"ok": True, "received": body["order_id"]}

    @app.post("/open")
    async def open_route(body: dict):
        return {"ok": True}

    return TestClient(app)


def test_middleware_passes_valid_payload(client):
    r = client.post("/pay", json=VALID)
    assert r.status_code == 200
    assert r.json()["received"] == "ord-2026-0001"


def test_middleware_blocks_invalid_payload(client):
    bad = copy.deepcopy(VALID)
    bad["email"] = "nope"
    r = client.post("/pay", json=bad)
    assert r.status_code == 422
    assert any(e["field"] == "email" for e in r.json()["errors"])


def test_middleware_blocks_xss(client):
    bad = copy.deepcopy(VALID)
    bad["comment"] = "<script>alert(1)</script>"
    r = client.post("/pay", json=bad)
    assert r.status_code == 422


def test_middleware_rejects_bad_json(client):
    r = client.post(
        "/pay", content=b"{not json", headers={"content-type": "application/json"}
    )
    assert r.status_code == 400


def test_middleware_ignores_unconfigured_path(client):
    # /open isn't in paths, so even an invalid body passes the middleware
    # (the route itself just echoes ok).
    r = client.post("/open", json={"anything": "goes"})
    assert r.status_code == 200


def test_middleware_rejects_oversized_body():
    app = FastAPI()
    app.add_middleware(PayloadValidationMiddleware, paths=["/pay"], max_body_bytes=10)

    @app.post("/pay")
    async def pay(body: dict):
        return {"ok": True}

    c = TestClient(app)
    r = c.post("/pay", json=VALID)
    assert r.status_code == 413
