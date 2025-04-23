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
            # API Configuration
            'api_key': os.getenv('OPENAI_API_KEY'),
            'temperature': float(os.getenv('MODEL_TEMPERATURE', '0.7')),
            'max_tokens': int(os.getenv('MAX_TOKENS', '1000')),
            'rate_limit_rpm': int(os.getenv('RATE_LIMIT_RPM', '60')),
            'model': os.getenv('DEFAULT_MODEL', 'gpt-3.5-turbo'),
            
            # Security Configuration
            'key_rotation_hours': int(os.getenv('API_KEY_ROTATION_HOURS', '24')),
            'request_timeout': int(os.getenv('REQUEST_TIMEOUT_SECONDS', '30')),
            'max_retries': int(os.getenv('MAX_RETRY_ATTEMPTS', '3')),
            'enable_response_validation': os.getenv('ENABLE_RESPONSE_VALIDATION', 'true').lower() == 'true',
            
            # Logging Configuration
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'log_format': os.getenv('LOG_FORMAT', ''),
            'log_sensitive_data': os.getenv('LOG_SENSITIVE_DATA', 'false').lower() == 'true'
        }
        
    def _validate_config(self):
        """Validate that required API credentials and security settings are correct."""
        if not self.config['api_key']:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please copy .env.example to .env and set your API key."
            )
            
        # Validate security settings
        if self.config['key_rotation_hours'] < 1:
            raise ValueError("API_KEY_ROTATION_HOURS must be at least 1")
            
        if self.config['request_timeout'] < 1:
            raise ValueError("REQUEST_TIMEOUT_SECONDS must be at least 1")
            
        if self.config['max_retries'] < 0:
            raise ValueError("MAX_RETRY_ATTEMPTS must be non-negative")
            
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
        
    def is_sensitive_data_logging_enabled(self) -> bool:
        """Check if sensitive data logging is enabled."""
        return self.config['log_sensitive_data']
        
    def get_security_settings(self) -> Dict[str, Any]:
        """Get security-related configuration settings."""
        return {
            'key_rotation_hours': self.config['key_rotation_hours'],
            'request_timeout': self.config['request_timeout'],
            'max_retries': self.config['max_retries'],
            'enable_response_validation': self.config['enable_response_validation']
        } 