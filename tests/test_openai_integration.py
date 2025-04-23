import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from agents.common.model_manager import ModelManager, ModelType
from agents.common.security import SecurityUtils
import asyncio

@pytest.fixture
def mock_openai_response():
    """Fixture for mock OpenAI response."""
    return MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content="Test completion"
                )
            )
        ]
    )

@pytest.fixture
def model_manager():
    """Fixture for ModelManager with test API key."""
    return ModelManager(
        model_type=ModelType.GPT35,
        api_key="test-api-key"
    )

@pytest.mark.asyncio
async def test_get_completion_success(model_manager, mock_openai_response):
    """Test successful completion request."""
    with patch('openai.AsyncOpenAI.chat.completions.create', 
              new_callable=AsyncMock, 
              return_value=mock_openai_response):
        result = await model_manager.get_completion("Test prompt")
        assert result == "Test completion"

@pytest.mark.asyncio
async def test_get_completion_security_validation(model_manager, mock_openai_response):
    """Test security validation of API response."""
    # Mock a response with potentially dangerous content
    mock_openai_response.choices[0].message.content = "<script>alert('xss')</script>"
    
    with patch('openai.AsyncOpenAI.chat.completions.create', 
              new_callable=AsyncMock, 
              return_value=mock_openai_response):
        with pytest.raises(ValueError, match="Invalid API response detected"):
            await model_manager.get_completion("Test prompt")

@pytest.mark.asyncio
async def test_get_completion_rate_limiting(model_manager, mock_openai_response):
    """Test rate limiting functionality."""
    with patch('openai.AsyncOpenAI.chat.completions.create', 
              new_callable=AsyncMock, 
              return_value=mock_openai_response):
        # First request
        await model_manager.get_completion("Test prompt 1")
        # Second request should respect rate limit
        await model_manager.get_completion("Test prompt 2")

@pytest.mark.asyncio
async def test_get_completion_timeout(model_manager):
    """Test timeout handling."""
    with patch('openai.AsyncOpenAI.chat.completions.create', 
              new_callable=AsyncMock, 
              side_effect=asyncio.TimeoutError):
        with pytest.raises(asyncio.TimeoutError):
            await model_manager.get_completion("Test prompt", timeout=0.1)

@pytest.mark.asyncio
async def test_get_completion_api_error(model_manager):
    """Test API error handling."""
    with patch('openai.AsyncOpenAI.chat.completions.create', 
              new_callable=AsyncMock, 
              side_effect=Exception("API Error")):
        with pytest.raises(Exception, match="API Error"):
            await model_manager.get_completion("Test prompt")

def test_simple_completion():
    """Test simple completion mode."""
    manager = ModelManager(model_type=ModelType.SIMPLE)
    result = manager._simple_completion("Test prompt")
    assert result == "Processed: Test prompt" 