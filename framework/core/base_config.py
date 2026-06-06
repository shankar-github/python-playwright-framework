"""
Base configuration settings shared across all layers
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Base configuration shared across all layers"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    env: str = "dev"
    app_url: str = ""

    log_level: str = "INFO"
    log_file: str = "logs/automation.log"

    parallel_workers: str = "auto"
    retry_count: int = 2
    retry_delay: int = 1

    allure_results_dir: str = "reports/allure-results"
    allure_report_dir: str = "reports/allure-report"

    test_data_dir: str = "test_data"
