"""
Example: REST API test with transaction management
"""
import pytest
import allure
from framework.api.base_api_test import BaseAPITestWithDB
from framework.api.services import UsersAPI
from framework.utils.test_data import test_data
from framework.db.transaction_manager import TransactionManager


@allure.epic("API Testing")
@allure.feature("REST API with Transaction Management")
@pytest.mark.api
@pytest.mark.rest
class TestRESTAPIWithTransaction(BaseAPITestWithDB):
    """REST API tests with transaction management for guaranteed rollback"""

    @allure.story("User Management")
    @allure.title("Create user with transaction rollback")
    def test_create_user_with_transaction(self):
        users = self.api_service(UsersAPI)
        transaction_manager = TransactionManager(self.db_client)

        self.set_test_title("Create User with Transaction Management")

        with self.step("Generate test user data") as step_ctx:
            user_data = test_data.generate_user_data()
            self.add_test_data("user_data", user_data)
            step_ctx.set_result(f"Generated user: {user_data['email']}")

        with transaction_manager.transaction(rollback_on_error=True):
            with self.step("Create user and validate in database") as step_ctx:
                response_data = users.create_and_validate_in_db(user_data)
                step_ctx.set_result(response_data)
