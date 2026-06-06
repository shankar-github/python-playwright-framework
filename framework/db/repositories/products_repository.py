"""Repository for products table operations."""
from typing import Any, Dict, List, Optional
from framework.db.repositories.base_repository import BaseRepository


class ProductsRepository(BaseRepository):
    TABLE = "products"

    INSERT_FULL_QUERY = """
        INSERT INTO products (name, description, price, sku, category, stock, created_at)
        VALUES (:name, :description, :price, :sku, :category, :stock, NOW())
        RETURNING id
    """

    INSERT_QUERY = """
        INSERT INTO products (name, category_id, price)
        VALUES (:name, :category_id, :price)
        RETURNING id
    """

    def create_full(self, product_data: Dict[str, Any]) -> Any:
        return self.db.execute_scalar(query=self.INSERT_FULL_QUERY, params=product_data)

    def get_record(self, product_id: Any) -> Optional[Dict[str, Any]]:
        return self.validator.get_record(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": product_id},
        )

    DELETE_QUERY = "DELETE FROM products WHERE id = :id"

    JOIN_QUERY = """
        SELECT p.id, p.name, p.price, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.id = :product_id
    """

    def create(self, product_data: Dict[str, Any]) -> Any:
        return self.db.execute_scalar(query=self.INSERT_QUERY, params=product_data)

    def delete(self, product_id: Any):
        self.db.execute_update(query=self.DELETE_QUERY, params={"id": product_id})

    def get_with_category(self, product_id: Any) -> List[Dict[str, Any]]:
        return self.db.execute_query(self.JOIN_QUERY, {"product_id": product_id})

    def assert_exists(self, product_id: Any):
        self.validator.assert_record_exists(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": product_id},
        )

    def assert_not_exists(self, product_id: Any):
        self.validator.assert_record_not_exists(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": product_id},
        )

    def validate_join_result(self, result: List[Dict[str, Any]], product_id: Any):
        assert len(result) > 0, "Query should return result"
        assert result[0]["id"] == product_id, "Product ID should match"
        assert "category_name" in result[0], "Should have category name from join"
