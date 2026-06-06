"""
Base test class for Mobile UI tests
"""
import os
from typing import Type, TypeVar
import pytest
from framework.core.base_test import BaseTest
from framework.core.config_manager import config
from framework.mobile.appium_manager import AppiumManager
from framework.mobile.base_screen import BaseScreen

TScreen = TypeVar("TScreen", bound=BaseScreen)


class BaseMobileTest(BaseTest):
    """Base test class for Mobile UI tests."""

    test_type_label = "Mobile UI test"

    def _init_resources(self, request):
        if os.getenv("SKIP_APPIUM", "").lower() in ("1", "true", "yes"):
            pytest.skip("Appium not available (SKIP_APPIUM is set)")

        platform = "android"
        if hasattr(request.node, "iter_markers"):
            for marker in request.node.iter_markers():
                if marker.name == "ios":
                    platform = "ios"
                    break

        self.appium_manager = AppiumManager()
        if platform == "android":
            self.appium_manager.start_driver(
                platform=platform,
                device_name=config.mobile.android_device_name,
                platform_version=config.mobile.android_platform_version,
            )
        else:
            self.appium_manager.start_driver(
                platform=platform,
                device_name=config.mobile.ios_device_name,
                platform_version=config.mobile.ios_platform_version,
            )
        self.screen = BaseScreen(self.appium_manager.get_driver())

    def _cleanup_resources(self):
        self.appium_manager.close_driver()

    def _capture_failure_artifacts(self):
        try:
            self.screen.screenshot("mobile_failure")
        except Exception as error:
            self.logger.warning(f"Mobile failure screenshot failed: {error}")

    def screen_object(self, screen_cls: Type[TScreen]) -> TScreen:
        """Create a screen object bound to the current Appium driver."""
        return screen_cls(self.appium_manager.get_driver())

    @property
    def mobile_config(self):
        """Get Mobile-specific configuration."""
        return config.mobile
