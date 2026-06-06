"""
Mobile UI tests using Appium
"""
import pytest
import allure
from framework.mobile.base_mobile_test import BaseMobileTest
from framework.mobile.screens import LoginScreen, ProductsScreen
from framework.utils.assertions import hard_assert


@allure.epic("Mobile UI Testing")
@allure.feature("Appium Mobile Tests")
@pytest.mark.mobile
class TestMobileUI(BaseMobileTest):
    """Mobile UI tests using Appium"""

    @allure.story("User Authentication")
    @allure.title("Mobile user login flow")
    @pytest.mark.android
    @pytest.mark.smoke_mobile
    def test_mobile_login_android(self):
        login_screen = self.screen_object(LoginScreen)

        with self.step("Log in with valid credentials"):
            login_screen.login("test@example.com", "password123")

        with self.step("Verify successful login") as step_ctx:
            login_screen.wait_for_dashboard()
            welcome_text = login_screen.get_welcome_message()
            hard_assert.assert_string_contains(
                welcome_text, "Welcome", "Welcome message should be displayed"
            )
            step_ctx.set_result(welcome_text)

        login_screen.screenshot("mobile_login_success")

    @allure.story("Product Browsing")
    @allure.title("Browse products on mobile")
    @pytest.mark.android
    def test_browse_products_android(self):
        products_screen = self.screen_object(ProductsScreen)

        with self.step("Open products list"):
            products_screen.open()

        with self.step("Browse products") as step_ctx:
            products_screen.swipe_through_list()
            product_count = products_screen.get_product_count()
            hard_assert.assert_greater_than(product_count, 0, "Products should be displayed")
            step_ctx.set_result(f"{product_count} products displayed")

        products_screen.screenshot("products_list")
