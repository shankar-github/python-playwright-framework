"""Registration screen object."""
from typing import Any, Dict
from framework.mobile.base_screen import BaseScreen


class RegistrationScreen(BaseScreen):
    APP_ID = "com.example.app:id"

    REGISTER_BUTTON = f"{APP_ID}/register_button"
    REGISTRATION_FORM = f"{APP_ID}/registration_form"
    FIRST_NAME_INPUT = f"{APP_ID}/first_name_input"
    LAST_NAME_INPUT = f"{APP_ID}/last_name_input"
    EMAIL_INPUT = f"{APP_ID}/email_input"
    PASSWORD_INPUT = f"{APP_ID}/password_input"
    SUBMIT_BUTTON = f"{APP_ID}/submit_button"
    WELCOME_SCREEN = f"{APP_ID}/welcome_screen"
    WELCOME_MESSAGE = f"{APP_ID}/welcome_message"

    def open(self):
        self.click("id", self.REGISTER_BUTTON)
        self.wait_for_element("id", self.REGISTRATION_FORM)

    def register(self, user_data: Dict[str, Any], password: str):
        self.send_keys("id", self.FIRST_NAME_INPUT, user_data["first_name"])
        self.send_keys("id", self.LAST_NAME_INPUT, user_data["last_name"])
        self.send_keys("id", self.EMAIL_INPUT, user_data["email"])
        self.send_keys("id", self.PASSWORD_INPUT, password)
        self.click("id", self.SUBMIT_BUTTON)

    def wait_for_success(self) -> str:
        self.wait_for_element("id", self.WELCOME_SCREEN)
        return self.get_text("id", self.WELCOME_MESSAGE)
