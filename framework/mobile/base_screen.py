"""
Base screen class for Appium Screen Object Model
"""
from typing import Optional, Dict, Any
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from framework.core.logger import Logger
from framework.utils.ui_retry import retry_ui_operation
from framework.utils.redact import redact_selector_value
import allure

log = Logger.get_logger(__name__)


class BaseScreen:
    """Base screen class with common Appium operations"""
    
    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
        self.timeout = 30
    
    def find_element(self, locator_type: str, locator_value: str):
        """Find element by locator"""
        log.debug(f"Finding element: {locator_type}={locator_value}")
        
        locator_map = {
            "id": AppiumBy.ID,
            "xpath": AppiumBy.XPATH,
            "class": AppiumBy.CLASS_NAME,
            "name": AppiumBy.NAME,
            "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
            "android_uiautomator": AppiumBy.ANDROID_UIAUTOMATOR,
            "ios_predicate": AppiumBy.IOS_PREDICATE,
            "ios_class_chain": AppiumBy.IOS_CLASS_CHAIN,
        }
        
        by = locator_map.get(locator_type.lower())
        if not by:
            raise ValueError(f"Unsupported locator type: {locator_type}")
        
        return self.driver.find_element(by, locator_value)
    
    def find_elements(self, locator_type: str, locator_value: str):
        """Find multiple elements by locator"""
        log.debug(f"Finding elements: {locator_type}={locator_value}")
        
        locator_map = {
            "id": AppiumBy.ID,
            "xpath": AppiumBy.XPATH,
            "class": AppiumBy.CLASS_NAME,
            "name": AppiumBy.NAME,
            "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
            "android_uiautomator": AppiumBy.ANDROID_UIAUTOMATOR,
            "ios_predicate": AppiumBy.IOS_PREDICATE,
            "ios_class_chain": AppiumBy.IOS_CLASS_CHAIN,
        }
        
        by = locator_map.get(locator_type.lower())
        if not by:
            raise ValueError(f"Unsupported locator type: {locator_type}")
        
        return self.driver.find_elements(by, locator_value)
    
    @retry_ui_operation(max_attempts=3, wait_min=1.0, wait_max=3.0)
    def click(self, locator_type: str, locator_value: str):
        """Click element with retry for flakiness"""
        log.debug(f"Clicking element: {locator_type}={locator_value}")
        try:
            element = self.find_element(locator_type, locator_value)
            element.click()
        except (TimeoutException, NoSuchElementException) as e:
            log.warning(f"Click failed for {locator_type}={locator_value}: {str(e)}")
            raise
    
    @retry_ui_operation(max_attempts=3, wait_min=1.0, wait_max=3.0)
    def send_keys(self, locator_type: str, locator_value: str, text: str):
        """Send keys to element with retry for flakiness"""
        log.debug(
            f"Sending keys to {locator_type}={locator_value}: "
            f"{redact_selector_value(locator_value, text)}"
        )
        try:
            element = self.find_element(locator_type, locator_value)
            element.send_keys(text)
        except (TimeoutException, NoSuchElementException) as e:
            log.warning(f"Send keys failed for {locator_type}={locator_value}: {str(e)}")
            raise
    
    def clear(self, locator_type: str, locator_value: str):
        """Clear element text"""
        log.debug(f"Clearing element: {locator_type}={locator_value}")
        element = self.find_element(locator_type, locator_value)
        element.clear()
    
    def get_text(self, locator_type: str, locator_value: str) -> str:
        """Get element text"""
        log.debug(f"Getting text from: {locator_type}={locator_value}")
        element = self.find_element(locator_type, locator_value)
        return element.text
    
    def is_displayed(self, locator_type: str, locator_value: str) -> bool:
        """Check if element is displayed"""
        try:
            element = self.find_element(locator_type, locator_value)
            return element.is_displayed()
        except Exception:
            return False
    
    def is_enabled(self, locator_type: str, locator_value: str) -> bool:
        """Check if element is enabled"""
        try:
            element = self.find_element(locator_type, locator_value)
            return element.is_enabled()
        except Exception:
            return False
    
    @retry_ui_operation(max_attempts=3, wait_min=1.0, wait_max=3.0)
    def wait_for_element(self, locator_type: str, locator_value: str, timeout: Optional[int] = None):
        """Wait for element to be present with mobile-optimized waits"""
        from appium.webdriver.common.appiumby import AppiumBy
        from appium.webdriver.support.ui import WebDriverWait
        from appium.webdriver.support import expected_conditions as EC
        
        log.debug(f"Waiting for element: {locator_type}={locator_value}")
        
        locator_map = {
            "id": AppiumBy.ID,
            "xpath": AppiumBy.XPATH,
            "class": AppiumBy.CLASS_NAME,
            "name": AppiumBy.NAME,
            "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
        }
        
        by = locator_map.get(locator_type.lower())
        if not by:
            raise ValueError(f"Unsupported locator type: {locator_type}")
        
        # Mobile-optimized wait: check for presence first, then visibility
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        
        # First wait for element to be present in DOM
        wait.until(EC.presence_of_element_located((by, locator_value)))
        
        # Then wait for element to be visible (mobile-specific)
        wait.until(EC.visibility_of_element_located((by, locator_value)))
        
        log.debug(f"Element {locator_type}={locator_value} is present and visible")
    
    def wait_for_element_clickable(self, locator_type: str, locator_value: str, timeout: Optional[int] = None):
        """Wait for element to be clickable (mobile-optimized)"""
        from appium.webdriver.common.appiumby import AppiumBy
        from appium.webdriver.support.ui import WebDriverWait
        from appium.webdriver.support import expected_conditions as EC
        
        log.debug(f"Waiting for element to be clickable: {locator_type}={locator_value}")
        
        locator_map = {
            "id": AppiumBy.ID,
            "xpath": AppiumBy.XPATH,
            "class": AppiumBy.CLASS_NAME,
            "name": AppiumBy.NAME,
            "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
        }
        
        by = locator_map.get(locator_type.lower())
        if not by:
            raise ValueError(f"Unsupported locator type: {locator_type}")
        
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        wait.until(EC.element_to_be_clickable((by, locator_value)))
        log.debug(f"Element {locator_type}={locator_value} is clickable")
    
    def wait_for_text_in_element(self, locator_type: str, locator_value: str, text: str, timeout: Optional[int] = None):
        """Wait for text to appear in element (mobile-optimized)"""
        from appium.webdriver.common.appiumby import AppiumBy
        from appium.webdriver.support.ui import WebDriverWait
        from appium.webdriver.support import expected_conditions as EC
        
        log.debug(f"Waiting for text '{text}' in element: {locator_type}={locator_value}")
        
        locator_map = {
            "id": AppiumBy.ID,
            "xpath": AppiumBy.XPATH,
            "class": AppiumBy.CLASS_NAME,
            "name": AppiumBy.NAME,
            "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
        }
        
        by = locator_map.get(locator_type.lower())
        if not by:
            raise ValueError(f"Unsupported locator type: {locator_type}")
        
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        wait.until(EC.text_to_be_present_in_element((by, locator_value), text))
        log.debug(f"Text '{text}' found in element {locator_type}={locator_value}")
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1000):
        """Swipe gesture"""
        log.debug(f"Swipe from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        self.driver.swipe(start_x, start_y, end_x, end_y, duration)
    
    def swipe_up(self, duration: int = 1000):
        """Swipe up"""
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = int(size['height'] * 0.8)
        end_y = int(size['height'] * 0.2)
        self.swipe(start_x, start_y, start_x, end_y, duration)
    
    def swipe_down(self, duration: int = 1000):
        """Swipe down"""
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = int(size['height'] * 0.2)
        end_y = int(size['height'] * 0.8)
        self.swipe(start_x, start_y, start_x, end_y, duration)
    
    def tap(self, x: int, y: int):
        """Tap at coordinates"""
        log.debug(f"Tapping at ({x}, {y})")
        self.driver.tap([(x, y)])
    
    def screenshot(self, name: str = "screenshot"):
        """Take screenshot"""
        screenshot = self.driver.get_screenshot_as_png()
        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG
        )
        log.debug(f"Screenshot taken: {name}")
    
    def get_page_source(self) -> str:
        """Get page source"""
        return self.driver.page_source
    
    def hide_keyboard(self):
        """Hide keyboard"""
        log.debug("Hiding keyboard")
        self.driver.hide_keyboard()
    
    def press_keycode(self, keycode: int):
        """Press Android keycode"""
        log.debug(f"Pressing keycode: {keycode}")
        self.driver.press_keycode(keycode)
    
    def background_app(self, seconds: int):
        """Background app for specified seconds"""
        log.debug(f"Backgrounding app for {seconds} seconds")
        self.driver.background_app(seconds)
