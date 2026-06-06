"""Tests for sensitive data redaction utilities."""
from framework.utils.redact import (
    REDACTED,
    is_sensitive_key,
    redact_dict,
    redact_headers,
    redact_log_message,
    redact_payload,
    redact_selector_value,
    redact_value,
)


class TestRedact:
    def test_is_sensitive_key(self):
        assert is_sensitive_key("password")
        assert is_sensitive_key("api_key")
        assert is_sensitive_key("Authorization")
        assert not is_sensitive_key("username")

    def test_redact_value_masks_sensitive_keys(self):
        assert redact_value("password", "secret123") == REDACTED
        assert redact_value("email", "user@example.com") == "user@example.com"

    def test_redact_dict(self):
        data = {"email": "a@b.com", "password": "secret"}
        redacted = redact_dict(data)
        assert redacted["email"] == "a@b.com"
        assert redacted["password"] == REDACTED

    def test_redact_payload_nested(self):
        payload = {"user": {"token": "abc", "name": "test"}}
        redacted = redact_payload(payload)
        assert redacted["user"]["token"] == REDACTED
        assert redacted["user"]["name"] == "test"

    def test_redact_headers(self):
        headers = {"Authorization": "Bearer xyz", "Content-Type": "application/json"}
        redacted = redact_headers(headers)
        assert redacted["Authorization"] == REDACTED
        assert redacted["Content-Type"] == "application/json"

    def test_redact_selector_value(self):
        assert redact_selector_value("#password", "secret") == REDACTED
        assert redact_selector_value("#email", "a@b.com") == "a@b.com"

    def test_redact_log_message(self):
        message = 'Request Body: {"password": "secret123", "email": "a@b.com"}'
        redacted = redact_log_message(message)
        assert "secret123" not in redacted
        assert REDACTED in redacted

    def test_redact_log_message_bearer_token(self):
        message = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9"
        redacted = redact_log_message(message)
        assert "Bearer ***" in redacted
