"""
Web UI tests using Playwright
"""
import pytest
import allure
from framework.web.base_web_test import BaseWebTest
from framework.web.pages import LoginPage, ProductsPage
from framework.utils.assertions import hard_assert


@allure.epic("Web UI Testing")
@allure.feature("Playwright Web Tests")
@pytest.mark.web
class TestWebUI(BaseWebTest):
    """Web UI tests using Playwright"""

    @allure.story("User Authentication")
    @allure.title("User login flow")
    @pytest.mark.smoke
    def test_user_login(self):
        """Test user login flow"""
        login_page = self.page_object(LoginPage)
        credentials = {"email": "test@example.com", "password": "password123"}

        self.set_test_title("User Login Flow - Web UI")
        self.add_test_data("credentials", credentials)

        with self.step("Navigate to login page") as step_ctx:
            login_page.open()
            step_ctx.set_result(login_page.get_url())

        with self.step("Log in with valid credentials") as step_ctx:
            login_page.login(credentials["email"], credentials["password"])
            step_ctx.set_result("Credentials submitted")

        with self.step("Verify redirect to dashboard") as step_ctx:
            login_page.wait_for_dashboard()
            step_ctx.set_result(login_page.get_url())

        with self.step("Verify welcome message") as step_ctx:
            welcome_text = login_page.get_welcome_message()
            hard_assert.assert_string_contains(
                welcome_text, "Welcome", "Welcome message should be displayed"
            )
            step_ctx.set_result(welcome_text)

        login_page.screenshot("login_success")

    @allure.story("Product Search")
    @allure.title("Search for product")
    def test_product_search(self):
        """Test product search functionality"""
        products_page = self.page_object(ProductsPage)

        with self.step("Open products page"):
            products_page.open()

        with self.step("Search for a product"):
            products_page.search("laptop")

        with self.step("Verify search results") as step_ctx:
            product_count = products_page.get_product_count()
            hard_assert.assert_greater_than(product_count, 0, "Search should return results")
            step_ctx.set_result(f"{product_count} products found")

        products_page.screenshot("search_results")
