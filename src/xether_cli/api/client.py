import httpx
from typing import Any, Dict, Optional
from xether_cli.core.config import load_config

class XetherAPIClient:
    def __init__(self):
        self.config = load_config()
        self.base_url = self.config.backend_url
        self.client = httpx.Client(base_url=self.base_url, follow_redirects=True)
        self._set_auth_header()
        
    def _set_auth_header(self):
        if self.config.access_token:
            self.client.headers.update({
                "Authorization": f"Bearer {self.config.access_token}"
            })
            
    def get(self, endpoint: str, **kwargs) -> httpx.Response:
        return self.client.get(endpoint, **kwargs)
        
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> httpx.Response:
        return self.client.post(endpoint, data=data, json=json, **kwargs)
        
    def delete(self, endpoint: str, **kwargs) -> httpx.Response:
        return self.client.delete(endpoint, **kwargs)
        
    def close(self):
        self.client.close()

def get_client() -> XetherAPIClient:
    return XetherAPIClient()
