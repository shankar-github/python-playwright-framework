"""Registration page object."""
from typing import Any, Dict
from framework.web.base_page import BasePage


class RegistrationPage(BasePage):
    PATH = "/register"
    DASHBOARD_URL_PATTERN = "**/dashboard"

    FIRST_NAME_TEST_ID = "first-name-input"
    LAST_NAME_TEST_ID = "last-name-input"
    EMAIL_TEST_ID = "email-input"
    PASSWORD_TEST_ID = "password-input"
    CONFIRM_PASSWORD_TEST_ID = "confirm-password-input"
    SUBMIT_TEST_ID = "register-submit"
    SUCCESS_TEST_ID = "success-message"

    def open(self):
        self.navigate(self.PATH)

    def register(self, user_data: Dict[str, Any], password: str):
        self.fill_test_id(self.FIRST_NAME_TEST_ID, user_data["first_name"])
        self.fill_test_id(self.LAST_NAME_TEST_ID, user_data["last_name"])
        self.fill_test_id(self.EMAIL_TEST_ID, user_data["email"])
        self.fill_test_id(self.PASSWORD_TEST_ID, password)
        self.fill_test_id(self.CONFIRM_PASSWORD_TEST_ID, password)
        self.click_test_id(self.SUBMIT_TEST_ID)

    def wait_for_success(self) -> str:
        self.wait_for_url(self.DASHBOARD_URL_PATTERN)
        return self.get_text_test_id(self.SUCCESS_TEST_ID)
