"""Repository for orders table operations."""
from typing import Any, Dict, List
from framework.db.repositories.base_repository import BaseRepository
from framework.utils.assertions import hard_assert


class OrdersRepository(BaseRepository):
    TABLE = "orders"

    INSERT_QUERY = """
        INSERT INTO orders (order_number, total_amount, status)
        VALUES (:order_number, :total_amount, :status)
        RETURNING id
    """

    DELETE_QUERY = "DELETE FROM orders WHERE order_number = :order_number"

    AGGREGATION_QUERY = """
        SELECT
            COUNT(*) as total_orders,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as average_order_value,
            MAX(total_amount) as max_order,
            MIN(total_amount) as min_order
        FROM orders
        WHERE status = 'completed'
    """

    def create(self, order_data: Dict[str, Any]) -> Any:
        return self.db.execute_scalar(query=self.INSERT_QUERY, params=order_data)

    def delete_by_order_number(self, order_number: str):
        self.db.execute_update(query=self.DELETE_QUERY, params={"order_number": order_number})

    def get_aggregation_stats(self) -> Dict[str, Any]:
        result = self.db.execute_query(self.AGGREGATION_QUERY)
        return result[0]

    def validate_aggregation(self, stats: Dict[str, Any]):
        hard_assert.assert_greater_than(stats["total_orders"], 0, "Should have orders")
        hard_assert.assert_greater_than(stats["total_revenue"], 0, "Should have revenue")
        assert "average_order_value" in stats, "Should have average"
