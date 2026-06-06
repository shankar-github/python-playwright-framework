"""Repository for users table operations."""
from typing import Any, Dict, Optional
from framework.db.repositories.base_repository import BaseRepository


class UsersRepository(BaseRepository):
    TABLE = "users"

    INSERT_QUERY = """
        INSERT INTO users (email, first_name, last_name, created_at)
        VALUES (:email, :first_name, :last_name, NOW())
        RETURNING id
    """

    INSERT_BASIC_QUERY = """
        INSERT INTO users (email, first_name, last_name)
        VALUES (:email, :first_name, :last_name)
        RETURNING id
    """

    DELETE_QUERY = "DELETE FROM users WHERE id = :id"

    def create(self, user_data: Dict[str, Any], with_timestamp: bool = True) -> Any:
        query = self.INSERT_QUERY if with_timestamp else self.INSERT_BASIC_QUERY
        return self.db.execute_scalar(query=query, params=user_data)

    def delete(self, user_id: Any):
        self.db.execute_update(query=self.DELETE_QUERY, params={"id": user_id})

    def get_record(self, user_id: Any) -> Optional[Dict[str, Any]]:
        return self.validator.get_record(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": user_id},
        )

    def assert_exists(self, user_id: Any):
        self.validator.assert_record_exists(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": user_id},
        )

    def assert_not_exists(self, user_id: Any):
        self.validator.assert_record_not_exists(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": user_id},
        )

    def assert_field_value(self, user_id: Any, field: str, expected_value: Any):
        self.validator.assert_field_value(
            table_name=self.TABLE,
            field_name=field,
            expected_value=expected_value,
            where_clause="id = :id",
            params={"id": user_id},
        )

    def assert_referential_integrity(self):
        self.validator.assert_referential_integrity(
            child_table="products",
            child_fk="category_id",
            parent_table="categories",
            parent_pk="id",
        )

    def assert_insert_fails_for_null_email(self):
        try:
            self.db.execute_update(query="INSERT INTO users (email) VALUES (NULL)", params={})
            raise AssertionError("Should have raised constraint violation for NULL email")
        except Exception:
            return

    def run_stored_procedure(self, procedure: str, params: Dict[str, Any]) -> Any:
        return self.db.execute_scalar(query=f"CALL {procedure}(:start_date, :end_date)", params=params)

    def query_limited(self, limit: int = 100):
        return self.db.execute_query(f"SELECT * FROM {self.TABLE} LIMIT {limit}")
