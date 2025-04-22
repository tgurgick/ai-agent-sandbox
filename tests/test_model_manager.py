import pytest
from agents.common.model_manager import ModelManager, ModelType

def test_model_manager_initialization():
    """Test basic ModelManager initialization"""
    manager = ModelManager(ModelType.SIMPLE)
    assert manager.model_type == ModelType.SIMPLE
    
def test_model_manager_api_key_validation():
    """Test API key validation"""
    with pytest.raises(ValueError):
        ModelManager(ModelType.GPT35)  # Should raise error without API key
        
@pytest.mark.asyncio
async def test_simple_completion():
    """Test simple completion functionality"""
    manager = ModelManager(ModelType.SIMPLE)
    result = await manager.get_completion("test prompt")
    assert isinstance(result, str)
    assert result == "Simple completion placeholder"
    
@pytest.mark.asyncio
async def test_ai_completion_not_implemented():
    """Test that AI completion raises NotImplementedError"""
    manager = ModelManager(ModelType.GPT35, api_key="test_key")
    with pytest.raises(NotImplementedError):
        await manager.get_completion("test prompt") 