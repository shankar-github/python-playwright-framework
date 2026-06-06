"""
Standalone database tests
"""
import pytest
import allure
from framework.db.base_db_test import BaseDBTest
from framework.db.repositories import UsersRepository, ProductsRepository, CategoriesRepository
from framework.utils.test_data import test_data
from framework.utils.assertions import hard_assert


@allure.epic("Database Testing")
@allure.feature("Standalone Database Tests")
@pytest.mark.db
class TestDatabaseStandalone(BaseDBTest):
    """Standalone database tests"""

    @allure.story("Data Integrity")
    @allure.title("Test referential integrity constraints")
    def test_referential_integrity(self):
        categories = self.repository(CategoriesRepository)
        products = self.repository(ProductsRepository)

        self.set_test_title("Test Referential Integrity Constraints")

        with self.step("Create parent and child records") as step_ctx:
            category_data = {
                "name": test_data.generate_string(prefix="Category_"),
                "description": "Test category",
            }
            self.add_test_data("category_data", category_data)
            category_id = categories.create(category_data)

            product_data = {
                "name": test_data.generate_string(prefix="Product_"),
                "category_id": category_id,
                "price": 99.99,
            }
            self.add_test_data("product_data", product_data)
            product_id = products.create(product_data)
            step_ctx.set_result({"category_id": category_id, "product_id": product_id})

        with self.step("Verify referential integrity"):
            users = self.repository(UsersRepository)
            users.assert_referential_integrity()

        with self.step("Cleanup test data"):
            products.delete(product_id)
            categories.delete(category_id)

    @allure.story("Data Validation")
    @allure.title("Test data validation constraints")
    def test_data_validation_constraints(self):
        users = self.repository(UsersRepository)
        user_data = test_data.generate_user_data()

        self.set_test_title("Test Data Validation Constraints")

        with self.step("Test NOT NULL constraint violation") as step_ctx:
            users.assert_insert_fails_for_null_email()
            step_ctx.set_result("Constraint violation caught as expected")

        with self.step("Insert valid data") as step_ctx:
            user_id = users.create(user_data, with_timestamp=False)
            self.add_test_data("user_data", user_data)
            step_ctx.set_result({"user_id": user_id})

        with self.step("Verify record exists in database"):
            users.assert_exists(user_id)

        with self.step("Cleanup test data"):
            users.delete(user_id)

    @allure.story("Stored Procedures")
    @allure.title("Test stored procedure execution")
    def test_stored_procedure(self):
        users = self.repository(UsersRepository)

        self.set_test_title("Test Stored Procedure Execution")

        with self.step("Execute stored procedure") as step_ctx:
            result = users.run_stored_procedure(
                "calculate_total_sales",
                {"start_date": "2024-01-01", "end_date": "2024-12-31"},
            )
            self.add_test_data("stored_procedure_result", result)
            step_ctx.set_result({"result": result})

        with self.step("Validate stored procedure result"):
            hard_assert.assert_is_not_none(result, "Stored procedure should return result")
