"""Shared dependencies for database repository classes."""
from framework.db.db_client import DatabaseClient
from framework.db.db_validator import DatabaseValidator


class BaseRepository:
    def __init__(self, db_client: DatabaseClient, db_validator: DatabaseValidator):
        self.db = db_client
        self.validator = db_validator
