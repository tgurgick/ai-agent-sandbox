from typing import Any, Dict, Optional
import time
import re
from loguru import logger
from datetime import datetime, timedelta

class SecurityUtils:
    """Security utilities for API interactions and data validation."""
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize input text to prevent injection attacks.
        
        Args:
            text: Input text to sanitize
            
        Returns:
            str: Sanitized text
        """
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>{}[\]]', '', text)
        return sanitized.strip()
    
    @staticmethod
    def validate_api_response(response: Dict[str, Any]) -> bool:
        """
        Validate API response for potential security issues.
        
        Args:
            response: API response to validate
            
        Returns:
            bool: True if response is valid
        """
        if not isinstance(response, dict):
            return False
            
        # Check for common injection patterns
        if any(isinstance(value, str) and re.search(r'<script|javascript:|eval\(', value.lower()) 
               for value in response.values()):
            return False
            
        return True

class APIKeyManager:
    """Manages API key rotation and validation."""
    
    def __init__(self, rotation_interval_hours: int = 24):
        self.rotation_interval = rotation_interval_hours
        self._key_history: Dict[str, datetime] = {}
        
    def should_rotate_key(self, api_key: str) -> bool:
        """
        Check if API key should be rotated.
        
        Args:
            api_key: Current API key
            
        Returns:
            bool: True if key should be rotated
        """
        if api_key not in self._key_history:
            self._key_history[api_key] = datetime.now()
            return False
            
        time_since_last_use = datetime.now() - self._key_history[api_key]
        return time_since_last_use > timedelta(hours=self.rotation_interval)
        
    def update_key_usage(self, api_key: str):
        """Update the last usage time for an API key."""
        self._key_history[api_key] = datetime.now()
        
    def get_key_age(self, api_key: str) -> Optional[timedelta]:
        """
        Get the age of an API key.
        
        Args:
            api_key: API key to check
            
        Returns:
            Optional[timedelta]: Age of the key if found, None otherwise
        """
        if api_key in self._key_history:
            return datetime.now() - self._key_history[api_key]
        return None 