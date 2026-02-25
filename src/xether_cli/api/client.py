import httpx
import time
from typing import Any, Dict, Optional
from xether_cli.core.config import load_config, save_config

class XetherAPIError(Exception):
    """Base exception for Xether API errors"""
    pass

class XetherNetworkError(XetherAPIError):
    """Network-related errors"""
    pass

class XetherHTTPError(XetherAPIError):
    """HTTP status errors"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")

class XetherAuthError(XetherAPIError):
    """Authentication errors"""
    pass

class XetherAPIClient:
    def __init__(self):
        self.config = load_config()
        self.base_url = self.config.backend_url
        self.client = httpx.Client(
            base_url=self.base_url,
            follow_redirects=True,
            timeout=self.config.request_timeout
        )
        self._set_auth_header()
        
    def _set_auth_header(self):
        if self.config.access_token:
            self.client.headers.update({
                "Authorization": f"Bearer {self.config.access_token}"
            })
    
    def _handle_auth_error(self):
        """Handle authentication errors by clearing expired tokens"""
        if self.config.access_token:
            self.config.access_token = None
            self.config.refresh_token = None
            save_config(self.config)
            # Remove header from current client
            self.client.headers.pop("Authorization", None)
    
    def _retry_request(self, method, *args, max_retries=None, **kwargs):
        """Retry logic for failed requests"""
        if max_retries is None:
            max_retries = self.config.max_retries
            
        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                response = method(*args, **kwargs)
                
                # Check for authentication errors
                if response.status_code == 401:
                    self._handle_auth_error()
                    raise XetherAuthError("Authentication failed - token may be expired")
                
                # Check for other HTTP errors
                if response.status_code >= 400:
                    raise XetherHTTPError(response.status_code, response.text)
                
                return response
                
            except httpx.RequestError as e:
                last_exception = XetherNetworkError(f"Network error: {e}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                break
            except (XetherAuthError, XetherHTTPError) as e:
                # Don't retry auth or HTTP errors
                raise e
        
        raise last_exception
            
    def get(self, endpoint: str, **kwargs) -> httpx.Response:
        return self._retry_request(self.client.get, endpoint, **kwargs)
        
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
             json: Optional[Dict[str, Any]] = None, **kwargs) -> httpx.Response:
        return self._retry_request(self.client.post, endpoint, data=data, json=json, **kwargs)
        
    def delete(self, endpoint: str, **kwargs) -> httpx.Response:
        return self._retry_request(self.client.delete, endpoint, **kwargs)
        
    def close(self):
        self.client.close()

def get_client() -> XetherAPIClient:
    return XetherAPIClient()
