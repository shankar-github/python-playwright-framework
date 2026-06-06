"""Repository for categories table operations."""
from typing import Any, Dict
from framework.db.repositories.base_repository import BaseRepository


class CategoriesRepository(BaseRepository):
    TABLE = "categories"

    INSERT_QUERY = """
        INSERT INTO categories (name, description)
        VALUES (:name, :description)
        RETURNING id
    """

    DELETE_QUERY = "DELETE FROM categories WHERE id = :id"

    def create(self, category_data: Dict[str, Any]) -> Any:
        return self.db.execute_scalar(query=self.INSERT_QUERY, params=category_data)

    def delete(self, category_id: Any):
        self.db.execute_update(query=self.DELETE_QUERY, params={"id": category_id})

    def assert_not_exists(self, category_id: Any):
        self.validator.assert_record_not_exists(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": category_id},
        )
