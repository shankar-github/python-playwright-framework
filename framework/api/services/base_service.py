"""Shared dependencies for API service classes."""
from typing import Optional
from framework.api.rest_client import RESTClient
from framework.api.graphql_client import GraphQLClient
from framework.db.db_client import DatabaseClient
from framework.db.db_validator import DatabaseValidator


class BaseAPIService:
    """Base class for API services with optional database support."""

    def __init__(
        self,
        api_client: Optional[RESTClient] = None,
        graphql_client: Optional[GraphQLClient] = None,
        db_client: Optional[DatabaseClient] = None,
        db_validator: Optional[DatabaseValidator] = None,
    ):
        self.api_client = api_client
        self.graphql_client = graphql_client
        self.db_client = db_client
        self.db_validator = db_validator

    def _require_api_client(self) -> RESTClient:
        if self.api_client is None:
            raise RuntimeError(f"{self.__class__.__name__} requires an API client")
        return self.api_client

    def _require_graphql_client(self) -> GraphQLClient:
        if self.graphql_client is None:
            raise RuntimeError(f"{self.__class__.__name__} requires a GraphQL client")
        return self.graphql_client

    def _require_db(self):
        if self.db_client is None or self.db_validator is None:
            raise RuntimeError(f"{self.__class__.__name__} requires database access")
        return self.db_client, self.db_validator
