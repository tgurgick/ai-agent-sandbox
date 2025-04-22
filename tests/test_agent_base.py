import pytest
import os
import yaml
from agents.common.base import AgentBase
from agents.common.model_manager import ModelType

class TestAgent(AgentBase):
    """Test agent for testing AgentBase functionality."""
    pass

def test_agent_base_initialization():
    """Test basic AgentBase initialization."""
    agent = TestAgent()
    assert agent.config is not None
    assert agent.model_manager is not None
    assert agent.logger is not None
    
def test_agent_base_custom_config():
    """Test AgentBase with custom configuration."""
    # Create a temporary config file
    test_config = {
        'model_config': {
            'default_model': 'SIMPLE',
            'api_key': 'test_key'
        }
    }
    
    config_path = 'test_config.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(test_config, f)
        
    try:
        agent = TestAgent(config_path)
        assert agent.get_config('model_config.default_model') == 'SIMPLE'
    finally:
        os.remove(config_path)
        
def test_agent_base_config_loading():
    """Test configuration loading functionality."""
    agent = TestAgent()
    
    # Test getting existing config
    assert agent.get_config('model_config.default_model') is not None
    
    # Test getting non-existent config with default
    assert agent.get_config('non.existent.key', 'default') == 'default'
    
def test_agent_base_config_update():
    """Test configuration update functionality."""
    agent = TestAgent()
    
    # Update a config value
    agent.update_config('model_config.default_model', 'GPT35')
    assert agent.get_config('model_config.default_model') == 'GPT35'
    
@pytest.mark.asyncio
async def test_agent_base_lifecycle():
    """Test agent initialization and cleanup."""
    agent = TestAgent()
    await agent.initialize()
    await agent.cleanup()
    
def test_agent_base_model_manager_initialization():
    """Test model manager initialization."""
    agent = TestAgent()
    assert agent.model_manager.model_type == ModelType.SIMPLE 