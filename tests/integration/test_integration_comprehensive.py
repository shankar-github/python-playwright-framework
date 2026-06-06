"""
Comprehensive Integration/E2E test examples
"""
import pytest
import allure
from framework.integration.base_integration_test import BaseIntegrationTest
from framework.api.services import UsersAPI
from framework.web.pages import LoginPage, ProductsPage
from framework.utils.test_data import test_data
from framework.utils.assertions import hard_assert


@allure.epic("Integration Testing")
@allure.feature("E2E Tests - Comprehensive Examples")
@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.regression
class TestIntegrationComprehensive(BaseIntegrationTest):
    """Comprehensive Integration/E2E test examples"""

    @allure.story("Complete User Journey")
    @allure.title("Complete user journey: Register -> Login -> Purchase")
    @pytest.mark.smoke_e2e
    def test_complete_user_journey(self):
        users = self.api_service(UsersAPI)
        login_page = self.page_object(LoginPage)
        products_page = self.page_object(ProductsPage)
        user_data = test_data.generate_user_data()

        self.set_test_title("Complete User Journey: Register -> Login -> Purchase")
        self.add_test_data("user_email", user_data["email"])

        with self.step("Register user via API") as step_ctx:
            created = users.create(user_data)
            user_id = created["id"]
            step_ctx.set_result({"user_id": user_id})

        with self.step("Verify user in database"):
            users.validate_user_exists_in_db(user_id)

        with self.step("Login via Web UI"):
            login_page.open()
            login_page.login(user_data["email"], user_data["password"])
            login_page.wait_for_dashboard()

        with self.step("Browse products via Web UI") as step_ctx:
            products_page.open()
            product_count = products_page.get_product_count()
            hard_assert.assert_greater_than(product_count, 0, "Products should be displayed")
            step_ctx.set_result(f"Found {product_count} products")

        with self.step("Cleanup test data"):
            users.delete(user_id)
