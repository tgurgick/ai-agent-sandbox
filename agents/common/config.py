from typing import Dict, Any
import os
from dotenv import load_dotenv
from loguru import logger

class APIConfig:
    """Handles API configuration and validation."""
    
    def __init__(self):
        """Initialize API configuration."""
        load_dotenv()  # Load .env file if it exists
        self.config = self._load_config()
        self._validate_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            'api_key': os.getenv('OPENAI_API_KEY'),
            'temperature': float(os.getenv('MODEL_TEMPERATURE', '0.7')),
            'max_tokens': int(os.getenv('MAX_TOKENS', '1000')),
            'rate_limit_rpm': int(os.getenv('RATE_LIMIT_RPM', '60')),
            'model': os.getenv('DEFAULT_MODEL', 'gpt-3.5-turbo')
        }
        
    def _validate_config(self):
        """Validate that required API credentials are set."""
        if not self.config['api_key']:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please copy .env.example to .env and set your API key."
            )
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
        
    def update(self, key: str, value: Any):
        """Update a configuration value."""
        self.config[key] = value
        # Also update environment variable
        os.environ[key.upper()] = str(value)
        
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self.config.copy() 