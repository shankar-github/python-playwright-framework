"""
End-to-end integration tests
"""
import pytest
import allure
from framework.integration.base_integration_test import BaseIntegrationTest
from framework.api.services import UsersAPI
from framework.web.pages import LoginPage
from framework.utils.test_data import test_data
from framework.utils.assertions import hard_assert


@allure.epic("Integration Testing")
@allure.feature("End-to-End Tests")
@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.regression
class TestE2EFlow(BaseIntegrationTest):
    """End-to-end integration tests"""

    @allure.story("User Registration Flow")
    @allure.title("Complete user registration flow: API -> DB -> UI")
    @pytest.mark.smoke_e2e
    def test_user_registration_e2e(self):
        users = self.api_service(UsersAPI)
        login_page = self.page_object(LoginPage)
        user_data = test_data.generate_user_data()

        self.set_test_title("Complete User Registration Flow: API -> DB -> UI")
        self.add_test_data("user_email", user_data["email"])

        with self.step("Create user via API") as step_ctx:
            created = users.create(user_data)
            user_id = created["id"]
            step_ctx.set_result({"user_id": user_id})

        with self.step("Validate user in database"):
            users.validate_user_exists_in_db(user_id)

        with self.step("Login via UI with created credentials"):
            login_page.open()
            login_page.login(user_data["email"], user_data["password"], user_data["first_name"])

        with self.step("Verify dashboard access") as step_ctx:
            login_page.wait_for_dashboard()
            welcome_text = login_page.get_welcome_message()
            hard_assert.assert_string_contains(
                welcome_text, user_data["first_name"], "Welcome message should contain user name"
            )
            step_ctx.set_result(welcome_text)

        with self.step("Cleanup test data"):
            users.delete(user_id)
