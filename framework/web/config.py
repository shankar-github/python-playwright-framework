"""Web UI layer specific configuration"""
from framework.core.base_config import BaseConfig


class WebSettings(BaseConfig):
    """Web UI-specific configuration settings"""

    web_url: str = ""
    browser: str = "chromium"
    headless: bool = True
    browser_timeout: int = 30000
    page_timeout: int = 30000
    record_trace: bool = True
    record_video: bool = False
