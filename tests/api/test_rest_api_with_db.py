"""
REST API tests with database validation
"""
import pytest
import allure
from framework.api.base_api_test import BaseAPITestWithDB
from framework.api.services import UsersAPI
from framework.db.repositories import UsersRepository
from framework.utils.test_data import test_data
from framework.utils.test_data_cleanup import cleanup_registry


@allure.epic("API Testing")
@allure.feature("REST API")
@pytest.mark.api
@pytest.mark.rest
class TestRESTAPIWithDB(BaseAPITestWithDB):
    """REST API tests with database validation"""

    @allure.story("User Management")
    @allure.title("Create user via API and validate in database")
    @pytest.mark.smoke_db
    def test_create_user_and_validate_in_db(self):
        users = self.api_service(UsersAPI)
        user_data = test_data.generate_user_data()

        self.set_test_title("Create User via API and Validate in Database")
        self.add_test_data("user_data", user_data)

        with self.step("Create user and validate in database") as step_ctx:
            response_data = users.create_and_validate_in_db(user_data)
            user_id = response_data["id"]
            step_ctx.set_result(response_data)

        self.attach_to_allure("API Response", response_data, "json")
        self.add_test_data("api_response", response_data)

        with self.step("Register cleanup task"):
            cleanup_registry.register_cleanup(
                self.db_client.execute_update,
                "DELETE FROM users WHERE id = :id",
                {"id": user_id},
                description=f"Delete user {user_id}",
            )
            users.delete(user_id)

        self.logger.info(f"Test completed successfully. User ID: {user_id}")

    @allure.story("User Management")
    @allure.title("Update user via API and validate database changes")
    def test_update_user_and_validate_db(self):
        users = self.api_service(UsersAPI)
        users_repo = self.repository(UsersRepository)
        user_data = test_data.generate_user_data()
        updated_data = {"first_name": "UpdatedFirstName", "last_name": "UpdatedLastName"}

        with self.step("Create user in database") as step_ctx:
            user_id = users_repo.create(user_data)
            step_ctx.set_result({"user_id": user_id})

        with self.step("Update user via API and validate database"):
            users.update_and_validate_in_db(user_id, updated_data)

        with self.step("Cleanup"):
            users_repo.delete(user_id)

    @allure.story("User Management")
    @allure.title("Delete user via API and validate database deletion")
    def test_delete_user_and_validate_db(self):
        users = self.api_service(UsersAPI)
        users_repo = self.repository(UsersRepository)
        user_data = test_data.generate_user_data()

        with self.step("Create user in database") as step_ctx:
            user_id = users_repo.create(user_data)
            step_ctx.set_result({"user_id": user_id})

        with self.step("Delete user via API and validate database"):
            users.delete_and_validate_in_db(user_id)
