"""
Unified configuration manager that loads layer-specific configs
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from dotenv import load_dotenv
import yaml

from framework.core.base_config import BaseConfig
from framework.api.config import APISettings
from framework.web.config import WebSettings
from framework.mobile.config import MobileSettings
from framework.db.config import DBSettings


class ConfigManager:
    """Manages configuration from environment variables and YAML files"""

    _instance: Optional["ConfigManager"] = None
    _base_settings: Optional[BaseConfig] = None
    _api_settings: Optional[APISettings] = None
    _web_settings: Optional[WebSettings] = None
    _mobile_settings: Optional[MobileSettings] = None
    _db_settings: Optional[DBSettings] = None
    _yaml_config: Dict[str, Any] = {}

    YAML_ENV_MAPPINGS: List[Tuple[Tuple[str, ...], str]] = [
        (("api", "base_url"), "API_BASE_URL"),
        (("api", "graphql_endpoint"), "GRAPHQL_ENDPOINT"),
        (("api", "timeout"), "API_TIMEOUT"),
        (("api", "graphql_fetch_schema"), "GRAPHQL_FETCH_SCHEMA"),
        (("web", "base_url"), "WEB_URL"),
        (("web", "browser"), "BROWSER"),
        (("web", "headless"), "HEADLESS"),
        (("web", "record_trace"), "RECORD_TRACE"),
        (("web", "record_video"), "RECORD_VIDEO"),
        (("database", "type"), "DB_TYPE"),
        (("database", "host"), "DB_HOST"),
        (("database", "port"), "DB_PORT"),
        (("database", "name"), "DB_NAME"),
        (("database", "user"), "DB_USER"),
        (("database", "password"), "DB_PASSWORD"),
        (("mobile", "appium_server_url"), "APPIUM_SERVER_URL"),
        (("logging", "level"), "LOG_LEVEL"),
        (("logging", "file"), "LOG_FILE"),
        (("execution", "retry_count"), "RETRY_COUNT"),
        (("execution", "retry_delay"), "RETRY_DELAY"),
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._base_settings is None:
            env_file = Path(".env")
            if env_file.exists():
                load_dotenv(env_file)

            self._load_yaml_config()
            self._apply_yaml_to_environment()

            self._base_settings = BaseConfig()
            self._api_settings = APISettings()
            self._web_settings = WebSettings()
            self._mobile_settings = MobileSettings()
            self._db_settings = DBSettings()

    def _load_yaml_config(self):
        env = os.getenv("ENV", "dev")
        config_file = Path("config") / f"config_{env}.yaml"
        if config_file.exists():
            with open(config_file, "r") as file_handle:
                self._yaml_config = yaml.safe_load(file_handle) or {}

    def _get_nested_value(self, path: Tuple[str, ...]) -> Any:
        value: Any = self._yaml_config
        for key in path:
            if not isinstance(value, dict):
                return None
            value = value.get(key)
        return value

    def _apply_yaml_to_environment(self):
        for path, env_key in self.YAML_ENV_MAPPINGS:
            if env_key in os.environ:
                continue
            value = self._get_nested_value(path)
            if value is not None:
                os.environ[env_key] = str(value)

    @property
    def base(self) -> BaseConfig:
        return self._base_settings

    @property
    def api(self) -> APISettings:
        return self._api_settings

    @property
    def web(self) -> WebSettings:
        return self._web_settings

    @property
    def mobile(self) -> MobileSettings:
        return self._mobile_settings

    @property
    def db(self) -> DBSettings:
        return self._db_settings

    def get(self, key: str, default: Any = None) -> Any:
        value = os.getenv(key.upper(), None)
        if value is not None:
            return value

        keys = key.split(".")
        config_value: Any = self._yaml_config
        for part in keys:
            if isinstance(config_value, dict):
                config_value = config_value.get(part)
            else:
                return default

        if config_value is not None:
            return config_value

        for settings in (
            self._base_settings,
            self._api_settings,
            self._web_settings,
            self._mobile_settings,
            self._db_settings,
        ):
            value = getattr(settings, key.lower(), None)
            if value is not None:
                return value

        return default


config = ConfigManager()
