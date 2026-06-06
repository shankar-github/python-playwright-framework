"""Database layer specific configuration"""
from framework.core.base_config import BaseConfig


class DBSettings(BaseConfig):
    """Database-specific configuration settings"""

    db_type: str = "postgresql"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "test_db"
    db_user: str = "test_user"
    db_password: str = ""

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_db: str = "test_db"
    mysql_user: str = "test_user"
    mysql_password: str = ""

    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_db: str = "test_db"
    mongo_user: str = ""
    mongo_password: str = ""
