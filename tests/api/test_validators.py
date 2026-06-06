"""
Tests for API validators
"""
import pytest
from unittest.mock import Mock
from framework.api.validators import APIResponseValidator
from framework.utils.assertions import AssertionError


class TestAPIResponseValidator:
    """Tests for APIResponseValidator"""
    
    def test_initialization(self):
        """Test validator initialization"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.text = '{"data": "test"}'
        
        validator = APIResponseValidator(mock_response)
        
        assert validator.status_code == 200, "Should set status code"
        assert validator.json_data is not None, "Should parse JSON"
    
    def test_assert_status_code(self):
        """Test assert_status_code"""
        mock_response = Mock()
        mock_response.status_code = 200
        
        validator = APIResponseValidator(mock_response)
        validator.assert_status_code(200, "Should pass")
        
        with pytest.raises(AssertionError):
            validator.assert_status_code(404, "Should fail")
    
    def test_assert_status_code_in(self):
        """Test assert_status_code_in"""
        mock_response = Mock()
        mock_response.status_code = 200
        
        validator = APIResponseValidator(mock_response)
        validator.assert_status_code_in([200, 201], "Should pass")
        
        with pytest.raises(AssertionError):
            validator.assert_status_code_in([404, 500], "Should fail")
    
    def test_assert_contains_key(self):
        """Test assert_contains_key"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "test"}
        
        validator = APIResponseValidator(mock_response)
        validator.assert_contains_key("id", "Should pass")
        validator.assert_contains_key("name", "Should pass")
        
        with pytest.raises(AssertionError):
            validator.assert_contains_key("missing", "Should fail")
    
    def test_assert_key_value(self):
        """Test assert_key_value"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "test"}
        
        validator = APIResponseValidator(mock_response)
        validator.assert_key_value("id", 1, "Should pass")
        validator.assert_key_value("name", "test", "Should pass")
        
        with pytest.raises(AssertionError):
            validator.assert_key_value("id", 2, "Should fail")
    
    def test_assert_response_time(self):
        """Test assert_response_time"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.5  # 500ms
        
        validator = APIResponseValidator(mock_response)
        validator.assert_response_time(1000, "Should pass")  # 1000ms limit
        
        with pytest.raises(AssertionError):
            validator.assert_response_time(100, "Should fail")  # 100ms limit
    
    def test_assert_header(self):
        """Test assert_header"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        
        validator = APIResponseValidator(mock_response)
        validator.assert_header("Content-Type")
        validator.assert_header("Content-Type", "application/json", "Should pass")
        
        with pytest.raises(AssertionError):
            validator.assert_header("Missing-Header", "Should fail")
    
    def test_get_value(self):
        """Test get_value with dot notation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user": {
                "name": "Test",
                "email": "test@example.com"
            }
        }
        
        validator = APIResponseValidator(mock_response)
        
        name = validator.get_value("user.name")
        email = validator.get_value("user.email")
        missing = validator.get_value("user.missing", "default")
        
        assert name == "Test", "Should get nested value"
        assert email == "test@example.com", "Should get nested value"
        assert missing == "default", "Should return default for missing key"
    
    def test_non_json_response(self):
        """Test validator with non-JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_response.text = "Plain text response"
        
        validator = APIResponseValidator(mock_response)
        
        assert validator.json_data is None, "Should handle non-JSON response"
        assert validator.text == "Plain text response", "Should have text"
        
        with pytest.raises(AssertionError):
            validator.assert_contains_key("key", "Should fail for non-JSON")
