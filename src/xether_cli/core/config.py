import json
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, field_validator

CONFIG_DIR = Path.home() / ".xether"
CONFIG_FILE = CONFIG_DIR / "config.json"

class XetherConfig(BaseModel):
    backend_url: str = Field(
        default_factory=lambda: os.getenv("XETHER_BACKEND_URL", "http://localhost:8000")
    )
    access_token: Optional[str] = Field(
        default_factory=lambda: os.getenv("XETHER_ACCESS_TOKEN")
    )
    refresh_token: Optional[str] = Field(
        default_factory=lambda: os.getenv("XETHER_REFRESH_TOKEN")
    )
    request_timeout: float = Field(
        default_factory=lambda: float(os.getenv("XETHER_REQUEST_TIMEOUT", "30.0"))
    )
    max_retries: int = Field(
        default_factory=lambda: int(os.getenv("XETHER_MAX_RETRIES", "3"))
    )
    
    @field_validator('backend_url')
    @classmethod
    def validate_backend_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('backend_url must start with http:// or https://')
        return v
    
    @field_validator('request_timeout')
    @classmethod
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError('request_timeout must be positive')
        return v
    
    @field_validator('max_retries')
    @classmethod
    def validate_retries(cls, v):
        if v < 0:
            raise ValueError('max_retries cannot be negative')
        return v
    
def load_config() -> XetherConfig:
    if not CONFIG_FILE.exists():
        return XetherConfig()
    
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return XetherConfig(**data)
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in config file: {e}")
        return XetherConfig()
    except Exception as e:
        print(f"Warning: Error loading config: {e}")
        return XetherConfig()

def save_config(config: XetherConfig):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config.model_dump(), f, indent=4)
