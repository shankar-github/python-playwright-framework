"""
Base test class for Database tests
"""
from typing import Type, TypeVar
from framework.core.base_test import BaseTest
from framework.core.config_manager import config
from framework.db.db_client import DatabaseClient, MongoDBClient
from framework.db.db_validator import DatabaseValidator, MongoDBValidator
from framework.db.repositories.base_repository import BaseRepository

TRepository = TypeVar("TRepository", bound=BaseRepository)


class BaseDBTest(BaseTest):
    """Base test class for Database tests."""

    test_type_label = "Database test"

    def _init_resources(self, request):
        self.db_client = DatabaseClient(
            db_type=config.db.db_type,
            host=config.db.db_host,
            port=config.db.db_port,
            database=config.db.db_name,
            username=config.db.db_user,
            password=config.db.db_password,
        )
        self.db_validator = DatabaseValidator(self.db_client)

        self.mongo_client = None
        self.mongo_validator = None
        if self._needs_mongodb():
            self.mongo_client = MongoDBClient(
                host=config.db.mongo_host,
                port=config.db.mongo_port,
                database=config.db.mongo_db,
                username=config.db.mongo_user,
                password=config.db.mongo_password,
            )
            self.mongo_validator = MongoDBValidator(self.mongo_client)

    def _cleanup_resources(self):
        self.db_client.close()
        if self.mongo_client:
            self.mongo_client.close()

    def repository(self, repo_cls: Type[TRepository]) -> TRepository:
        """Create a database repository for table-specific operations."""
        return repo_cls(self.db_client, self.db_validator)

    def _needs_mongodb(self) -> bool:
        """Override in subclasses if MongoDB is needed."""
        return False

    @property
    def db_config(self):
        """Get Database-specific configuration."""
        return config.db
