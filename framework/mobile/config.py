"""Mobile UI layer specific configuration"""
from framework.core.base_config import BaseConfig


class MobileSettings(BaseConfig):
    """Mobile UI-specific configuration settings"""

    appium_server_url: str = "http://localhost:4723"
    android_platform_version: str = "13.0"
    ios_platform_version: str = "16.0"
    android_device_name: str = "emulator-5554"
    ios_device_name: str = "iPhone 14"
