"""iOS login screen object."""
from framework.mobile.base_screen import BaseScreen


class IosLoginScreen(BaseScreen):
    EMAIL_FIELD = "type == 'XCUIElementTypeTextField' AND label == 'Email'"
    PASSWORD_FIELD = "type == 'XCUIElementTypeSecureTextField' AND label == 'Password'"
    LOGIN_BUTTON = "type == 'XCUIElementTypeButton' AND label == 'Login'"
    WELCOME_TEXT = "type == 'XCUIElementTypeStaticText' AND label CONTAINS 'Welcome'"

    def login(self, email: str, password: str):
        self.wait_for_element("ios_predicate", self.EMAIL_FIELD)
        self.send_keys("ios_predicate", self.EMAIL_FIELD, email)
        self.send_keys("ios_predicate", self.PASSWORD_FIELD, password)
        self.click("ios_predicate", self.LOGIN_BUTTON)

    def wait_for_success(self) -> str:
        self.wait_for_element("ios_predicate", self.WELCOME_TEXT)
        return self.get_text("ios_predicate", self.WELCOME_TEXT)
