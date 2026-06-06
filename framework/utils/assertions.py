"""
Centralized assertion utilities with hard and soft assertions
"""
import re
from typing import List, Any, Optional
from framework.core.logger import log


class AssertionError(Exception):
    """Custom assertion error for framework assertions with enhanced error reporting"""

    def __init__(
        self,
        message: str,
        actual: Any = None,
        expected: Any = None,
        context: Optional[dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.actual = actual
        self.expected = expected
        self.context = context or {}

    def __str__(self) -> str:
        error_msg = self.message
        if self.expected is not None or self.actual is not None:
            error_msg += "\n"
            if self.expected is not None:
                error_msg += f"Expected: {self.expected}\n"
            if self.actual is not None:
                error_msg += f"Actual: {self.actual}\n"
        if self.context:
            context_str = ", ".join([f"{k}={v}" for k, v in self.context.items()])
            error_msg += f"Context: {context_str}"
        return error_msg

    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "actual": str(self.actual) if self.actual is not None else None,
            "expected": str(self.expected) if self.expected is not None else None,
            "context": self.context,
        }


def _fail(
    message: str,
    actual: Any = None,
    expected: Any = None,
    context: Optional[dict] = None,
):
    raise AssertionError(message=message, actual=actual, expected=expected, context=context or {})


class SoftAssertions:
    """Soft assertion collector - collects failures without stopping execution"""

    def __init__(self):
        self.errors: List[str] = []

    def assert_true(self, condition: bool, message: str = "Condition is not True"):
        if not condition:
            self.errors.append(f"SOFT ASSERT: {message}")
            log.warning(f"Soft assertion failed: {message}")

    def assert_false(self, condition: bool, message: str = "Condition is not False"):
        if condition:
            self.errors.append(f"SOFT ASSERT: {message}")
            log.warning(f"Soft assertion failed: {message}")

    def assert_equal(self, actual: Any, expected: Any, message: Optional[str] = None):
        msg = message or f"Expected {expected}, but got {actual}"
        if actual != expected:
            self.errors.append(f"SOFT ASSERT: {msg}")
            log.warning(f"Soft assertion failed: {msg}")

    def assert_not_equal(self, actual: Any, expected: Any, message: Optional[str] = None):
        msg = message or f"Values should not be equal: {actual}"
        if actual == expected:
            self.errors.append(f"SOFT ASSERT: {msg}")
            log.warning(f"Soft assertion failed: {msg}")

    def assert_in(self, item: Any, container: Any, message: Optional[str] = None):
        msg = message or f"{item} not found in {container}"
        if item not in container:
            self.errors.append(f"SOFT ASSERT: {msg}")
            log.warning(f"Soft assertion failed: {msg}")

    def assert_not_in(self, item: Any, container: Any, message: Optional[str] = None):
        msg = message or f"{item} should not be in {container}"
        if item in container:
            self.errors.append(f"SOFT ASSERT: {msg}")
            log.warning(f"Soft assertion failed: {msg}")

    def assert_is_none(self, value: Any, message: Optional[str] = None):
        msg = message or f"Expected None, but got {value}"
        if value is not None:
            self.errors.append(f"SOFT ASSERT: {msg}")
            log.warning(f"Soft assertion failed: {msg}")

    def assert_is_not_none(self, value: Any, message: Optional[str] = None):
        msg = message or "Expected non-None value"
        if value is None:
            self.errors.append(f"SOFT ASSERT: {msg}")
            log.warning(f"Soft assertion failed: {msg}")

    def assert_greater_than(self, actual: Any, expected: Any, message: Optional[str] = None):
        msg = message or f"Expected {actual} > {expected}"
        if not (actual > expected):
            self.errors.append(f"SOFT ASSERT: {msg}")
            log.warning(f"Soft assertion failed: {msg}")

    def assert_less_than(self, actual: Any, expected: Any, message: Optional[str] = None):
        msg = message or f"Expected {actual} < {expected}"
        if not (actual < expected):
            self.errors.append(f"SOFT ASSERT: {msg}")
            log.warning(f"Soft assertion failed: {msg}")

    def assert_contains(self, container: Any, item: Any, message: Optional[str] = None):
        msg = message or f"{container} should contain {item}"
        if item not in container:
            self.errors.append(f"SOFT ASSERT: {msg}")
            log.warning(f"Soft assertion failed: {msg}")

    def assert_string_contains(self, haystack: str, needle: str, message: Optional[str] = None):
        msg = message or f"Expected '{needle}' in '{haystack}'"
        if needle not in haystack:
            self.errors.append(f"SOFT ASSERT: {msg}")
            log.warning(f"Soft assertion failed: {msg}")

    def assert_regex(self, pattern: str, string: str, message: Optional[str] = None):
        msg = message or f"{string} should match pattern {pattern}"
        if not re.search(pattern, string):
            self.errors.append(f"SOFT ASSERT: {msg}")
            log.warning(f"Soft assertion failed: {msg}")

    def assert_dict_has_key(self, data: dict, key: str, message: Optional[str] = None):
        msg = message or f"Key '{key}' not found in response"
        if key not in data:
            self.errors.append(f"SOFT ASSERT: {msg}")
            log.warning(f"Soft assertion failed: {msg}")

    def assert_all(self):
        if self.errors:
            error_msg = "\n".join(self.errors)
            log.error(f"Soft assertions failed:\n{error_msg}")
            raise AssertionError(
                message=f"Soft assertions failed:\n{error_msg}",
                context={"failure_count": len(self.errors), "errors": self.errors},
            )


class HardAssertions:
    """Hard assertions - stop execution immediately on failure"""

    @staticmethod
    def assert_true(condition: bool, message: str = "Condition is not True"):
        if not condition:
            _fail(message, actual=condition, expected=True)
        log.debug(f"Assertion passed: {message}")

    @staticmethod
    def assert_false(condition: bool, message: str = "Condition is not False"):
        if condition:
            _fail(message, actual=condition, expected=False)
        log.debug(f"Assertion passed: {message}")

    @staticmethod
    def assert_equal(actual: Any, expected: Any, message: Optional[str] = None):
        msg = message or f"Expected {expected}, but got {actual}"
        if actual != expected:
            _fail(msg, actual=actual, expected=expected)
        log.debug(f"Assertion passed: {msg}")

    @staticmethod
    def assert_not_equal(actual: Any, expected: Any, message: Optional[str] = None):
        msg = message or f"Values should not be equal: {actual}"
        if actual == expected:
            _fail(msg, actual=actual, expected=f"not {expected}")
        log.debug(f"Assertion passed: {msg}")

    @staticmethod
    def assert_in(item: Any, container: Any, message: Optional[str] = None):
        msg = message or f"{item} not found in {container}"
        if item not in container:
            _fail(msg, actual=container, expected=item)
        log.debug(f"Assertion passed: {msg}")

    @staticmethod
    def assert_not_in(item: Any, container: Any, message: Optional[str] = None):
        msg = message or f"{item} should not be in {container}"
        if item in container:
            _fail(msg, actual=container, expected=f"not containing {item}")
        log.debug(f"Assertion passed: {msg}")

    @staticmethod
    def assert_is_none(value: Any, message: Optional[str] = None):
        msg = message or f"Expected None, but got {value}"
        if value is not None:
            _fail(msg, actual=value, expected=None)
        log.debug(f"Assertion passed: {msg}")

    @staticmethod
    def assert_is_not_none(value: Any, message: Optional[str] = None):
        msg = message or "Expected non-None value"
        if value is None:
            _fail(msg, actual=value, expected="non-None value")
        log.debug(f"Assertion passed: {msg}")

    @staticmethod
    def assert_greater_than(actual: Any, expected: Any, message: Optional[str] = None):
        msg = message or f"Expected {actual} > {expected}"
        if not (actual > expected):
            _fail(msg, actual=actual, expected=f">{expected}")
        log.debug(f"Assertion passed: {msg}")

    @staticmethod
    def assert_less_than(actual: Any, expected: Any, message: Optional[str] = None):
        msg = message or f"Expected {actual} < {expected}"
        if not (actual < expected):
            _fail(msg, actual=actual, expected=f"<{expected}")
        log.debug(f"Assertion passed: {msg}")

    @staticmethod
    def assert_contains(container: Any, item: Any, message: Optional[str] = None):
        msg = message or f"{container} should contain {item}"
        if item not in container:
            _fail(msg, actual=container, expected=item)
        log.debug(f"Assertion passed: {msg}")

    @staticmethod
    def assert_string_contains(haystack: str, needle: str, message: Optional[str] = None):
        msg = message or f"Expected '{needle}' in '{haystack}'"
        if needle not in haystack:
            _fail(msg, actual=haystack, expected=needle)
        log.debug(f"Assertion passed: {msg}")

    @staticmethod
    def assert_dict_has_key(data: dict, key: str, message: Optional[str] = None):
        msg = message or f"Key '{key}' not found in response"
        if key not in data:
            _fail(msg, actual=list(data.keys()), expected=key)
        log.debug(f"Assertion passed: {msg}")

    @staticmethod
    def assert_regex(pattern: str, string: str, message: Optional[str] = None):
        msg = message or f"{string} should match pattern {pattern}"
        if not re.search(pattern, string):
            _fail(msg, actual=string, expected=pattern)
        log.debug(f"Assertion passed: {msg}")


hard_assert = HardAssertions()

__all__ = ["AssertionError", "SoftAssertions", "HardAssertions", "hard_assert"]
