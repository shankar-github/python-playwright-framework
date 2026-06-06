"""
Comprehensive Database test examples
"""
import time
import pytest
import allure
from framework.db.base_db_test import BaseDBTest
from framework.db.repositories import (
    UsersRepository,
    ProductsRepository,
    CategoriesRepository,
    OrdersRepository,
)
from framework.utils.test_data import test_data
from framework.utils.assertions import hard_assert


@allure.epic("Database Testing")
@allure.feature("Database Tests - Comprehensive Examples")
@pytest.mark.db
@pytest.mark.regression
class TestDatabaseComprehensive(BaseDBTest):
    """Comprehensive Database test examples"""

    @allure.story("Complex Queries")
    @allure.title("Test complex SQL query with joins")
    @pytest.mark.smoke_db
    def test_complex_query_with_joins(self):
        categories = self.repository(CategoriesRepository)
        products = self.repository(ProductsRepository)

        self.set_test_title("Complex SQL Query with Joins")

        with self.step("Setup test data") as step_ctx:
            category_id = categories.create(
                {"name": test_data.generate_string(prefix="Cat_"), "description": "Test"}
            )
            product_id = products.create(
                {
                    "name": test_data.generate_string(prefix="Prod_"),
                    "category_id": category_id,
                    "price": 99.99,
                }
            )
            self.add_test_data("category_id", category_id)
            self.add_test_data("product_id", product_id)
            step_ctx.set_result({"category_id": category_id, "product_id": product_id})

        with self.step("Execute complex query with joins") as step_ctx:
            result = products.get_with_category(product_id)
            step_ctx.set_result(result)

        with self.step("Validate query result"):
            products.validate_join_result(result, product_id)

        with self.step("Cleanup"):
            products.delete(product_id)
            categories.delete(category_id)

    @allure.story("Transactions")
    @allure.title("Test database transaction rollback")
    def test_transaction_rollback(self):
        users = self.repository(UsersRepository)
        user_data = test_data.generate_user_data()

        self.set_test_title("Test Database Transaction Rollback")

        with self.step("Insert test data") as step_ctx:
            user_id = users.create(user_data, with_timestamp=False)
            self.add_test_data("user_id", user_id)
            step_ctx.set_result({"user_id": user_id})

        with self.step("Verify data exists"):
            users.assert_exists(user_id)

        with self.step("Rollback transaction (cleanup)"):
            users.delete(user_id)

        with self.step("Verify rollback"):
            users.assert_not_exists(user_id)

    @allure.story("Data Aggregation")
    @allure.title("Test data aggregation queries")
    def test_data_aggregation(self):
        orders = self.repository(OrdersRepository)
        order_data = []

        self.set_test_title("Test Data Aggregation Queries")

        with self.step("Setup test data for aggregation") as step_ctx:
            for _ in range(3):
                order = {
                    "order_number": test_data.generate_string(prefix="ORD_"),
                    "total_amount": test_data.generate_number(10, 100),
                    "status": "completed",
                }
                orders.create(order)
                order_data.append(order)
            self.add_test_data("orders", order_data)
            step_ctx.set_result(f"Created {len(order_data)} orders")

        with self.step("Execute aggregation query") as step_ctx:
            stats = orders.get_aggregation_stats()
            step_ctx.set_result(stats)

        with self.step("Validate aggregation results"):
            orders.validate_aggregation(stats)

        with self.step("Cleanup"):
            for order in order_data:
                orders.delete_by_order_number(order["order_number"])

    @allure.story("Data Integrity")
    @allure.title("Test cascade delete")
    def test_cascade_delete(self):
        categories = self.repository(CategoriesRepository)
        products = self.repository(ProductsRepository)

        self.set_test_title("Test Cascade Delete")

        with self.step("Create parent and child records") as step_ctx:
            category_id = categories.create(
                {"name": test_data.generate_string(prefix="Cat_"), "description": "Test"}
            )
            product_id = products.create(
                {
                    "name": test_data.generate_string(prefix="Prod_"),
                    "category_id": category_id,
                    "price": 99.99,
                }
            )
            step_ctx.set_result({"category_id": category_id, "product_id": product_id})

        with self.step("Delete parent record"):
            categories.delete(category_id)

        with self.step("Verify cascade delete"):
            categories.assert_not_exists(category_id)

    @allure.story("Performance")
    @allure.title("Test query performance")
    def test_query_performance(self):
        users = self.repository(UsersRepository)

        self.set_test_title("Test Query Performance")

        with self.step("Execute query and measure performance") as step_ctx:
            start_time = time.time()
            result = users.query_limited(limit=100)
            execution_time = time.time() - start_time
            self.add_test_data("execution_time_seconds", execution_time)
            self.add_test_data("rows_returned", len(result))
            step_ctx.set_result(
                {"execution_time": f"{execution_time:.3f}s", "rows_returned": len(result)}
            )

        with self.step("Validate query performance"):
            hard_assert.assert_less_than(execution_time, 1.0, "Query should complete within 1 second")
