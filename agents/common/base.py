from typing import Dict, Any, Optional
import yaml
import os
from loguru import logger
from .model_manager import ModelManager, ModelType

class AgentBase:
    """Base class for all agents in the system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the agent with configuration.
        
        Args:
            config_path: Path to the configuration file. If None, uses default config.
        """
        self.config = self._load_config(config_path)
        self.model_manager = self._initialize_model_manager()
        self.logger = logger.bind(agent=self.__class__.__name__)
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config',
                'default_config.yaml'
            )
            
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
            
    def _initialize_model_manager(self) -> ModelManager:
        """Initialize the model manager based on configuration."""
        model_type = ModelType[self.config['model_config']['default_model']]
        api_key = os.getenv("OPENAI_API_KEY")
        return ModelManager(model_type, api_key)
        
    async def initialize(self):
        """Initialize the agent's resources."""
        self.logger.info("Initializing agent")
        # Add any initialization logic here
        
    async def cleanup(self):
        """Clean up the agent's resources."""
        self.logger.info("Cleaning up agent")
        # Add any cleanup logic here
        
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key in dot notation (e.g., 'model_config.default_model')
            default: Default value if key not found
            
        Returns:
            The configuration value or default
        """
        try:
            value = self.config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def update_config(self, key: str, value: Any):
        """
        Update a configuration value.
        
        Args:
            key: Configuration key in dot notation
            value: New value to set
        """
        keys = key.split('.')
        current = self.config
        for k in keys[:-1]:
            current = current[k]
        current[keys[-1]] = value 