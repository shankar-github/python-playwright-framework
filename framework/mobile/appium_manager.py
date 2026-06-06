"""
Appium driver management
"""
from typing import Optional, Dict, Any
from appium import webdriver
from appium.options.common import AppiumOptions
from framework.core.config_manager import config
from framework.core.logger import log


class AppiumManager:
    """Manages Appium driver instances"""
    
    def __init__(self):
        self.driver: Optional[webdriver.Remote] = None
    
    def start_driver(
        self,
        platform: str,
        app_path: Optional[str] = None,
        app_package: Optional[str] = None,
        app_activity: Optional[str] = None,
        bundle_id: Optional[str] = None,
        device_name: Optional[str] = None,
        platform_version: Optional[str] = None,
        **kwargs
    ):
        """Start Appium driver"""
        server_url = config.mobile.appium_server_url
        
        options = AppiumOptions()
        
        if platform.lower() == "android":
            options.platform_name = "Android"
            options.device_name = device_name or config.mobile.android_device_name
            options.platform_version = platform_version or config.mobile.android_platform_version
            
            if app_path:
                options.app = app_path
            if app_package:
                options.app_package = app_package
            if app_activity:
                options.app_activity = app_activity
            
            # Android-specific options
            options.automation_name = "UiAutomator2"
            options.no_reset = kwargs.get("no_reset", False)
            options.full_reset = kwargs.get("full_reset", False)
        
        elif platform.lower() == "ios":
            options.platform_name = "iOS"
            options.device_name = device_name or config.mobile.ios_device_name
            options.platform_version = platform_version or config.mobile.ios_platform_version
            
            if app_path:
                options.app = app_path
            if bundle_id:
                options.bundle_id = bundle_id
            
            # iOS-specific options
            options.automation_name = "XCUITest"
            options.no_reset = kwargs.get("no_reset", False)
            options.full_reset = kwargs.get("full_reset", False)
        
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Add any additional options
        for key, value in kwargs.items():
            if key not in ["no_reset", "full_reset"]:
                setattr(options, key, value)
        
        log.info(f"Starting Appium driver for {platform}")
        log.debug(f"Server URL: {server_url}")
        log.debug(f"Options: {options.as_dict()}")
        
        self.driver = webdriver.Remote(server_url, options=options)
        log.info("Appium driver started successfully")
    
    def get_driver(self) -> webdriver.Remote:
        """Get current driver"""
        if not self.driver:
            raise RuntimeError("Driver not started. Call start_driver() first.")
        return self.driver
    
    def close_driver(self):
        """Close driver"""
        if self.driver:
            log.info("Closing Appium driver")
            self.driver.quit()
            self.driver = None
