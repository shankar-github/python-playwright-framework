"""Home page object with site-wide navigation."""
from framework.web.base_page import BasePage


class HomePage(BasePage):
    PATH = "/"

    PRODUCTS_LINK_TEST_ID = "products-link"
    ABOUT_LINK_TEST_ID = "about-link"
    PRODUCTS_URL_PATTERN = "**/products"
    ABOUT_URL_PATTERN = "**/about"

    def open(self):
        self.navigate(self.PATH)

    def go_to_products(self):
        self.click_test_id(self.PRODUCTS_LINK_TEST_ID)
        self.wait_for_url(self.PRODUCTS_URL_PATTERN)

    def go_to_about(self):
        self.click_test_id(self.ABOUT_LINK_TEST_ID)
        self.wait_for_url(self.ABOUT_URL_PATTERN)
