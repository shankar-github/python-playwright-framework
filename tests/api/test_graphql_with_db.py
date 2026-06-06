"""
GraphQL API tests with database validation
"""
import pytest
import allure
from framework.api.base_api_test import BaseAPITestWithDB
from framework.api.services import ProductsGraphQL
from framework.db.repositories import ProductsRepository
from framework.utils.test_data import test_data


@allure.epic("API Testing")
@allure.feature("GraphQL API")
@pytest.mark.api
@pytest.mark.graphql
class TestGraphQLWithDB(BaseAPITestWithDB):
    """GraphQL API tests with database validation"""

    @allure.story("Product Management")
    @allure.title("Create product via GraphQL mutation and validate in database")
    @pytest.mark.smoke_db
    def test_create_product_via_graphql_and_validate_db(self):
        products = self.api_service(ProductsGraphQL)
        product_data = test_data.generate_product_data()

        with self.step("Create product and validate in database") as step_ctx:
            product = products.create_and_validate_in_db(product_data)
            product_id = product["id"]
            step_ctx.set_result(product)

        self.attach_to_allure("GraphQL Response", product, "json")
        products.cleanup(product_id)

    @allure.story("Product Management")
    @allure.title("Query product via GraphQL and validate with database")
    def test_query_product_via_graphql_and_validate_db(self):
        products = self.api_service(ProductsGraphQL)
        products_repo = self.repository(ProductsRepository)
        product_data = test_data.generate_product_data()

        with self.step("Create product in database") as step_ctx:
            product_id = products_repo.create_full(product_data)
            step_ctx.set_result({"product_id": product_id})

        with self.step("Query product via GraphQL and validate against database") as step_ctx:
            db_record = products_repo.get_record(product_id)
            product = products.query_and_validate_against_db(product_id, db_record)
            step_ctx.set_result(product)

        with self.step("Cleanup"):
            products_repo.delete(product_id)
