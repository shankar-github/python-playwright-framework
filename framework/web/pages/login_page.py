"""Login page object."""
from typing import Optional
from framework.web.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/login"
    DASHBOARD_URL_PATTERN = "**/dashboard"

    EMAIL_TEST_ID = "email-input"
    PASSWORD_TEST_ID = "password-input"
    FIRST_NAME_TEST_ID = "first-name-input"
    SUBMIT_TEST_ID = "login-submit"
    WELCOME_TEST_ID = "welcome-message"

    def open(self):
        self.navigate(self.PATH)

    def login(self, email: str, password: str, first_name: Optional[str] = None):
        self.fill_test_id(self.EMAIL_TEST_ID, email)
        self.fill_test_id(self.PASSWORD_TEST_ID, password)
        if first_name:
            self.page.locator(f'[data-testid="{self.FIRST_NAME_TEST_ID}"]').evaluate(
                "(element, value) => { element.value = value; }",
                first_name,
            )
        self.click_test_id(self.SUBMIT_TEST_ID)

    def wait_for_dashboard(self):
        self.wait_for_url(self.DASHBOARD_URL_PATTERN)

    def get_welcome_message(self) -> str:
        return self.get_text_test_id(self.WELCOME_TEST_ID)
