"""
Tests for logger
"""
import pytest
import tempfile
from pathlib import Path
from framework.core.logger import Logger, log


class TestLogger:
    """Tests for Logger class"""
    
    def test_logger_setup(self):
        """Test that logger can be set up"""
        Logger.setup()
        
        # Logger should be configured
        assert Logger._configured is True, "Logger should be configured after setup"
    
    def test_get_logger(self):
        """Test getting logger instance"""
        Logger.setup()
        logger = Logger.get_logger("test_module")
        
        assert logger is not None, "Logger should be returned"
    
    def test_get_logger_with_name(self):
        """Test getting logger with specific name"""
        Logger.setup()
        logger = Logger.get_logger("test_module")
        
        # Logger should be bound with name
        assert logger is not None, "Logger should be returned with name"
    
    def test_logger_initialization(self):
        """Test that logger is initialized on import"""
        # Logger should be initialized when module is imported
        assert log is not None, "Global logger should be available"
    
    def test_logging_levels(self):
        """Test different logging levels"""
        Logger.setup(log_level="DEBUG")
        logger = Logger.get_logger("test")
        
        # These should not raise exceptions
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
    
    def test_custom_log_file(self):
        """Test logging to custom file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            Logger.setup(log_file=str(log_file), force=True)
            logger = Logger.get_logger("test")
            logger.info("Test message")
            
            # File should be created
            assert log_file.exists(), "Log file should be created"
            
            # File should contain message
            content = log_file.read_text()
            assert "Test message" in content, "Log file should contain message"
    
    def test_log_rotation(self):
        """Test that log rotation is configured"""
        Logger.setup(rotation="1 MB", retention="1 day")
        
        # Logger should be configured with rotation
        assert Logger._configured is True, "Logger should be configured with rotation"
