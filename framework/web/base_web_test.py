"""
Base test class for Web UI tests
"""
from typing import Type, TypeVar
from framework.core.base_test import BaseTest
from framework.core.config_manager import config
from framework.web.browser_manager import BrowserManager
from framework.web.base_page import BasePage

TPage = TypeVar("TPage", bound=BasePage)

_SHARED_BROWSER_MARKERS = ("smoke", "smoke_e2e", "regression")


class BaseWebTest(BaseTest):
    """Base test class for Web UI tests."""

    test_type_label = "Web UI test"

    def _uses_shared_browser(self, request) -> bool:
        return any(request.node.get_closest_marker(marker) for marker in _SHARED_BROWSER_MARKERS)

    def _init_resources(self, request):
        if self._uses_shared_browser(request):
            self.browser_manager = request.getfixturevalue("session_browser_manager")
            self.browser_manager.create_context()
            self._owns_browser = False
        else:
            self.browser_manager = BrowserManager()
            self.browser_manager.start_browser(
                browser_type=config.web.browser,
                headless=config.web.headless,
            )
            self._owns_browser = True
        self.page = BasePage(self.browser_manager.get_page())

    def _cleanup_resources(self):
        if getattr(self, "_owns_browser", True):
            self.browser_manager.close_browser()
        else:
            self.browser_manager.close_context()

    def _capture_failure_artifacts(self):
        self.browser_manager.capture_failure_artifacts(self.test_id)

    def page_object(self, page_cls: Type[TPage]) -> TPage:
        """Create a page object bound to the current browser page."""
        return page_cls(self.page.page)

    @property
    def web_config(self):
        """Get Web-specific configuration."""
        return config.web
