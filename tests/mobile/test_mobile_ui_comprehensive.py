"""
Comprehensive Mobile UI test examples
"""
import pytest
import allure
from framework.mobile.base_mobile_test import BaseMobileTest
from framework.mobile.screens import (
    RegistrationScreen,
    ProductsScreen,
    CarouselScreen,
    IosLoginScreen,
    NavigationScreen,
)
from framework.utils.assertions import hard_assert
from framework.utils.test_data import test_data


@allure.epic("Mobile UI Testing")
@allure.feature("Appium Mobile Tests - Comprehensive Examples")
@pytest.mark.mobile
@pytest.mark.regression
class TestMobileUIComprehensive(BaseMobileTest):
    """Comprehensive Mobile UI test examples"""

    @allure.story("User Registration")
    @allure.title("Mobile user registration flow")
    @pytest.mark.android
    @pytest.mark.smoke_mobile
    def test_mobile_user_registration(self):
        registration = self.screen_object(RegistrationScreen)
        user_data = test_data.generate_user_data()

        self.set_test_title("Mobile User Registration Flow")
        self.add_test_data("user_data", user_data)

        with self.step("Open registration screen"):
            registration.open()

        with self.step("Register a new user"):
            registration.register(user_data, "SecurePass123!")

        with self.step("Verify registration success") as step_ctx:
            welcome_text = registration.wait_for_success()
            hard_assert.assert_string_contains(
                welcome_text, "Welcome", "Registration should be successful"
            )
            step_ctx.set_result(welcome_text)

        registration.screenshot("mobile_registration_success")

    @allure.story("Gestures")
    @allure.title("Test swipe gestures")
    @pytest.mark.android
    def test_swipe_gestures(self):
        carousel = self.screen_object(CarouselScreen)

        self.set_test_title("Test Swipe Gestures")

        with self.step("Open carousel"):
            carousel.open()

        with self.step("Swipe through carousel"):
            carousel.swipe_next()
            carousel.swipe_previous()

        carousel.screenshot("swipe_gestures")

    @allure.story("Product Browsing")
    @allure.title("Browse and filter products on mobile")
    @pytest.mark.android
    def test_browse_and_filter_products(self):
        products = self.screen_object(ProductsScreen)

        self.set_test_title("Browse and Filter Products on Mobile")

        with self.step("Open products list"):
            products.open()

        with self.step("Apply category filter"):
            products.apply_category_filter()

        with self.step("Verify filtered results") as step_ctx:
            product_count = products.get_product_count()
            hard_assert.assert_greater_than(
                product_count, 0, "Filtered products should be displayed"
            )
            step_ctx.set_result(f"Found {product_count} filtered products")

        products.screenshot("filtered_products")

    @allure.story("iOS Tests")
    @allure.title("iOS user login flow")
    @pytest.mark.ios
    @pytest.mark.smoke_mobile
    def test_ios_user_login(self):
        login_screen = self.screen_object(IosLoginScreen)
        credentials = {"email": "test@example.com", "password": "password123"}

        self.set_test_title("iOS User Login Flow")
        self.add_test_data("credentials", credentials)

        with self.step("Log in on iOS"):
            login_screen.login(credentials["email"], credentials["password"])

        with self.step("Verify login success") as step_ctx:
            welcome_text = login_screen.wait_for_success()
            hard_assert.assert_string_contains(welcome_text, "Welcome", "Login should be successful")
            step_ctx.set_result(welcome_text)

        login_screen.screenshot("ios_login_success")

    @allure.story("Navigation")
    @allure.title("Test mobile app navigation")
    @pytest.mark.android
    def test_mobile_navigation(self):
        navigation = self.screen_object(NavigationScreen)

        self.set_test_title("Mobile App Navigation Test")

        with self.step("Navigate to home screen"):
            navigation.go_to_home()

        with self.step("Navigate to products screen"):
            navigation.go_to_products()

        with self.step("Navigate to profile screen"):
            navigation.go_to_profile()

        with self.step("Navigate back to products"):
            navigation.press_android_back()
            navigation.wait_for_products_screen()
