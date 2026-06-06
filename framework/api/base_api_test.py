"""
Base test classes for API tests
"""
from typing import Type, TypeVar
from framework.core.base_test import BaseTest
from framework.core.config_manager import config
from framework.api.rest_client import RESTClient
from framework.api.graphql_client import GraphQLClient
from framework.api.services.base_service import BaseAPIService
from framework.db.db_client import DatabaseClient
from framework.db.db_validator import DatabaseValidator
from framework.db.repositories.base_repository import BaseRepository

TService = TypeVar("TService", bound=BaseAPIService)
TRepository = TypeVar("TRepository", bound=BaseRepository)


class BaseAPITest(BaseTest):
    """Base test class for API tests with lazy client initialization."""

    test_type_label = "API test"

    def _init_resources(self, request):
        self._api_client = None
        self._graphql_client = None

    def _cleanup_resources(self):
        if self._api_client:
            self._api_client.close()

    def api_service(self, service_cls: Type[TService]) -> TService:
        """Create an API service with REST/GraphQL clients."""
        return service_cls(
            api_client=self.api_client,
            graphql_client=self.graphql_client,
        )

    @property
    def api_client(self) -> RESTClient:
        """Lazy initialization of REST API client."""
        if self._api_client is None:
            self._api_client = RESTClient(
                base_url=config.api.api_base_url,
                timeout=config.api.api_timeout,
            )
        return self._api_client

    @property
    def graphql_client(self) -> GraphQLClient:
        """Lazy initialization of GraphQL client."""
        if self._graphql_client is None:
            self._graphql_client = GraphQLClient(endpoint=config.api.graphql_endpoint)
        return self._graphql_client

    @property
    def api_config(self):
        """Get API-specific configuration."""
        return config.api


class BaseAPITestWithDB(BaseAPITest):
    """API tests that also need database validation."""

    def _init_resources(self, request):
        super()._init_resources(request)
        self._db_client = None
        self._db_validator = None

    @property
    def db_client(self) -> DatabaseClient:
        if self._db_client is None:
            self._db_client = DatabaseClient()
        return self._db_client

    @property
    def db_validator(self) -> DatabaseValidator:
        if self._db_validator is None:
            self._db_validator = DatabaseValidator(self.db_client)
        return self._db_validator

    def _cleanup_resources(self):
        if self._db_client is not None:
            self._db_client.close()
            self._db_client = None
        super()._cleanup_resources()

    def api_service(self, service_cls: Type[TService]) -> TService:
        """Create an API service with REST/GraphQL clients and database access."""
        return service_cls(
            api_client=self.api_client,
            graphql_client=self.graphql_client,
            db_client=self.db_client,
            db_validator=self.db_validator,
        )

    def repository(self, repo_cls: Type[TRepository]) -> TRepository:
        """Create a database repository for test setup and verification."""
        return repo_cls(self.db_client, self.db_validator)
