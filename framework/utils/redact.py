"""Redact sensitive values from logs and reports."""
import json
import re
from typing import Any, Dict, Iterable, Set

SENSITIVE_KEYS: Set[str] = {
    "password",
    "passwd",
    "secret",
    "token",
    "authorization",
    "api_key",
    "apikey",
    "credentials",
}

REDACTED = "***"
_SENSITIVE_JSON_PATTERN = re.compile(
    r'("(?:password|passwd|secret|token|authorization|api_key|apikey|credentials)"\s*:\s*)"(?:[^"\\]|\\.)*"',
    re.IGNORECASE,
)
_BEARER_PATTERN = re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE)


def is_sensitive_key(key: str) -> bool:
    key_lower = key.lower()
    return any(sensitive in key_lower for sensitive in SENSITIVE_KEYS)


def redact_value(key: str, value: Any) -> Any:
    if is_sensitive_key(key):
        return REDACTED
    if isinstance(value, dict):
        return redact_dict(value)
    if isinstance(value, list):
        return [redact_value(str(index), item) for index, item in enumerate(value)]
    return value


def redact_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    return {key: redact_value(key, value) for key, value in data.items()}


def redact_selector_value(selector: str, value: str) -> str:
    if any(token in selector.lower() for token in ("password", "passwd", "secret", "token")):
        return REDACTED
    return value


def redact_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        return redact_dict(payload)
    if isinstance(payload, list):
        return [redact_payload(item) for item in payload]
    return payload


def redact_headers(headers: Dict[str, str]) -> Dict[str, str]:
    return {key: REDACTED if is_sensitive_key(key) else value for key, value in headers.items()}


def redact_log_message(message: str) -> str:
    redacted = _BEARER_PATTERN.sub("Bearer ***", message)
    redacted = _SENSITIVE_JSON_PATTERN.sub(r'\1"***"', redacted)
    return redacted
