"""
Base page class for Playwright Page Object Model
"""
from typing import Optional, List
from playwright.sync_api import Page, expect, Locator, TimeoutError as PlaywrightTimeoutError
from framework.core.config_manager import config
from framework.core.logger import log
from framework.utils.ui_retry import retry_ui_operation
from framework.utils.redact import redact_selector_value
import allure


class BasePage:
    """Base page class with common Playwright operations"""
    
    def __init__(self, page: Page):
        self.page = page
        self.base_url = config.web.web_url
        self.timeout = config.web.page_timeout
    
    def navigate(self, url: str = ""):
        """Navigate to URL"""
        full_url = f"{self.base_url}/{url.lstrip('/')}" if url else self.base_url
        log.info(f"Navigating to: {full_url}")
        self.page.goto(full_url, timeout=self.timeout)
        self.page.wait_for_load_state("domcontentloaded")
    
    @retry_ui_operation(max_attempts=3, wait_min=1.0, wait_max=3.0)
    def click(self, selector: str, timeout: Optional[int] = None):
        """Click element with retry for flakiness"""
        log.debug(f"Clicking element: {selector}")
        try:
            self.page.click(selector, timeout=timeout or self.timeout)
        except PlaywrightTimeoutError as e:
            log.warning(f"Click timeout for {selector}: {str(e)}")
            raise

    @retry_ui_operation(max_attempts=3, wait_min=1.0, wait_max=3.0)
    def click_test_id(self, test_id: str, timeout: Optional[int] = None):
        """Click element located by data-testid."""
        log.debug(f"Clicking [data-testid={test_id}]")
        self.page.get_by_test_id(test_id).click(timeout=timeout or self.timeout)

    @retry_ui_operation(max_attempts=3, wait_min=1.0, wait_max=3.0)
    def click_role(self, role: str, name: Optional[str] = None, timeout: Optional[int] = None, **kwargs):
        """Click element located by ARIA role."""
        locator = self.page.get_by_role(role, name=name, **kwargs) if name else self.page.get_by_role(role, **kwargs)
        log.debug(f"Clicking role={role} name={name}")
        locator.click(timeout=timeout or self.timeout)
    
    @retry_ui_operation(max_attempts=3, wait_min=1.0, wait_max=3.0)
    def fill(self, selector: str, value: str, timeout: Optional[int] = None):
        """Fill input field with retry for flakiness"""
        log.debug(f"Filling {selector} with value: {redact_selector_value(selector, value)}")
        try:
            self.page.fill(selector, value, timeout=timeout or self.timeout)
        except PlaywrightTimeoutError as e:
            log.warning(f"Fill timeout for {selector}: {str(e)}")
            raise

    @retry_ui_operation(max_attempts=3, wait_min=1.0, wait_max=3.0)
    def fill_test_id(self, test_id: str, value: str, timeout: Optional[int] = None):
        """Fill input located by data-testid."""
        log.debug(f"Filling [data-testid={test_id}] with value: {redact_selector_value(test_id, value)}")
        self.page.get_by_test_id(test_id).fill(value, timeout=timeout or self.timeout)

    @retry_ui_operation(max_attempts=3, wait_min=1.0, wait_max=3.0)
    def fill_role(self, role: str, value: str, name: Optional[str] = None, timeout: Optional[int] = None, **kwargs):
        """Fill input located by ARIA role."""
        locator = self.page.get_by_role(role, name=name, **kwargs) if name else self.page.get_by_role(role, **kwargs)
        log.debug(f"Filling role={role} name={name} with value: {redact_selector_value(role, value)}")
        locator.fill(value, timeout=timeout or self.timeout)
    
    def type(self, selector: str, text: str, delay: int = 0, timeout: Optional[int] = None):
        """Type text into element sequentially."""
        log.debug(f"Typing into {selector}: {redact_selector_value(selector, text)}")
        self.page.locator(selector).press_sequentially(text, delay=delay, timeout=timeout or self.timeout)
    
    def select_option(self, selector: str, value: str, timeout: Optional[int] = None):
        """Select option from dropdown"""
        log.debug(f"Selecting option {value} from {selector}")
        self.page.select_option(selector, value, timeout=timeout or self.timeout)
    
    def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """Get text content of element"""
        log.debug(f"Getting text from: {selector}")
        return self.page.locator(selector).inner_text(timeout=timeout or self.timeout)

    def get_text_test_id(self, test_id: str, timeout: Optional[int] = None) -> str:
        """Get text from element located by data-testid."""
        return self.page.get_by_test_id(test_id).inner_text(timeout=timeout or self.timeout)
    
    def get_attribute(self, selector: str, attribute: str, timeout: Optional[int] = None) -> Optional[str]:
        """Get attribute value"""
        log.debug(f"Getting attribute {attribute} from: {selector}")
        return self.page.get_attribute(selector, attribute, timeout=timeout or self.timeout)
    
    def is_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Check if element is visible"""
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout or self.timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def is_enabled(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Check if element is enabled"""
        try:
            return self.page.locator(selector).is_enabled(timeout=timeout or self.timeout)
        except PlaywrightTimeoutError:
            return False
    
    @retry_ui_operation(max_attempts=3, wait_min=1.0, wait_max=3.0)
    def wait_for_element(self, selector: str, timeout: Optional[int] = None):
        """Wait for element to be visible with retry for flakiness"""
        log.debug(f"Waiting for element: {selector}")
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout or self.timeout)
        except PlaywrightTimeoutError as e:
            log.warning(f"Wait timeout for {selector}: {str(e)}")
            raise

    @retry_ui_operation(max_attempts=3, wait_min=1.0, wait_max=3.0)
    def wait_for_test_id(self, test_id: str, timeout: Optional[int] = None):
        """Wait for element located by data-testid."""
        self.page.get_by_test_id(test_id).wait_for(state="visible", timeout=timeout or self.timeout)
    
    def wait_for_text(self, selector: str, text: str, timeout: Optional[int] = None):
        """Wait for element to contain text"""
        log.debug(f"Waiting for text '{text}' in: {selector}")
        expect(self.page.locator(selector)).to_contain_text(text, timeout=timeout or self.timeout)
    
    def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None):
        """Wait for URL to match pattern"""
        log.debug(f"Waiting for URL pattern: {url_pattern}")
        self.page.wait_for_url(url_pattern, timeout=timeout or self.timeout)
    
    def screenshot(self, name: str = "screenshot"):
        """Take screenshot"""
        screenshot = self.page.screenshot()
        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG
        )
        log.debug(f"Screenshot taken: {name}")
    
    def get_title(self) -> str:
        """Get page title"""
        return self.page.title()
    
    def get_url(self) -> str:
        """Get current URL"""
        return self.page.url
    
    def go_back(self):
        """Navigate back"""
        log.debug("Navigating back")
        self.page.go_back()
    
    def go_forward(self):
        """Navigate forward"""
        log.debug("Navigating forward")
        self.page.go_forward()
    
    def refresh(self):
        """Refresh page"""
        log.debug("Refreshing page")
        self.page.reload()
        self.page.wait_for_load_state("domcontentloaded")
    
    def switch_to_tab(self, index: int):
        """Switch to tab by index"""
        log.debug(f"Switching to tab {index}")
        self.page.context.pages[index].bring_to_front()
    
    def close_tab(self, index: int):
        """Close tab by index"""
        log.debug(f"Closing tab {index}")
        self.page.context.pages[index].close()
    
    def get_all_tabs(self) -> List[Page]:
        """Get all open tabs"""
        return self.page.context.pages
    
    def execute_script(self, script: str):
        """Execute JavaScript"""
        log.debug(f"Executing script: {script[:50]}...")
        return self.page.evaluate(script)
    
    def wait_for_load_state(self, state: str = "networkidle"):
        """Wait for page load state"""
        self.page.wait_for_load_state(state)
    
    def locator(self, selector: str) -> Locator:
        """Get locator for element"""
        return self.page.locator(selector)

    def locator_test_id(self, test_id: str) -> Locator:
        """Get locator for data-testid element."""
        return self.page.get_by_test_id(test_id)

    def set_input_files(self, selector: str, file_path: str, timeout: Optional[int] = None):
        """Set files on a file input element"""
        log.debug(f"Setting input files on {selector}: {file_path}")
        self.page.locator(selector).set_input_files(file_path, timeout=timeout or self.timeout)

    def set_input_files_test_id(self, test_id: str, file_path: str, timeout: Optional[int] = None):
        """Set files on a file input located by data-testid."""
        self.page.get_by_test_id(test_id).set_input_files(file_path, timeout=timeout or self.timeout)
