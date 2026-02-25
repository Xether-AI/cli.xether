import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch
from xether_cli.core.config import XetherConfig, load_config, save_config

class TestXetherConfig:
    """Test XetherConfig model"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = XetherConfig()
        assert config.backend_url == "http://localhost:8000"
        assert config.access_token is None
        assert config.refresh_token is None
        assert config.request_timeout == 30.0
        assert config.max_retries == 3
    
    @patch.dict('os.environ', {
        'XETHER_BACKEND_URL': 'https://api.xether.ai',
        'XETHER_ACCESS_TOKEN': 'test-token',
        'XETHER_REQUEST_TIMEOUT': '60',
        'XETHER_MAX_RETRIES': '5'
    })
    def test_environment_variables(self):
        """Test configuration from environment variables"""
        config = XetherConfig()
        assert config.backend_url == "https://api.xether.ai"
        assert config.access_token == "test-token"
        assert config.request_timeout == 60.0
        assert config.max_retries == 5
    
    def test_invalid_backend_url(self):
        """Test validation of backend URL"""
        with pytest.raises(ValueError, match="backend_url must start with http:// or https://"):
            XetherConfig(backend_url="invalid-url")
    
    def test_invalid_timeout(self):
        """Test validation of timeout"""
        with pytest.raises(ValueError, match="request_timeout must be positive"):
            XetherConfig(request_timeout=-1)
    
    def test_invalid_retries(self):
        """Test validation of retries"""
        with pytest.raises(ValueError, match="max_retries cannot be negative"):
            XetherConfig(max_retries=-1)

class TestConfigFunctions:
    """Test configuration loading and saving functions"""
    
    def test_load_config_no_file(self):
        """Test loading config when no file exists"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".xether"
            with patch('xether_cli.core.config.CONFIG_DIR', config_dir):
                config = load_config()
                assert isinstance(config, XetherConfig)
                assert config.backend_url == "http://localhost:8000"
    
    def test_load_config_valid_file(self):
        """Test loading config from valid JSON file"""
        test_config = {
            "backend_url": "https://test.xether.ai",
            "access_token": "test-token",
            "request_timeout": 45.0,
            "max_retries": 2
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".xether"
            config_file = config_dir / "config.json"
            config_dir.mkdir(parents=True)
            
            with open(config_file, 'w') as f:
                json.dump(test_config, f)
            
            with patch('xether_cli.core.config.CONFIG_FILE', config_file):
                config = load_config()
                assert config.backend_url == "https://test.xether.ai"
                assert config.access_token == "test-token"
                assert config.request_timeout == 45.0
                assert config.max_retries == 2
    
    def test_load_config_invalid_json(self):
        """Test loading config with invalid JSON"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".xether"
            config_file = config_dir / "config.json"
            config_dir.mkdir(parents=True)
            
            with open(config_file, 'w') as f:
                f.write("invalid json content")
            
            with patch('xether_cli.core.config.CONFIG_FILE', config_file):
                # Should return default config on JSON error
                config = load_config()
                assert isinstance(config, XetherConfig)
                assert config.backend_url == "http://localhost:8000"
    
    def test_save_config(self):
        """Test saving configuration to file"""
        config = XetherConfig(
            backend_url="https://save-test.xether.ai",
            access_token="save-token"
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".xether"
            config_file = config_dir / "config.json"
            
            with patch('xether_cli.core.config.CONFIG_DIR', config_dir):
                with patch('xether_cli.core.config.CONFIG_FILE', config_file):
                    save_config(config)
                    
                    # Verify file was created and contains correct data
                    assert config_file.exists()
                    with open(config_file, 'r') as f:
                        saved_data = json.load(f)
                    
                    assert saved_data["backend_url"] == "https://save-test.xether.ai"
                    assert saved_data["access_token"] == "save-token"
