"""
Tests for REST API client
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from framework.api.rest_client import RESTClient


class TestRESTClient:
    """Tests for RESTClient"""
    
    def test_initialization(self):
        """Test RESTClient initialization"""
        client = RESTClient()
        
        assert client.base_url is not None, "Should have base_url"
        assert client.timeout is not None, "Should have timeout"
        assert client.session is not None, "Should have session"
    
    def test_custom_base_url(self):
        """Test RESTClient with custom base URL"""
        client = RESTClient(base_url="https://custom-api.com")
        
        assert client.base_url == "https://custom-api.com", "Should use custom base URL"
    
    def test_custom_timeout(self):
        """Test RESTClient with custom timeout"""
        client = RESTClient(timeout=60)
        
        assert client.timeout == 60, "Should use custom timeout"
    
    def test_set_header(self):
        """Test setting header"""
        client = RESTClient()
        client.set_header("Authorization", "Bearer token123")
        
        assert client.session.headers["Authorization"] == "Bearer token123", "Should set header"
    
    def test_set_headers(self):
        """Test setting multiple headers"""
        client = RESTClient()
        client.set_headers({
            "Authorization": "Bearer token123",
            "X-Custom": "value"
        })
        
        assert client.session.headers["Authorization"] == "Bearer token123", "Should set first header"
        assert client.session.headers["X-Custom"] == "value", "Should set second header"
    
    def test_set_auth_bearer(self):
        """Test setting Bearer authentication"""
        client = RESTClient()
        client.set_auth("bearer", "token123")
        
        assert client.session.headers["Authorization"] == "Bearer token123", "Should set Bearer token"
    
    def test_set_auth_basic(self):
        """Test setting Basic authentication"""
        client = RESTClient()
        client.set_auth("basic", ("user", "pass"))
        
        assert client.session.auth == ("user", "pass"), "Should set Basic auth"
    
    @patch('framework.api.rest_client.requests.Session.get')
    def test_get_request(self, mock_get):
        """Test GET request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.text = '{"data": "test"}'
        mock_response.reason = "OK"
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_get.return_value = mock_response
        
        client = RESTClient(base_url="https://api.example.com")
        response = client.get("/endpoint")
        
        assert response.status_code == 200, "Should return response"
        mock_get.assert_called_once()
    
    @patch('framework.api.rest_client.requests.Session.post')
    def test_post_request(self, mock_post):
        """Test POST request"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1}
        mock_response.text = '{"id": 1}'
        mock_response.reason = "Created"
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_post.return_value = mock_response
        
        client = RESTClient(base_url="https://api.example.com")
        response = client.post("/endpoint", json={"data": "test"})
        
        assert response.status_code == 201, "Should return response"
        mock_post.assert_called_once()
    
    @patch('framework.api.rest_client.requests.Session.put')
    def test_put_request(self, mock_put):
        """Test PUT request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"updated": True}
        mock_response.text = '{"updated": true}'
        mock_response.reason = "OK"
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_put.return_value = mock_response
        
        client = RESTClient(base_url="https://api.example.com")
        response = client.put("/endpoint", json={"data": "test"})
        
        assert response.status_code == 200, "Should return response"
        mock_put.assert_called_once()
    
    @patch('framework.api.rest_client.requests.Session.delete')
    def test_delete_request(self, mock_delete):
        """Test DELETE request"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_response.reason = "No Content"
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_delete.return_value = mock_response
        
        client = RESTClient(base_url="https://api.example.com")
        response = client.delete("/endpoint")
        
        assert response.status_code == 204, "Should return response"
        mock_delete.assert_called_once()
    
    def test_build_url(self):
        """Test URL building"""
        client = RESTClient(base_url="https://api.example.com")
        
        url = client._build_url("/endpoint")
        assert url == "https://api.example.com/endpoint", "Should build correct URL"
        
        url = client._build_url("https://full-url.com/path")
        assert url == "https://full-url.com/path", "Should use full URL as-is"
    
    def test_close(self):
        """Test closing session"""
        client = RESTClient()
        client.close()
        
        # Should not raise exception
        assert True, "Should close without error"
