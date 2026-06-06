"""
Comprehensive REST API test examples
"""
import pytest
import allure
from framework.api.base_api_test import BaseAPITest
from framework.api.services import UsersAPI
from framework.utils.test_data import test_data


@allure.epic("API Testing")
@allure.feature("REST API - Comprehensive Examples")
@pytest.mark.api
@pytest.mark.rest
@pytest.mark.regression
class TestRESTAPIComprehensive(BaseAPITest):
    """Comprehensive REST API test examples"""

    @allure.story("User Management")
    @allure.title("GET user by ID")
    @pytest.mark.smoke
    def test_get_user_by_id(self):
        users = self.api_service(UsersAPI)
        user_data = test_data.generate_user_data()

        self.set_test_title("GET User by ID")

        with self.step("Create test user") as step_ctx:
            created = users.create(user_data)
            user_id = created["id"]
            self.add_test_data("user_id", user_id)
            step_ctx.set_result({"user_id": user_id})

        with self.step("GET user by ID") as step_ctx:
            response_data = users.get_and_validate(user_id, user_data)
            step_ctx.set_result(response_data)

        with self.step("Cleanup test data"):
            users.delete(user_id)

    @allure.story("User Management")
    @allure.title("GET all users with pagination")
    def test_get_all_users_with_pagination(self):
        users = self.api_service(UsersAPI)
        self.set_test_title("GET All Users with Pagination")

        with self.step("GET users with pagination") as step_ctx:
            response_data = users.list_users(page=1, limit=10)
            step_ctx.set_result(response_data)

        with self.step("Validate users data structure") as step_ctx:
            count = users.validate_user_list_structure(response_data)
            step_ctx.set_result(f"Found {count} users")

    @allure.story("User Management")
    @allure.title("UPDATE user via PUT")
    def test_update_user_via_put(self):
        users = self.api_service(UsersAPI)
        user_data = test_data.generate_user_data()
        updated_data = {
            "first_name": "UpdatedFirstName",
            "last_name": "UpdatedLastName",
            "email": user_data["email"],
        }

        self.set_test_title("UPDATE User via PUT")

        with self.step("Create test user") as step_ctx:
            user_id = users.create(user_data)["id"]
            self.add_test_data("original_user_data", user_data)
            step_ctx.set_result({"user_id": user_id})

        with self.step("Update user via PUT") as step_ctx:
            response_data = users.update(user_id, updated_data)
            step_ctx.set_result(response_data)

        with self.step("Validate user update in database"):
            users.validate_field_in_db(user_id, "first_name", updated_data["first_name"])

        with self.step("Cleanup"):
            users.delete(user_id)

    @allure.story("User Management")
    @allure.title("PARTIAL UPDATE user via PATCH")
    def test_partial_update_user_via_patch(self):
        users = self.api_service(UsersAPI)
        user_data = test_data.generate_user_data()
        patch_data = {"first_name": "PatchedName"}

        self.set_test_title("PARTIAL UPDATE User via PATCH")

        with self.step("Create test user") as step_ctx:
            user_id = users.create(user_data)["id"]
            step_ctx.set_result({"user_id": user_id})

        with self.step("Partial update via PATCH") as step_ctx:
            response_data = users.partial_update(user_id, patch_data)
            step_ctx.set_result(response_data)

        with self.step("Validate unchanged fields"):
            users.get_and_validate(user_id, {"email": user_data["email"]})

        with self.step("Cleanup"):
            users.delete(user_id)

    @allure.story("User Management")
    @allure.title("DELETE user and verify deletion")
    def test_delete_user_and_verify(self):
        users = self.api_service(UsersAPI)
        user_data = test_data.generate_user_data()

        self.set_test_title("DELETE User and Verify Deletion")

        with self.step("Create test user") as step_ctx:
            user_id = users.create(user_data)["id"]
            step_ctx.set_result({"user_id": user_id})

        with self.step("Verify user exists in database"):
            users.validate_user_exists_in_db(user_id)

        with self.step("Delete user via API"):
            users.delete(user_id)

        with self.step("Verify user deleted from database"):
            users.validate_user_deleted_from_db(user_id)

    @allure.story("Error Handling")
    @allure.title("Handle 404 Not Found error")
    def test_handle_404_error(self):
        users = self.api_service(UsersAPI)
        self.set_test_title("Handle 404 Not Found Error")

        with self.step("GET non-existent user"):
            users.expect_not_found(99999)

    @allure.story("Error Handling")
    @allure.title("Handle 400 Bad Request error")
    def test_handle_400_error(self):
        users = self.api_service(UsersAPI)
        invalid_data = {"email": "invalid-email"}

        self.set_test_title("Handle 400 Bad Request Error")
        self.add_test_data("invalid_data", invalid_data)

        with self.step("Create user with invalid data") as step_ctx:
            error_data = users.create_expect_validation_error(invalid_data)
            self.add_test_data("error_response", error_data)
            step_ctx.set_result(error_data)
