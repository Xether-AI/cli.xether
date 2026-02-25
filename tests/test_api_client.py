import pytest
import httpx
from unittest.mock import Mock, patch, MagicMock
from xether_cli.api.client import (
    XetherAPIClient, XetherAPIError, XetherNetworkError, 
    XetherHTTPError, XetherAuthError, get_client
)

class TestXetherAPIClient:
    """Test Xether API client"""
    
    @patch('xether_cli.api.client.load_config')
    def test_client_initialization(self, mock_load_config):
        """Test client initialization"""
        mock_config = Mock()
        mock_config.backend_url = "https://test.xether.ai"
        mock_config.access_token = "test-token"
        mock_config.request_timeout = 30.0
        mock_config.max_retries = 3
        mock_load_config.return_value = mock_config
        
        client = XetherAPIClient()
        
        assert client.base_url == "https://test.xether.ai"
        assert str(client.client.timeout) == "Timeout(timeout=30.0)"
        assert "Authorization" in client.client.headers
        assert client.client.headers["Authorization"] == "Bearer test-token"
    
    @patch('xether_cli.api.client.load_config')
    def test_client_no_auth_header(self, mock_load_config):
        """Test client initialization without access token"""
        mock_config = Mock()
        mock_config.backend_url = "https://test.xether.ai"
        mock_config.access_token = None
        mock_config.request_timeout = 30.0
        mock_config.max_retries = 3
        mock_load_config.return_value = mock_config
        
        client = XetherAPIClient()
        
        assert "Authorization" not in client.client.headers
    
    @patch('xether_cli.api.client.load_config')
    def test_successful_request(self, mock_load_config):
        """Test successful API request"""
        mock_config = Mock()
        mock_config.backend_url = "https://test.xether.ai"
        mock_config.access_token = None
        mock_config.request_timeout = 30.0
        mock_config.max_retries = 3
        mock_load_config.return_value = mock_config
        
        client = XetherAPIClient()
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        client.client.get = Mock(return_value=mock_response)
        
        response = client.get("/test")
        
        assert response.status_code == 200
        client.client.get.assert_called_once_with("/test")
    
    @patch('xether_cli.api.client.load_config')
    def test_auth_error_handling(self, mock_load_config):
        """Test authentication error handling"""
        mock_config = Mock()
        mock_config.backend_url = "https://test.xether.ai"
        mock_config.access_token = None
        mock_config.request_timeout = 30.0
        mock_config.max_retries = 3
        mock_load_config.return_value = mock_config
        
        client = XetherAPIClient()
        
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        client.client.get = Mock(return_value=mock_response)
        
        with pytest.raises(XetherAuthError, match="Authentication failed"):
            client.get("/test")
    
    @patch('xether_cli.api.client.load_config')
    def test_http_error_handling(self, mock_load_config):
        """Test HTTP error handling"""
        mock_config = Mock()
        mock_config.backend_url = "https://test.xether.ai"
        mock_config.access_token = None
        mock_config.request_timeout = 30.0
        mock_config.max_retries = 3
        mock_load_config.return_value = mock_config
        
        client = XetherAPIClient()
        
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        client.client.get = Mock(return_value=mock_response)
        
        with pytest.raises(XetherHTTPError) as exc_info:
            client.get("/test")
        
        assert exc_info.value.status_code == 404
        assert "Not found" in str(exc_info.value)
    
    @patch('xether_cli.api.client.load_config')
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_retry_logic_network_error(self, mock_sleep, mock_load_config):
        """Test retry logic for network errors"""
        mock_config = Mock()
        mock_config.backend_url = "https://test.xether.ai"
        mock_config.access_token = None
        mock_config.request_timeout = 30.0
        mock_config.max_retries = 2
        mock_load_config.return_value = mock_config
        
        client = XetherAPIClient()
        
        # Mock network error that fails twice then succeeds
        client.client.get = Mock(side_effect=[
            httpx.RequestError("Connection failed"),
            httpx.RequestError("Connection failed"),
            Mock(status_code=200, json=lambda: {"data": "success"})
        ])
        
        response = client.get("/test")
        
        assert response.status_code == 200
        assert client.client.get.call_count == 3
        assert mock_sleep.call_count == 2  # Should sleep twice for retries
    
    @patch('xether_cli.api.client.load_config')
    def test_retry_logic_exhausted(self, mock_load_config):
        """Test retry logic when all retries are exhausted"""
        mock_config = Mock()
        mock_config.backend_url = "https://test.xether.ai"
        mock_config.access_token = None
        mock_config.request_timeout = 30.0
        mock_config.max_retries = 1
        mock_load_config.return_value = mock_config
        
        client = XetherAPIClient()
        
        # Mock persistent network error
        client.client.get = Mock(side_effect=httpx.RequestError("Connection failed"))
        
        with pytest.raises(XetherNetworkError, match="Network error"):
            client.get("/test")
        
        assert client.client.get.call_count == 2  # Initial attempt + 1 retry
    
    @patch('xether_cli.api.client.load_config')
    def test_post_request(self, mock_load_config):
        """Test POST request"""
        mock_config = Mock()
        mock_config.backend_url = "https://test.xether.ai"
        mock_config.access_token = None
        mock_config.request_timeout = 30.0
        mock_config.max_retries = 3
        mock_load_config.return_value = mock_config
        
        client = XetherAPIClient()
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "123"}
        client.client.post = Mock(return_value=mock_response)
        
        response = client.post("/test", json={"name": "test"})
        
        assert response.status_code == 201
        client.client.post.assert_called_once_with("/test", data=None, json={"name": "test"})
    
    @patch('xether_cli.api.client.load_config')
    def test_delete_request(self, mock_load_config):
        """Test DELETE request"""
        mock_config = Mock()
        mock_config.backend_url = "https://test.xether.ai"
        mock_config.access_token = None
        mock_config.request_timeout = 30.0
        mock_config.max_retries = 3
        mock_load_config.return_value = mock_config
        
        client = XetherAPIClient()
        
        mock_response = Mock()
        mock_response.status_code = 204
        client.client.delete = Mock(return_value=mock_response)
        
        response = client.delete("/test/123")
        
        assert response.status_code == 204
        client.client.delete.assert_called_once_with("/test/123")

class TestGetClient:
    """Test get_client factory function"""
    
    @patch('xether_cli.api.client.XetherAPIClient')
    def test_get_client(self, mock_client_class):
        """Test get_client returns XetherAPIClient instance"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        result = get_client()
        
        mock_client_class.assert_called_once()
        assert result == mock_client
