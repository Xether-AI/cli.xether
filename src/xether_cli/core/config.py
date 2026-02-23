import json
import os
from pathlib import Path
from pydantic import BaseModel, Field

CONFIG_DIR = Path.home() / ".xether"
CONFIG_FILE = CONFIG_DIR / "config.json"

class XetherConfig(BaseModel):
    backend_url: str = Field(default="http://localhost:8000")
    access_token: str | None = Field(default=None)
    refresh_token: str | None = Field(default=None)
    
def load_config() -> XetherConfig:
    if not CONFIG_FILE.exists():
        return XetherConfig()
    
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return XetherConfig(**data)
    except Exception:
        return XetherConfig()

def save_config(config: XetherConfig):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config.model_dump(), f, indent=4)
