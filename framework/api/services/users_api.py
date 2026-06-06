"""REST API service for user resources."""
from typing import Any, Dict, List, Optional
from framework.api.services.base_service import BaseAPIService
from framework.api.validators import APIResponseValidator
from framework.utils.assertions import hard_assert


class UsersAPI(BaseAPIService):
    PATH = "/users"
    TABLE = "users"

    def create(self, user_data: Dict[str, Any], expected_status: int = 201) -> Dict[str, Any]:
        response = self._require_api_client().post(self.PATH, json=user_data)
        validator = APIResponseValidator(response)
        validator.assert_status_code(expected_status)
        validator.assert_contains_key("id")
        return response.json()

    def get(self, user_id: Any, expected_status: int = 200) -> Dict[str, Any]:
        response = self._require_api_client().get(f"{self.PATH}/{user_id}")
        APIResponseValidator(response).assert_status_code(expected_status)
        return response.json()

    def get_and_validate(self, user_id: Any, expected: Dict[str, Any]) -> Dict[str, Any]:
        response = self._require_api_client().get(f"{self.PATH}/{user_id}")
        validator = APIResponseValidator(response)
        validator.assert_status_code(200)
        validator.assert_key_value("id", user_id)
        if "email" in expected:
            validator.assert_key_value("email", expected["email"])
        return response.json()

    def list_users(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        response = self._require_api_client().get(self.PATH, params={"page": page, "limit": limit})
        validator = APIResponseValidator(response)
        validator.assert_status_code(200)
        for key in ("data", "total", "page", "limit"):
            validator.assert_contains_key(key)
        return response.json()

    def validate_user_list_structure(self, response_data: Dict[str, Any]) -> int:
        users = response_data.get("data", [])
        if users:
            hard_assert.assert_dict_has_key(users[0], "id", "User should have ID")
            hard_assert.assert_dict_has_key(users[0], "email", "User should have email")
        return len(users)

    def update(self, user_id: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        response = self._require_api_client().put(f"{self.PATH}/{user_id}", json=data)
        validator = APIResponseValidator(response)
        validator.assert_status_code(200)
        for key, value in data.items():
            validator.assert_key_value(key, value)
        return response.json()

    def partial_update(self, user_id: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        response = self._require_api_client().patch(f"{self.PATH}/{user_id}", json=data)
        validator = APIResponseValidator(response)
        validator.assert_status_code(200)
        for key, value in data.items():
            validator.assert_key_value(key, value)
        return response.json()

    def delete(self, user_id: Any, expected_status: int = 204):
        response = self._require_api_client().delete(f"{self.PATH}/{user_id}")
        APIResponseValidator(response).assert_status_code(expected_status)

    def expect_not_found(self, user_id: Any):
        response = self._require_api_client().get(f"{self.PATH}/{user_id}")
        APIResponseValidator(response).assert_status_code(404)

    def create_expect_validation_error(self, invalid_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self._require_api_client().post(self.PATH, json=invalid_data)
        APIResponseValidator(response).assert_status_code_in([400, 422])
        return response.json() if response.text else {}

    def create_and_validate_in_db(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        _, db_validator = self._require_db()
        db_validator.assert_record_not_exists(
            table_name=self.TABLE,
            where_clause="email = :email",
            params={"email": user_data["email"]},
        )
        response_data = self.create(user_data)
        user_id = response_data["id"]
        db_validator.assert_record_exists(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": user_id},
        )
        db_validator.compare_api_response_with_db(
            api_data=response_data,
            table_name=self.TABLE,
            where_clause="id = :id",
            field_mapping={"email": "email", "first_name": "first_name", "last_name": "last_name"},
            params={"id": user_id},
        )
        return response_data

    def update_and_validate_in_db(self, user_id: Any, updated_data: Dict[str, Any]) -> Dict[str, Any]:
        _, db_validator = self._require_db()
        response_data = self.update(user_id, updated_data)
        for field, value in updated_data.items():
            db_validator.assert_field_value(
                table_name=self.TABLE,
                field_name=field,
                expected_value=value,
                where_clause="id = :id",
                params={"id": user_id},
            )
        return response_data

    def delete_and_validate_in_db(self, user_id: Any):
        _, db_validator = self._require_db()
        db_validator.assert_record_exists(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": user_id},
        )
        self.delete(user_id)
        db_validator.assert_record_not_exists(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": user_id},
        )

    def validate_user_exists_in_db(self, user_id: Any):
        _, db_validator = self._require_db()
        db_validator.assert_record_exists(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": user_id},
        )

    def validate_user_deleted_from_db(self, user_id: Any):
        _, db_validator = self._require_db()
        db_validator.assert_record_not_exists(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": user_id},
        )

    def validate_field_in_db(self, user_id: Any, field: str, expected_value: Any):
        _, db_validator = self._require_db()
        db_validator.assert_field_value(
            table_name=self.TABLE,
            field_name=field,
            expected_value=expected_value,
            where_clause="id = :id",
            params={"id": user_id},
        )
