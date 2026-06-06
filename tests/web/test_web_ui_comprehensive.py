"""
Comprehensive Web UI test examples
"""
import tempfile
import pytest
import allure
from framework.web.base_web_test import BaseWebTest
from framework.web.pages import (
    RegistrationPage,
    ProductsPage,
    ContactPage,
    HomePage,
    UploadPage,
)
from framework.utils.assertions import hard_assert
from framework.utils.test_data import test_data


@allure.epic("Web UI Testing")
@allure.feature("Playwright Web Tests - Comprehensive Examples")
@pytest.mark.web
@pytest.mark.regression
class TestWebUIComprehensive(BaseWebTest):
    """Comprehensive Web UI test examples using the Page Object Model"""

    @allure.story("User Registration")
    @allure.title("Complete user registration flow")
    @pytest.mark.smoke
    def test_user_registration_flow(self):
        """Test complete user registration flow"""
        registration_page = self.page_object(RegistrationPage)
        user_data = test_data.generate_user_data()
        password = "SecurePassword123!"

        self.set_test_title("Complete User Registration Flow")
        self.add_test_data("user_data", user_data)

        with self.step("Open registration page"):
            registration_page.open()

        with self.step("Register a new user"):
            registration_page.register(user_data, password)

        with self.step("Verify registration success") as step_ctx:
            success_message = registration_page.wait_for_success()
            hard_assert.assert_string_contains(
                success_message, "Welcome", "Registration should be successful"
            )
            step_ctx.set_result(success_message)

        registration_page.screenshot("registration_success")

    @allure.story("Product Management")
    @allure.title("Add product to cart")
    def test_add_product_to_cart(self):
        """Test adding a product to cart"""
        products_page = self.page_object(ProductsPage)

        self.set_test_title("Add Product to Cart")

        with self.step("Open products page"):
            products_page.open()

        with self.step("Select first product") as step_ctx:
            product_name = products_page.select_first_product()
            self.add_test_data("product_name", product_name)
            step_ctx.set_result(product_name)

        with self.step("Add product to cart"):
            products_page.add_to_cart()

        with self.step("Verify cart updated") as step_ctx:
            cart_count = products_page.get_cart_count()
            hard_assert.assert_equal(cart_count, "1", "Cart should show 1 item")
            step_ctx.set_result(cart_count)

        products_page.screenshot("product_added_to_cart")

    @allure.story("Form Validation")
    @allure.title("Test form validation errors")
    def test_form_validation_errors(self):
        """Test form validation error handling"""
        contact_page = self.page_object(ContactPage)

        self.set_test_title("Test Form Validation Errors")

        with self.step("Open contact form"):
            contact_page.open()

        with self.step("Submit empty form"):
            contact_page.submit_empty_form()

        with self.step("Verify validation errors") as step_ctx:
            error_texts = contact_page.get_validation_errors()
            self.add_test_data("validation_errors", error_texts)
            hard_assert.assert_greater_than(
                len(error_texts), 0, "Validation errors should be displayed"
            )
            step_ctx.set_result(f"Found {len(error_texts)} validation errors")

        contact_page.screenshot("validation_errors")

    @allure.story("Navigation")
    @allure.title("Test multi-page navigation")
    def test_multi_page_navigation(self):
        """Test navigation across multiple pages"""
        home_page = self.page_object(HomePage)

        self.set_test_title("Multi-Page Navigation Test")

        with self.step("Open home page") as step_ctx:
            home_page.open()
            step_ctx.set_result(home_page.get_url())

        with self.step("Navigate to products") as step_ctx:
            home_page.go_to_products()
            step_ctx.set_result(home_page.get_url())

        with self.step("Navigate to about") as step_ctx:
            home_page.go_to_about()
            step_ctx.set_result(home_page.get_url())

        with self.step("Navigate back to products") as step_ctx:
            home_page.go_back()
            home_page.wait_for_url(HomePage.PRODUCTS_URL_PATTERN)
            step_ctx.set_result("Navigated back to products")

        with self.step("Navigate forward to about") as step_ctx:
            home_page.go_forward()
            home_page.wait_for_url(HomePage.ABOUT_URL_PATTERN)
            step_ctx.set_result("Navigated forward to about")

    @allure.story("Dynamic Content")
    @allure.title("Test dynamic content loading")
    def test_dynamic_content_loading(self):
        """Test dynamic content loading"""
        products_page = self.page_object(ProductsPage)

        self.set_test_title("Test Dynamic Content Loading")

        with self.step("Open products page"):
            products_page.open()

        with self.step("Wait for dynamic content to load"):
            products_page.wait_for_products()

        with self.step("Verify products are displayed") as step_ctx:
            product_count = products_page.get_product_count()
            hard_assert.assert_greater_than(product_count, 0, "Products should be displayed")
            step_ctx.set_result(f"Found {product_count} products")

        products_page.screenshot("dynamic_content_loaded")

    @allure.story("File Upload")
    @allure.title("Test file upload functionality")
    def test_file_upload(self):
        """Test file upload functionality"""
        upload_page = self.page_object(UploadPage)

        self.set_test_title("Test File Upload Functionality")

        with self.step("Open upload page"):
            upload_page.open()

        with self.step("Select and upload a file") as step_ctx:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as temp_file:
                temp_file.write("Test file content")
                test_file_path = temp_file.name

            upload_page.select_file(test_file_path)
            self.add_test_data("uploaded_file", test_file_path)
            step_ctx.set_result(test_file_path)

        with self.step("Submit upload"):
            upload_page.submit()

        with self.step("Verify upload success") as step_ctx:
            success_message = upload_page.get_success_message()
            hard_assert.assert_string_contains(
                success_message.lower(), "success", "Upload should be successful"
            )
            step_ctx.set_result(success_message)
