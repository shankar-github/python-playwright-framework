"""
Base test class for integration and end-to-end tests
"""
from typing import Type, TypeVar, Optional
from framework.core.base_test import BaseTest
from framework.core.config_manager import config
from framework.api.rest_client import RESTClient
from framework.api.graphql_client import GraphQLClient
from framework.api.services.base_service import BaseAPIService
from framework.web.browser_manager import BrowserManager
from framework.web.base_page import BasePage
from framework.db.db_client import DatabaseClient
from framework.db.db_validator import DatabaseValidator
from framework.db.repositories.base_repository import BaseRepository

TService = TypeVar("TService", bound=BaseAPIService)
TRepository = TypeVar("TRepository", bound=BaseRepository)
TPage = TypeVar("TPage", bound=BasePage)

_SHARED_BROWSER_MARKERS = ("smoke", "smoke_e2e", "regression")


class BaseIntegrationTest(BaseTest):
    """Base test class for integration tests combining API, Web, and DB."""

    test_type_label = "Integration test"
    requires_browser: bool = True
    requires_db: bool = True
    requires_graphql: bool = False

    def _uses_shared_browser(self, request) -> bool:
        return any(request.node.get_closest_marker(marker) for marker in _SHARED_BROWSER_MARKERS)

    def _init_resources(self, request):
        self.api_client = RESTClient(
            base_url=config.api.api_base_url,
            timeout=config.api.api_timeout,
        )

        if self.requires_graphql:
            self.graphql_client = GraphQLClient(endpoint=config.api.graphql_endpoint)
        else:
            self.graphql_client = None

        if self.requires_db:
            self.db_client = DatabaseClient(
                db_type=config.db.db_type,
                host=config.db.db_host,
                port=config.db.db_port,
                database=config.db.db_name,
                username=config.db.db_user,
                password=config.db.db_password,
            )
            self.db_validator = DatabaseValidator(self.db_client)
        else:
            self.db_client = None
            self.db_validator = None

        if self.requires_browser:
            if self._uses_shared_browser(request):
                self.browser_manager = request.getfixturevalue("session_browser_manager")
                self.browser_manager.create_context()
                self._owns_browser = False
            else:
                self.browser_manager = BrowserManager()
                self.browser_manager.start_browser(
                    browser_type=config.web.browser,
                    headless=config.web.headless,
                )
                self._owns_browser = True
            self.page = BasePage(self.browser_manager.get_page())
        else:
            self.browser_manager = None
            self.page = None

    def _cleanup_resources(self):
        self.api_client.close()
        if self.db_client:
            self.db_client.close()
        if self.browser_manager:
            if getattr(self, "_owns_browser", True):
                self.browser_manager.close_browser()
            else:
                self.browser_manager.close_context()

    def _capture_failure_artifacts(self):
        if self.browser_manager:
            self.browser_manager.capture_failure_artifacts(self.test_id)

    def api_service(self, service_cls: Type[TService]) -> TService:
        return service_cls(
            api_client=self.api_client,
            graphql_client=self.graphql_client,
            db_client=self.db_client,
            db_validator=self.db_validator,
        )

    def repository(self, repo_cls: Type[TRepository]) -> TRepository:
        if not self.db_client or not self.db_validator:
            raise RuntimeError("Database resources are not initialized for this test class")
        return repo_cls(self.db_client, self.db_validator)

    def page_object(self, page_cls: Type[TPage]) -> TPage:
        if not self.page:
            raise RuntimeError("Browser page is not initialized for this test class")
        return page_cls(self.page.page)
