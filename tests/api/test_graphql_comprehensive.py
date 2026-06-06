"""
Comprehensive GraphQL API test examples
"""
import pytest
import allure
from framework.api.base_api_test import BaseAPITest
from framework.api.services import ProductsGraphQL
from framework.utils.test_data import test_data
from framework.utils.assertions import hard_assert


@allure.epic("API Testing")
@allure.feature("GraphQL API - Comprehensive Examples")
@pytest.mark.api
@pytest.mark.graphql
@pytest.mark.regression
class TestGraphQLComprehensive(BaseAPITest):
    """Comprehensive GraphQL API test examples"""

    @allure.story("Product Management")
    @allure.title("Query product by ID")
    @pytest.mark.smoke
    def test_query_product_by_id(self):
        products = self.api_service(ProductsGraphQL)
        product_data = test_data.generate_product_data()

        self.set_test_title("Query Product by ID via GraphQL")

        with self.step("Create test product") as step_ctx:
            created = products.create(product_data)
            product_id = created["id"]
            self.add_test_data("product_id", product_id)
            step_ctx.set_result({"product_id": product_id})

        with self.step("Query and validate product") as step_ctx:
            product = products.get_and_validate(product_id, product_data)
            step_ctx.set_result(product)

        with self.step("Cleanup test data"):
            products.cleanup(product_id)

    @allure.story("Product Management")
    @allure.title("Query all products with filters")
    def test_query_all_products_with_filters(self):
        products = self.api_service(ProductsGraphQL)
        filter_data = {"category": "Electronics", "minPrice": 100, "maxPrice": 1000}

        self.set_test_title("Query All Products with Filters")
        self.add_test_data("filter_variables", {"filter": filter_data})

        with self.step("Query products with filters") as step_ctx:
            result = products.list_with_filter(filter_data)
            step_ctx.set_result({"product_count": len(result)})

        with self.step("Validate filtered results") as step_ctx:
            count = products.validate_product_list(result)
            step_ctx.set_result(f"Validated {count} products")

    @allure.story("Product Management")
    @allure.title("Update product via GraphQL mutation")
    def test_update_product_via_graphql(self):
        products = self.api_service(ProductsGraphQL)
        product_data = test_data.generate_product_data()
        update_data = {"name": "Updated Product Name", "price": 199.99, "stock": 50}

        self.set_test_title("Update Product via GraphQL Mutation")
        self.add_test_data("update_data", update_data)

        with self.step("Create test product") as step_ctx:
            product_id = products.create(product_data)["id"]
            step_ctx.set_result({"product_id": product_id})

        with self.step("Update product and validate in database") as step_ctx:
            updated = products.update_and_validate_in_db(product_id, update_data)
            step_ctx.set_result(updated)

        with self.step("Cleanup"):
            products.cleanup(product_id)

    @allure.story("Product Management")
    @allure.title("Delete product via GraphQL mutation")
    def test_delete_product_via_graphql(self):
        products = self.api_service(ProductsGraphQL)
        product_data = test_data.generate_product_data()

        self.set_test_title("Delete Product via GraphQL Mutation")

        with self.step("Create test product") as step_ctx:
            product_id = products.create(product_data)["id"]
            step_ctx.set_result({"product_id": product_id})

        with self.step("Delete product and validate in database"):
            products.delete_and_validate_in_db(product_id)

    @allure.story("Error Handling")
    @allure.title("Handle GraphQL errors")
    def test_handle_graphql_errors(self):
        products = self.api_service(ProductsGraphQL)
        self.set_test_title("Handle GraphQL Errors")

        with self.step("Execute invalid GraphQL query") as step_ctx:
            try:
                result = products.execute_invalid_field_query()
                step_ctx.set_result(result)
            except Exception as error:
                self.add_test_data("graphql_error", str(error))
                step_ctx.set_result(str(error))

        with self.step("Validate error handling") as step_ctx:
            hard_assert.assert_in(
                "graphql_error",
                self.test_result.test_data,
                "GraphQL error should be recorded in test data",
            )
            step_ctx.set_result(self.test_result.test_data["graphql_error"])
