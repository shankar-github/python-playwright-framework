"""GraphQL API service for product resources."""
from typing import Any, Dict, List, Optional
from framework.api.services.base_service import BaseAPIService
from framework.utils.assertions import hard_assert


class ProductsGraphQL(BaseAPIService):
    TABLE = "products"

    CREATE_MUTATION = """
        mutation CreateProduct($input: ProductInput!) {
            createProduct(input: $input) {
                id
                name
                price
            }
        }
    """

    GET_QUERY = """
        query GetProduct($id: ID!) {
            product(id: $id) {
                id
                name
                description
                price
                sku
                category
                stock
            }
        }
    """

    LIST_QUERY = """
        query GetProducts($filter: ProductFilter) {
            products(filter: $filter) {
                id
                name
                price
                category
                stock
            }
        }
    """

    UPDATE_MUTATION = """
        mutation UpdateProduct($id: ID!, $input: ProductUpdateInput!) {
            updateProduct(id: $id, input: $input) {
                id
                name
                price
                stock
            }
        }
    """

    DELETE_MUTATION = """
        mutation DeleteProduct($id: ID!) {
            deleteProduct(id: $id) {
                success
                message
            }
        }
    """

    CREATE_FULL_MUTATION = """
        mutation CreateProduct($input: ProductInput!) {
            createProduct(input: $input) {
                id
                name
                description
                price
                sku
                category
                stock
                createdAt
            }
        }
    """

    def create(self, product_data: Dict[str, Any], full: bool = False) -> Dict[str, Any]:
        client = self._require_graphql_client()
        mutation = self.CREATE_FULL_MUTATION if full else self.CREATE_MUTATION
        result = client.execute_mutation(mutation, {"input": product_data}, "CreateProduct")
        return result["createProduct"]

    def get(self, product_id: Any) -> Optional[Dict[str, Any]]:
        client = self._require_graphql_client()
        result = client.execute_query(self.GET_QUERY, {"id": product_id}, "GetProduct")
        return result.get("product")

    def get_and_validate(self, product_id: Any, expected: Dict[str, Any]) -> Dict[str, Any]:
        product = self.get(product_id)
        hard_assert.assert_is_not_none(product, "Product should be returned")
        hard_assert.assert_equal(product["id"], product_id, "Product ID should match")
        hard_assert.assert_equal(product["name"], expected["name"], "Product name should match")
        return product

    def list_with_filter(self, filter_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        client = self._require_graphql_client()
        result = client.execute_query(self.LIST_QUERY, {"filter": filter_data}, "GetProducts")
        return result.get("products", [])

    def validate_product_list(self, products: List[Dict[str, Any]]) -> int:
        for product in products:
            hard_assert.assert_dict_has_key(product, "id", "Product should have ID")
            hard_assert.assert_dict_has_key(product, "name", "Product should have name")
            hard_assert.assert_dict_has_key(product, "price", "Product should have price")
        return len(products)

    def update(self, product_id: Any, update_data: Dict[str, Any]) -> Dict[str, Any]:
        client = self._require_graphql_client()
        result = client.execute_mutation(
            self.UPDATE_MUTATION,
            {"id": product_id, "input": update_data},
            "UpdateProduct",
        )
        updated = result["updateProduct"]
        hard_assert.assert_equal(updated["name"], update_data["name"], "Name should be updated")
        hard_assert.assert_equal(float(updated["price"]), update_data["price"], "Price should be updated")
        return updated

    def delete(self, product_id: Any) -> Dict[str, Any]:
        client = self._require_graphql_client()
        return client.execute_mutation(
            self.DELETE_MUTATION,
            {"id": product_id},
            "DeleteProduct",
        )

    def cleanup(self, product_id: Any):
        """Remove test data via GraphQL delete (no DB required)."""
        self.delete(product_id)

    def assert_not_exists_by_sku(self, sku: str):
        _, db_validator = self._require_db()
        db_validator.assert_record_not_exists(
            table_name=self.TABLE,
            where_clause="sku = :sku",
            params={"sku": sku},
        )

    def assert_exists(self, product_id: Any):
        _, db_validator = self._require_db()
        db_validator.assert_record_exists(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": int(product_id)},
        )

    def assert_not_exists(self, product_id: Any):
        _, db_validator = self._require_db()
        db_validator.assert_record_not_exists(
            table_name=self.TABLE,
            where_clause="id = :id",
            params={"id": product_id},
        )

    def assert_field_in_db(self, product_id: Any, field: str, expected_value: Any):
        _, db_validator = self._require_db()
        db_validator.assert_field_value(
            table_name=self.TABLE,
            field_name=field,
            expected_value=expected_value,
            where_clause="id = :id",
            params={"id": product_id},
        )

    def compare_with_db(self, product: Dict[str, Any], product_id: Any):
        _, db_validator = self._require_db()
        db_validator.compare_api_response_with_db(
            api_data=product,
            table_name=self.TABLE,
            where_clause="id = :id",
            field_mapping={
                "name": "name",
                "description": "description",
                "price": "price",
                "sku": "sku",
            },
            params={"id": product_id},
        )

    def create_and_validate_in_db(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        if "sku" in product_data:
            self.assert_not_exists_by_sku(product_data["sku"])
        product = self.create(product_data, full=True)
        hard_assert.assert_is_not_none(product, "Product should be created")
        hard_assert.assert_dict_has_key(product, "id", "Product should have ID")
        self.assert_exists(product["id"])
        self.compare_with_db(product, product["id"])
        return product

    def update_and_validate_in_db(self, product_id: Any, update_data: Dict[str, Any]) -> Dict[str, Any]:
        updated = self.update(product_id, update_data)
        self.assert_field_in_db(product_id, "name", update_data["name"])
        return updated

    def delete_and_validate_in_db(self, product_id: Any):
        self.assert_exists(product_id)
        self.delete(product_id)
        self.assert_not_exists(product_id)

    def execute_invalid_field_query(self, product_id: str = "123"):
        """Execute a query with an invalid field to test error handling."""
        invalid_query = """
            query GetProduct($id: ID!) {
                product(id: $id) {
                    nonExistentField
                }
            }
        """
        client = self._require_graphql_client()
        return client.execute_query(invalid_query, {"id": product_id}, "GetProduct")

    def query_and_validate_against_db(self, product_id: Any, db_record: Dict[str, Any]) -> Dict[str, Any]:
        product = self.get(product_id)
        hard_assert.assert_is_not_none(product, "Product should be returned")
        hard_assert.assert_equal(product["id"], str(product_id), "Product ID should match")
        hard_assert.assert_equal(product["name"], db_record["name"], "Product name should match")
        hard_assert.assert_equal(float(product["price"]), float(db_record["price"]), "Product price should match")
        return product
