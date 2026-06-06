"""
Shared base test class for all automation layers.
"""
import pytest
import uuid
from typing import Optional, Dict, Any
from framework.core.logger import Logger
from framework.core.config_manager import config
from framework.reporting.test_result_manager import TestResultManager
from framework.reporting.step_context import step
from framework.utils.test_data_cleanup import cleanup_registry
from framework.utils.assertions import SoftAssertions


class BaseTest:
    """Shared setup, reporting helpers, and teardown for all test types."""

    test_type_label: str = "test"

    @pytest.fixture(autouse=True)
    def setup_test(self, request):
        """Automatic setup and teardown for each test."""
        self.logger = Logger.get_logger(self.__class__.__name__)
        self.test_id = str(uuid.uuid4())[:8]
        self.correlation_id = f"{self.__class__.__name__}_{self.test_id}"

        test_title = getattr(request.node, "test_title", request.node.name)
        self.test_result = TestResultManager(test_title=test_title)
        self.test_result.start_test()
        self.soft_assert = SoftAssertions()

        self.logger.info(
            f"Starting {self.test_type_label}: {request.node.name} [ID: {self.test_id}]"
        )

        self._init_resources(request)
        self._setup()

        self._test_passed = True
        test_error = None

        try:
            yield
        except Exception as e:
            self._test_passed = False
            test_error = str(e)
            raise
        finally:
            try:
                if not self._test_passed:
                    self._capture_failure_artifacts()
            except Exception as artifact_error:
                self.logger.error(f"Failure artifact capture error: {str(artifact_error)}")

            try:
                cleanup_registry.execute_cleanup()
            except Exception as cleanup_error:
                self.logger.error(f"Cleanup execution error: {str(cleanup_error)}")

            self._teardown()
            self._cleanup_resources()

            if self.test_result.has_failed_steps():
                self._test_passed = False

            result_status = "passed" if self._test_passed else "failed"
            self.test_result.end_test(result=result_status, error_message=test_error)
            self.logger.info(
                f"Completed {self.test_type_label}: {request.node.name} "
                f"[ID: {self.test_id}] - {result_status}"
            )

    def _init_resources(self, request):
        """Initialize layer-specific resources. Override in subclasses."""

    def _cleanup_resources(self):
        """Clean up layer-specific resources. Override in subclasses."""

    def _setup(self):
        """Override in subclasses for custom setup."""

    def _teardown(self):
        """Override in subclasses for custom teardown."""

    def _capture_failure_artifacts(self):
        """Override in subclasses to attach failure diagnostics."""

    @property
    def config(self):
        """Get configuration instance."""
        return config

    def set_test_title(self, title: str):
        """Set test title."""
        self.test_result.set_title(title)

    def add_test_data(self, key: str, value: Any):
        """Add test data."""
        self.test_result.add_test_data(key, value)

    def add_test_data_dict(self, data: Dict[str, Any]):
        """Add multiple test data items."""
        self.test_result.add_test_data_dict(data)

    def start_step(self, step_name: str, step_data: Optional[Dict[str, Any]] = None) -> int:
        """Start a new test step and return step index."""
        return self.test_result.start_step(step_name, step_data)

    def complete_step(
        self,
        step_index: int,
        status: str = "passed",
        result: Optional[Any] = None,
        error: Optional[str] = None,
    ):
        """Complete a test step."""
        self.test_result.complete_step(step_index, status, result, error)

    def step(self, step_name: str, step_data: Optional[Dict[str, Any]] = None):
        """Create a step context manager."""
        return step(self.test_result, step_name, step_data)

    def attach_to_allure(self, name: str, content: Any, attachment_type: str = "text"):
        """Attach content to Allure report."""
        try:
            import allure

            attachment_types = {
                "json": allure.attachment_type.JSON,
                "text": allure.attachment_type.TEXT,
                "html": allure.attachment_type.HTML,
            }
            allure.attach(
                str(content),
                name=name,
                attachment_type=attachment_types.get(attachment_type, allure.attachment_type.TEXT),
            )
        except ImportError:
            self.logger.warning("Allure not available for attachment")
