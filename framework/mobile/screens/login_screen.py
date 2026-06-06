"""Login screen object."""
from framework.mobile.base_screen import BaseScreen


class LoginScreen(BaseScreen):
    APP_ID = "com.example.app:id"

    EMAIL_INPUT = f"{APP_ID}/email_input"
    PASSWORD_INPUT = f"{APP_ID}/password_input"
    LOGIN_BUTTON = f"{APP_ID}/login_button"
    DASHBOARD = f"{APP_ID}/dashboard"
    WELCOME_MESSAGE = f"{APP_ID}/welcome_message"

    def login(self, email: str, password: str):
        self.wait_for_element("id", self.EMAIL_INPUT)
        self.send_keys("id", self.EMAIL_INPUT, email)
        self.send_keys("id", self.PASSWORD_INPUT, password)
        self.click("id", self.LOGIN_BUTTON)

    def wait_for_dashboard(self):
        self.wait_for_element("id", self.DASHBOARD)

    def get_welcome_message(self) -> str:
        return self.get_text("id", self.WELCOME_MESSAGE)
