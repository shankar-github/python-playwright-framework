"""API layer specific configuration"""
from framework.core.base_config import BaseConfig


class APISettings(BaseConfig):
    """API-specific configuration settings"""

    api_base_url: str = ""
    graphql_endpoint: str = ""
    api_timeout: int = 30
    graphql_fetch_schema: bool = False
