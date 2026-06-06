"""
Retry utilities for UI operations to handle flakiness
"""
from functools import wraps
from typing import Callable
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryCallState
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from framework.core.logger import log

try:
    import allure
    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False


def retry_ui_operation(
    max_attempts: int = 3,
    wait_min: float = 1.0,
    wait_max: float = 5.0
):
    """Decorator to retry UI operations that may be flaky."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def before_sleep_callback(retry_state: RetryCallState):
            attempt = retry_state.attempt_number
            log.warning(f"Retrying UI operation {func.__name__} (attempt {attempt}/{max_attempts})")
            if ALLURE_AVAILABLE:
                try:
                    with allure.step(f"Retry attempt {attempt} for {func.__name__}"):
                        allure.attach(
                            f"Retry attempt {attempt} of {max_attempts}",
                            name=f"{func.__name__} Retry",
                            attachment_type=allure.attachment_type.TEXT
                        )
                except Exception:
                    pass

        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=wait_min, max=wait_max),
            retry=retry_if_exception_type(PlaywrightTimeoutError),
            reraise=True,
            before_sleep=before_sleep_callback
        )
        def wrapper(*args, **kwargs):
            log.debug(f"Executing UI operation: {func.__name__}")
            return func(*args, **kwargs)

        return wrapper
    return decorator
