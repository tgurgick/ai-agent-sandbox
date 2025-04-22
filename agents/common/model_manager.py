from enum import Enum
from typing import Optional, Dict, Any
import os
import time
from loguru import logger
from .config import APIConfig

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
        self._validate_config()
        
    def _validate_config(self):
        """Validate the configuration and API key if needed"""
        if self.model_type != ModelType.SIMPLE and not self.api_key:
            raise ValueError("API key is required for AI models")
            
    async def get_completion(self, prompt: str) -> str:
        """
        Get completion from the selected model with rate limiting
        
        Args:
            prompt: The input prompt for the model
            
        Returns:
            str: The model's completion
        """
        try:
            if self.model_type == ModelType.SIMPLE:
                return self._simple_completion(prompt)
                
            # Implement rate limiting
            self._check_rate_limit()
            return await self._ai_completion(prompt)
        except Exception as e:
            logger.error(f"Error getting completion: {e}")
            raise
            
    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        min_interval = 60 / self.api_config.get('rate_limit_rpm', 60)
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            
        self._last_request_time = time.time()
            
    def _simple_completion(self, prompt: str) -> str:
        """Simple pattern-based completion (placeholder)"""
        # TODO: Implement basic pattern matching
        return "Simple completion placeholder"
        
    async def _ai_completion(self, prompt: str) -> str:
        """AI-based completion using OpenAI API"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            response = await client.chat.completions.create(
                model=self.model_type.value,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.api_config.get('temperature', 0.7),
                max_tokens=self.api_config.get('max_tokens', 1000)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise 