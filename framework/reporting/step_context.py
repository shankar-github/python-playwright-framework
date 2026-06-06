"""
Context manager for test steps - cleaner API than step1, step2 variables
"""
from typing import Optional, Dict, Any
import allure
from framework.reporting.test_result_manager import TestResultManager


class StepContext:
    """Context manager for test steps with live Allure step nesting."""

    def __init__(
        self,
        test_result: TestResultManager,
        step_name: str,
        step_data: Optional[Dict[str, Any]] = None,
    ):
        self.test_result = test_result
        self.step_name = step_name
        self.step_data = step_data
        self.step_index: Optional[int] = None
        self._success = True
        self._error: Optional[str] = None
        self._result: Optional[Any] = None
        self._allure_step = None

    def __enter__(self):
        self.step_index = self.test_result.start_step(self.step_name, self.step_data)
        self._allure_step = allure.step(self.step_name)
        self._allure_step.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._allure_step is not None:
            self._allure_step.__exit__(exc_type, exc_val, exc_tb)

        if exc_type is not None:
            self._success = False
            self._error = str(exc_val) if exc_val else str(exc_type)
            status = "failed"
        else:
            status = "passed" if self._success else "failed"

        self.test_result.complete_step(
            self.step_index,
            status=status,
            result=self._result,
            error=self._error,
        )
        return False

    def set_result(self, result: Any):
        self._result = result

    def set_error(self, error: str):
        self._error = error
        self._success = False

    def mark_failed(self):
        self._success = False


def step(test_result: TestResultManager, step_name: str, step_data: Optional[Dict[str, Any]] = None) -> StepContext:
    """Create a step context manager."""
    return StepContext(test_result, step_name, step_data)
