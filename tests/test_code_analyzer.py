import pytest
import os
import tempfile
from pathlib import Path
from agents.code_analyzer.analyzer import CodeAnalyzer
from unittest.mock import AsyncMock, patch, MagicMock
import json
from agents.common.model_manager import ModelType

@pytest.fixture
def mock_model_manager():
    manager = MagicMock()
    manager.model_type = ModelType.OPENAI
    manager.get_completion = AsyncMock()
    return manager

@pytest.fixture
def sample_code():
    """Sample code for testing."""
    return """
def process_data(data):
    password = "secret123"  # Security issue
    for i in range(1000):  # Performance issue
        for j in range(1000):
            result = i * j
    return result
"""

@pytest.fixture
def temp_file(sample_code):
    """Create a temporary file with sample code."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(sample_code)
        return f.name

@pytest.fixture
def temp_dir(temp_file):
    """Create a temporary directory with the sample file."""
    temp_dir = tempfile.mkdtemp()
    file_name = os.path.basename(temp_file)
    new_path = os.path.join(temp_dir, file_name)
    os.rename(temp_file, new_path)
    return temp_dir

@pytest.fixture
def mock_ai_response():
    return json.dumps({
        "security": [{
            "line": 3,
            "description": "Hardcoded password",
            "severity": "high",
            "suggestion": "Use environment variables or secure storage"
        }],
        "performance": [{
            "line": 4,
            "description": "Nested loops with large ranges",
            "severity": "medium",
            "suggestion": "Consider using vectorized operations"
        }],
        "code_style": [],
        "potential_bugs": [],
        "best_practices": []
    })

@pytest.mark.asyncio
async def test_analyze_file(temp_file):
    """Test analyzing a single file."""
    analyzer = CodeAnalyzer()
    results = await analyzer.analyze_file(temp_file)
    
    assert 'file' in results
    assert 'pattern_analysis' in results
    assert 'security' in results['pattern_analysis']
    assert 'performance' in results['pattern_analysis']
    
    # Clean up
    os.unlink(temp_file)

@pytest.mark.asyncio
async def test_analyze_directory(temp_dir):
    """Test analyzing a directory."""
    analyzer = CodeAnalyzer()
    results = await analyzer.analyze_directory(temp_dir)
    
    assert 'files' in results
    assert len(results['files']) == 1
    
    # Clean up
    for file in Path(temp_dir).glob('*.py'):
        os.unlink(file)
    os.rmdir(temp_dir)

@pytest.mark.asyncio
async def test_pattern_analysis(mock_model_manager, sample_code):
    """Test pattern-based analysis."""
    analyzer = CodeAnalyzer()
    analyzer.model_manager = mock_model_manager
    
    results = await analyzer._pattern_analysis(sample_code)
    
    assert 'security' in results
    assert len(results['security']) > 0
    assert results['security'][0]['severity'] == 'high'
    assert 'password' in results['security'][0]['match'].lower()

@pytest.mark.asyncio
async def test_ai_analysis_success(mock_model_manager, sample_code, mock_ai_response):
    analyzer = CodeAnalyzer()
    analyzer.model_manager = mock_model_manager
    mock_model_manager.get_completion.return_value = mock_ai_response
    
    results = await analyzer._ai_analysis(sample_code)
    
    assert 'security' in results
    assert len(results['security']) > 0
    assert results['security'][0]['line'] == 3
    assert results['security'][0]['severity'] == 'high'
    assert 'password' in results['security'][0]['description'].lower()

@pytest.mark.asyncio
async def test_ai_analysis_fallback(mock_model_manager, sample_code):
    analyzer = CodeAnalyzer()
    analyzer.model_manager = mock_model_manager
    mock_model_manager.get_completion.return_value = "Invalid JSON response"
    
    results = await analyzer._ai_analysis(sample_code)
    
    assert all(category in results for category in analyzer.analysis_categories)
    assert isinstance(results['security'], list)

@pytest.mark.asyncio
async def test_analyze_file(mock_model_manager, tmp_path, sample_code, mock_ai_response):
    # Create a temporary file
    test_file = tmp_path / "test.py"
    test_file.write_text(sample_code)
    
    analyzer = CodeAnalyzer()
    analyzer.model_manager = mock_model_manager
    mock_model_manager.get_completion.return_value = mock_ai_response
    
    results = await analyzer.analyze_file(str(test_file))
    
    assert 'file' in results
    assert 'pattern_analysis' in results
    assert 'ai_analysis' in results
    assert str(test_file) in results['file']

@pytest.mark.asyncio
async def test_analyze_directory(mock_model_manager, tmp_path, sample_code, mock_ai_response):
    # Create a temporary directory with Python files
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    
    (test_dir / "file1.py").write_text(sample_code)
    (test_dir / "file2.py").write_text(sample_code)
    
    analyzer = CodeAnalyzer()
    analyzer.model_manager = mock_model_manager
    mock_model_manager.get_completion.return_value = mock_ai_response
    
    results = await analyzer.analyze_directory(str(test_dir))
    
    assert 'files' in results
    assert len(results['files']) == 2
    assert all('file' in f for f in results['files'])

@pytest.mark.asyncio
async def test_error_handling(mock_model_manager, tmp_path):
    # Test with non-existent file
    analyzer = CodeAnalyzer()
    analyzer.model_manager = mock_model_manager
    
    with pytest.raises(FileNotFoundError):
        await analyzer.analyze_file(str(tmp_path / "nonexistent.py"))
        
    # Test with non-existent directory
    with pytest.raises(NotADirectoryError):
        await analyzer.analyze_directory(str(tmp_path / "nonexistent_dir")) 