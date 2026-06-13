"""Strict payload validation with SQL-injection / XSS screening.

This module has two layers:

1. :class:`PayloadValidator` — a framework-agnostic validator that checks a
   dict of fields against per-field rules (type, required, length, allowed
   characters / choices) **and** screens every string value for SQL-injection
   and XSS signatures. It returns a cleaned payload or raises
   :class:`ValidationError` listing every problem found.

2. :class:`PayloadValidationMiddleware` (in ``middleware.py``) — a thin
   Starlette/FastAPI middleware that runs the validator over JSON request
   bodies and returns ``422`` on failure.

Security note
-------------
Signature-based screening is **defense in depth**, not a primary control. The
real defenses are *parameterised queries* (against SQLi) and *context-aware
output encoding* (against XSS). This layer catches obvious payloads early and
keeps junk out of the system; it is intentionally conservative (allow-list
field rules do most of the work, the deny-list is a backstop).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Pattern

__all__ = ["FieldRule", "PayloadValidator", "ValidationError", "FIELD_RULES"]


# --------------------------------------------------------------------------
# Injection signatures (deny-list backstop)
# --------------------------------------------------------------------------

# Compiled once. Each pattern is case-insensitive.
_SQLI_PATTERNS: List[Pattern[str]] = [
    re.compile(r"\bunion\b\s+\bselect\b", re.I),
    re.compile(r"\bselect\b.+\bfrom\b", re.I),
    re.compile(r"\binsert\b\s+\binto\b", re.I),
    re.compile(r"\b(drop|alter|truncate)\b\s+\btable\b", re.I),
    re.compile(r"\bdelete\b\s+\bfrom\b", re.I),
    re.compile(r"\bor\b\s+\d+\s*=\s*\d+", re.I),       # OR 1=1
    re.compile(r"'\s*or\s*'", re.I),                    # ' OR '
    re.compile(r"'\s*-{2,}", re.I),                     # ' followed by -- (comment terminator)
    re.compile(r"-{2,}\s|#\s|/\*", re.I),               # SQL comments
    re.compile(r";\s*\b(drop|delete|update|insert)\b", re.I),
    re.compile(r"\bxp_cmdshell\b", re.I),
    re.compile(r"\bwaitfor\b\s+\bdelay\b", re.I),
    re.compile(r"\bsleep\s*\(", re.I),
]

_XSS_PATTERNS: List[Pattern[str]] = [
    re.compile(r"<\s*script", re.I),
    re.compile(r"<\s*/\s*script", re.I),
    re.compile(r"javascript\s*:", re.I),
    re.compile(r"\bon\w+\s*=", re.I),                   # onerror=, onload=, ...
    re.compile(r"<\s*iframe", re.I),
    re.compile(r"<\s*img[^>]*\bsrc\b", re.I),
    re.compile(r"<\s*svg", re.I),
    re.compile(r"document\s*\.\s*cookie", re.I),
    re.compile(r"\beval\s*\(", re.I),
    re.compile(r"&#x?[0-9a-f]+;?", re.I),               # html entity obfuscation
]


def find_sqli(value: str) -> Optional[str]:
    """Return the matched SQLi signature, or ``None``."""
    for pat in _SQLI_PATTERNS:
        if pat.search(value):
            return pat.pattern
    return None


def find_xss(value: str) -> Optional[str]:
    """Return the matched XSS signature, or ``None``."""
    for pat in _XSS_PATTERNS:
        if pat.search(value):
            return pat.pattern
    return None


# --------------------------------------------------------------------------
# Field rules
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class FieldRule:
    """An allow-list rule for a single field."""

    name: str
    type: type = str
    required: bool = True
    min_len: int = 0
    max_len: int = 256
    pattern: Optional[Pattern[str]] = None
    choices: Optional[frozenset] = None
    # Numeric bounds (for int/float fields).
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    # If True, the value is screened for SQLi/XSS signatures.
    screen: bool = True


_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE = re.compile(r"^\+?[0-9 \-]{7,20}$")
_ALNUM = re.compile(r"^[A-Za-z0-9_]+$")
_NAME = re.compile(r"^[A-Za-z .'\-]+$")
_POSTAL = re.compile(r"^[A-Za-z0-9 \-]{3,12}$")
_COUNTRY = re.compile(r"^[A-Z]{2}$")
_CURRENCY = re.compile(r"^[A-Z]{3}$")
_UUIDISH = re.compile(r"^[A-Za-z0-9\-]{6,64}$")
_CARD = re.compile(r"^[0-9]{13,19}$")
_CVV = re.compile(r"^[0-9]{3,4}$")
_EXPIRY = re.compile(r"^(0[1-9]|1[0-2])/[0-9]{2}$")
_IP = re.compile(r"^[0-9a-fA-F:.]{3,45}$")


# 20 distinct payload fields, each with an allow-list rule.
FIELD_RULES: Dict[str, FieldRule] = {
    r.name: r
    for r in [
        FieldRule("email", max_len=254, pattern=_EMAIL),
        FieldRule("username", min_len=3, max_len=32, pattern=_ALNUM),
        FieldRule("password", min_len=8, max_len=128, screen=False),  # never regex/screen secrets
        FieldRule("full_name", min_len=1, max_len=80, pattern=_NAME),
        FieldRule("phone", pattern=_PHONE),
        FieldRule("address_line1", min_len=1, max_len=120),
        FieldRule("address_line2", required=False, max_len=120),
        FieldRule("city", min_len=1, max_len=60, pattern=_NAME),
        FieldRule("state", required=False, max_len=60, pattern=_NAME),
        FieldRule("postal_code", pattern=_POSTAL),
        FieldRule("country", pattern=_COUNTRY),
        FieldRule("card_number", pattern=_CARD),
        FieldRule("card_holder", min_len=1, max_len=80, pattern=_NAME),
        FieldRule("card_expiry", pattern=_EXPIRY),
        FieldRule("card_cvv", pattern=_CVV),
        FieldRule("amount", type=float, min_value=0.01, max_value=1_000_000),
        FieldRule("currency", pattern=_CURRENCY),
        FieldRule("order_id", pattern=_UUIDISH),
        FieldRule("coupon_code", required=False, max_len=32, pattern=_ALNUM),
        FieldRule("comment", required=False, max_len=500),  # free text -> screened
    ]
}


class ValidationError(Exception):
    """Raised when a payload fails validation. ``.errors`` lists every issue."""

    def __init__(self, errors: List[Dict[str, str]]):
        self.errors = errors
        super().__init__(f"payload validation failed: {len(errors)} error(s)")


class PayloadValidator:
    """Validate a payload dict against a set of :class:`FieldRule` objects."""

    def __init__(self, rules: Optional[Dict[str, FieldRule]] = None,
                 allow_unknown: bool = False) -> None:
        self.rules = rules if rules is not None else FIELD_RULES
        self.allow_unknown = allow_unknown

    def validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Return a cleaned payload or raise :class:`ValidationError`.

        Collects *all* errors rather than failing on the first one.
        """
        if not isinstance(payload, dict):
            raise ValidationError([{"field": "<root>", "error": "payload must be an object"}])

        errors: List[Dict[str, str]] = []
        cleaned: Dict[str, Any] = {}

        # Reject unknown fields unless explicitly allowed.
        if not self.allow_unknown:
            for key in payload:
                if key not in self.rules:
                    errors.append({"field": key, "error": "unknown field"})

        for name, rule in self.rules.items():
            present = name in payload
            value = payload.get(name)

            if not present or value is None:
                if rule.required:
                    errors.append({"field": name, "error": "required"})
                continue

            field_errors = self._validate_field(rule, value)
            if field_errors:
                errors.extend(field_errors)
            else:
                cleaned[name] = value

        if errors:
            raise ValidationError(errors)
        return cleaned

    # -- per-field checks -------------------------------------------------

    def _validate_field(self, rule: FieldRule, value: Any) -> List[Dict[str, str]]:
        errs: List[Dict[str, str]] = []

        # Type check (bool is not an int here; reject it explicitly).
        if rule.type in (int, float):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return [{"field": rule.name, "error": f"must be {rule.type.__name__}"}]
            if rule.min_value is not None and value < rule.min_value:
                errs.append({"field": rule.name, "error": f"must be >= {rule.min_value}"})
            if rule.max_value is not None and value > rule.max_value:
                errs.append({"field": rule.name, "error": f"must be <= {rule.max_value}"})
            return errs

        # String fields.
        if not isinstance(value, str):
            return [{"field": rule.name, "error": "must be a string"}]

        if len(value) < rule.min_len:
            errs.append({"field": rule.name, "error": f"too short (min {rule.min_len})"})
        if len(value) > rule.max_len:
            errs.append({"field": rule.name, "error": f"too long (max {rule.max_len})"})

        if rule.choices is not None and value not in rule.choices:
            errs.append({"field": rule.name, "error": "not an allowed value"})

        if rule.pattern is not None and not rule.pattern.match(value):
            errs.append({"field": rule.name, "error": "invalid format"})

        # Deny-list backstop (skipped for secrets like passwords).
        if rule.screen:
            sig = find_sqli(value)
            if sig:
                errs.append({"field": rule.name, "error": "possible SQL injection"})
            sig = find_xss(value)
            if sig:
                errs.append({"field": rule.name, "error": "possible XSS"})

        return errs

    def screen_all(self, payload: Dict[str, Any]) -> List[Dict[str, str]]:
        """Screen every string value (recursively) for injection signatures.

        Useful as a blanket pass independent of per-field rules.
        """
        hits: List[Dict[str, str]] = []

        def walk(prefix: str, val: Any) -> None:
            if isinstance(val, str):
                if find_sqli(val):
                    hits.append({"field": prefix, "error": "possible SQL injection"})
                if find_xss(val):
                    hits.append({"field": prefix, "error": "possible XSS"})
            elif isinstance(val, dict):
                for k, v in val.items():
                    walk(f"{prefix}.{k}" if prefix else str(k), v)
            elif isinstance(val, (list, tuple)):
                for i, v in enumerate(val):
                    walk(f"{prefix}[{i}]", v)

        walk("", payload)
        return hits
