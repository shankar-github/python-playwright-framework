"""Contact page object."""
from typing import List
from framework.web.base_page import BasePage


class ContactPage(BasePage):
    PATH = "/contact"

    SUBMIT_TEST_ID = "contact-submit"
    ERROR_TEST_ID = "error-message"

    def open(self):
        self.navigate(self.PATH)

    def submit_empty_form(self):
        self.click_test_id(self.SUBMIT_TEST_ID)

    def get_validation_errors(self) -> List[str]:
        self.wait_for_test_id(self.ERROR_TEST_ID)
        return [msg.inner_text() for msg in self.locator_test_id(self.ERROR_TEST_ID).all()]
