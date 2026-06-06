"""
Tests for configuration manager
"""
import pytest
import os
import tempfile
from pathlib import Path
from framework.core.config_manager import ConfigManager
from framework.core.base_config import BaseConfig
from framework.api.config import APISettings
from framework.db.config import DBSettings


class TestConfigManager:
    """Tests for ConfigManager"""
    
    def test_singleton_pattern(self):
        """Test that ConfigManager is a singleton"""
        config1 = ConfigManager()
        config2 = ConfigManager()
        
        assert config1 is config2, "ConfigManager should be a singleton"
        assert config1.base is config2.base, "Base settings should be shared"
    
    def test_settings_access(self):
        """Test accessing settings"""
        config = ConfigManager()
        base_settings = config.base
        api_settings = config.api
        
        assert base_settings is not None, "Base settings should be accessible"
        assert isinstance(base_settings, BaseConfig), "Base settings should be BaseConfig instance"
        assert api_settings is not None, "API settings should be accessible"
        assert isinstance(api_settings, APISettings), "API settings should be APISettings instance"
    
    def test_get_method(self):
        """Test get method for configuration values"""
        config = ConfigManager()
        
        # Test getting existing value from base config
        env = config.base.env
        assert env is not None, "Should return environment value"
        
        # Test getting value from API config
        api_url = config.api.api_base_url
        assert api_url is not None, "Should return API URL"
    
    def test_get_with_default(self):
        """Test get method with default value"""
        config = ConfigManager()
        
        # Test getting non-existent value with default
        value = config.get("non_existent_key", "default_value")
        assert value == "default_value", "Should return default value"
    
    def test_environment_variable_override(self):
        """Test that environment variables override defaults on fresh settings."""
        original_env = os.environ.get("ENV")

        try:
            os.environ["ENV"] = "test_override"
            settings = BaseConfig()
            assert settings.env == "test_override", "Environment variable should override default"
        finally:
            if original_env:
                os.environ["ENV"] = original_env
            elif "ENV" in os.environ:
                del os.environ["ENV"]


class TestLayerSpecificSettings:
    """Tests for layer-specific settings"""
    
    def test_api_settings_defaults(self, monkeypatch):
        """Test that API settings have default values"""
        monkeypatch.setenv("ENV", "dev")
        settings = APISettings()

        assert settings.api_timeout == 30, "Default API timeout should be 30"
        assert settings.env == "dev", "Should inherit from base"

    def test_web_settings_defaults(self, monkeypatch):
        """Test that Web settings have default values"""
        from framework.web.config import WebSettings

        monkeypatch.setenv("ENV", "dev")
        settings = WebSettings()

        assert settings.browser == "chromium", "Default browser should be 'chromium'"
        assert settings.headless is True, "Default headless should be True"
        assert settings.env == "dev", "Should inherit from base"

    def test_db_settings_defaults(self, monkeypatch):
        """Test that DB settings have default values"""
        from framework.db.config import DBSettings

        monkeypatch.setenv("ENV", "dev")
        settings = DBSettings()

        assert settings.db_type == "postgresql", "Default DB type should be postgresql"
        assert settings.db_port == 5432, "Default DB port should be 5432"
        assert settings.env == "dev", "Should inherit from base"
    
    def test_config_manager_properties(self):
        """Test accessing configs via ConfigManager properties"""
        config = ConfigManager()
        
        assert config.base is not None, "Base config should be accessible"
        assert config.api is not None, "API config should be accessible"
        assert config.web is not None, "Web config should be accessible"
        assert config.mobile is not None, "Mobile config should be accessible"
        assert config.db is not None, "DB config should be accessible"
    
    def test_environment_variable_loading(self):
        """Test loading from environment variables"""
        original_api_url = os.environ.get("API_BASE_URL")
        
        try:
            # Set environment variable
            os.environ["API_BASE_URL"] = "https://test-api.example.com"
            
            # Create new settings instance
            settings = APISettings()
            
            assert settings.api_base_url == "https://test-api.example.com", "Should load from environment"
        finally:
            # Restore original value
            if original_api_url:
                os.environ["API_BASE_URL"] = original_api_url
            elif "API_BASE_URL" in os.environ:
                del os.environ["API_BASE_URL"]
    
    def test_type_validation(self):
        """Test that Settings validate types"""
        api_settings = APISettings()
        db_settings = DBSettings()
        
        # Test integer type
        assert isinstance(api_settings.api_timeout, int), "API timeout should be integer"
        assert isinstance(db_settings.db_port, int), "DB port should be integer"
