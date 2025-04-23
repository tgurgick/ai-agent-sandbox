from enum import Enum
from typing import Optional, Dict, Any, List
import os
import time
import asyncio
import openai
from loguru import logger
from .config import APIConfig
from .security import SecurityUtils, APIKeyManager

class ModelType(Enum):
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    SIMPLE = "simple-regex"

class ModelManager:
    def __init__(self, model_type: ModelType, api_key: Optional[str] = None):
        self.model_type = model_type
        self.api_config = APIConfig()
        self.api_key = api_key or self.api_config.get('api_key')
        self._last_request_time = 0
        self._key_manager = APIKeyManager()
        self._client = None
        self._validate_config()
        
    def _validate_config(self):
        """Validate the configuration and API key if needed"""
        if self.model_type != ModelType.SIMPLE and not self.api_key:
            raise ValueError("API key is required for AI models")
            
    def _get_client(self) -> openai.AsyncOpenAI:
        """Get or create OpenAI client with proper configuration."""
        if not self._client:
            self._client = openai.AsyncOpenAI(
                api_key=self.api_key,
                timeout=self.api_config.get('request_timeout', 30),
                max_retries=self.api_config.get('max_retries', 3)
            )
        return self._client
            
    async def get_completion(self, prompt: str, timeout: int = 30) -> str:
        """
        Get completion from the selected model with rate limiting and security checks
        
        Args:
            prompt: The input prompt for the model
            timeout: Maximum time in seconds to wait for response
            
        Returns:
            str: The model's completion
        """
        try:
            # Sanitize input
            sanitized_prompt = SecurityUtils.sanitize_input(prompt)
            
            if self.model_type == ModelType.SIMPLE:
                return self._simple_completion(sanitized_prompt)
                
            # Check API key rotation
            if self._key_manager.should_rotate_key(self.api_key):
                logger.warning("API key should be rotated due to age")
                
            # Implement rate limiting
            self._check_rate_limit()
            
            # Update key usage
            self._key_manager.update_key_usage(self.api_key)
            
            # Get completion with timeout
            return await asyncio.wait_for(
                self._ai_completion(sanitized_prompt),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error("API request timed out")
            raise
        except Exception as e:
            logger.error(f"Error getting completion: {e}")
            raise
            
    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        min_interval = 60.0 / self.api_config.get('rate_limit_rpm', 60)
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
            
        self._last_request_time = time.time()
        
    def _simple_completion(self, prompt: str) -> str:
        """Simple regex-based completion for testing."""
        return f"Processed: {prompt}"
        
    async def _ai_completion(self, prompt: str) -> str:
        """Get completion from AI model with response validation."""
        try:
            client = self._get_client()
            
            # Prepare messages with system context
            messages: List[Dict[str, str]] = [
                {"role": "system", "content": "You are a helpful AI assistant focused on code analysis and development tasks."},
                {"role": "user", "content": prompt}
            ]
            
            # Make API call with retries
            response = await client.chat.completions.create(
                model=self.model_type.value,
                messages=messages,
                temperature=self.api_config.get('temperature', 0.7),
                max_tokens=self.api_config.get('max_tokens', 1000)
            )
            
            # Extract and validate response
            completion = response.choices[0].message.content
            if not completion:
                raise ValueError("Empty response from API")
                
            # Validate response content
            if not SecurityUtils.validate_api_response({"completion": completion}):
                raise ValueError("Invalid API response detected")
                
            return completion
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in AI completion: {e}")
            raise 