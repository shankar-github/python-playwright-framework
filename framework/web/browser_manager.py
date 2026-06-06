"""
Browser management for Playwright
"""
from pathlib import Path
from typing import Optional
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from framework.core.config_manager import config
from framework.core.logger import log
import allure


class BrowserManager:
    """Manages browser instances and contexts"""

    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._tracing_started = False
        self._browser_launched = False

    def launch_browser(
        self,
        browser_type: Optional[str] = None,
        headless: Optional[bool] = None,
        **kwargs
    ):
        """Launch browser process without creating a context."""
        if self._browser_launched:
            return

        browser_type = browser_type or config.web.browser
        headless = headless if headless is not None else config.web.headless

        log.info(f"Starting {browser_type} browser (headless={headless})")

        self.playwright = sync_playwright().start()

        if browser_type == "chromium":
            self.browser = self.playwright.chromium.launch(headless=headless, **kwargs)
        elif browser_type == "firefox":
            self.browser = self.playwright.firefox.launch(headless=headless, **kwargs)
        elif browser_type == "webkit":
            self.browser = self.playwright.webkit.launch(headless=headless, **kwargs)
        else:
            raise ValueError(f"Unsupported browser: {browser_type}")

        self._browser_launched = True
        log.info("Browser launched successfully")

    def create_context(self, **kwargs):
        """Create a new browser context and page."""
        if not self.browser:
            raise RuntimeError("Browser not launched. Call launch_browser() first.")

        if self.context:
            self.close_context()

        context_kwargs = {
            "viewport": {"width": 1920, "height": 1080},
            "ignore_https_errors": kwargs.get("ignore_https_errors", False),
        }
        if config.web.record_video:
            video_dir = Path("reports/videos")
            video_dir.mkdir(parents=True, exist_ok=True)
            context_kwargs["record_video_dir"] = str(video_dir)

        self.context = self.browser.new_context(
            **context_kwargs,
            **{k: v for k, v in kwargs.items() if k != "ignore_https_errors"}
        )

        if config.web.record_trace:
            self.context.tracing.start(screenshots=True, snapshots=True, sources=True)
            self._tracing_started = True

        self.page = self.context.new_page()
        log.info("Browser context created")

    def start_browser(
        self,
        browser_type: Optional[str] = None,
        headless: Optional[bool] = None,
        **kwargs
    ):
        """Launch browser and create an initial context."""
        self.launch_browser(browser_type=browser_type, headless=headless, **kwargs)
        self.create_context(**kwargs)

    def get_page(self) -> Page:
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        return self.page

    def new_page(self) -> Page:
        if not self.context:
            raise RuntimeError("Browser context not available. Call create_context() first.")
        self.page = self.context.new_page()
        return self.page

    def capture_failure_artifacts(self, test_id: str):
        """Capture screenshot, trace, and video on test failure."""
        if self.page:
            screenshot = self.page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name="Failure Screenshot",
                attachment_type=allure.attachment_type.PNG,
            )

        if self.context and self._tracing_started:
            trace_dir = Path("reports/traces")
            trace_dir.mkdir(parents=True, exist_ok=True)
            trace_path = trace_dir / f"{test_id}.zip"
            self.context.tracing.stop(path=str(trace_path))
            self._tracing_started = False
            allure.attach.file(
                str(trace_path),
                name="Playwright Trace",
                attachment_type=allure.attachment_type.ZIP,
            )

        if self.page and self.page.video:
            try:
                video_path = self.page.video.path()
                if video_path:
                    self.page.close()
                    allure.attach.file(
                        video_path,
                        name="Failure Video",
                        attachment_type=allure.attachment_type.WEBM,
                    )
            except Exception as video_error:
                log.warning(f"Could not attach failure video: {video_error}")

    def close_context(self):
        """Close the active context while keeping the browser process alive."""
        if self.context and self._tracing_started:
            self.context.tracing.stop()
            self._tracing_started = False

        if self.context:
            self.context.close()
            self.context = None
            self.page = None
            log.debug("Browser context closed")

    def close_browser(self):
        self.close_context()

        if self.browser:
            log.info("Closing browser")
            self.browser.close()
            self.browser = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None

        self._browser_launched = False

    def take_screenshot(self, name: str = "screenshot"):
        if not self.page:
            raise RuntimeError("No page available")

        screenshot = self.page.screenshot()
        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG
        )
        log.debug(f"Screenshot taken: {name}")
