import pytest
import os
import tempfile
from pathlib import Path
from agents.code_analyzer.analyzer import CodeAnalyzer

@pytest.fixture
def sample_code():
    """Sample code for testing."""
    return """
def example_function(password="secret"):
    for i in range(10):
        for j in range(10):
            print(i * j)
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
async def test_pattern_analysis(sample_code):
    """Test pattern-based analysis."""
    analyzer = CodeAnalyzer()
    results = await analyzer._pattern_analysis(sample_code)
    
    assert 'security' in results
    assert 'performance' in results
    assert len(results['security']) > 0  # Should find the password pattern
    assert len(results['performance']) > 0  # Should find the nested loops

@pytest.mark.asyncio
async def test_invalid_file():
    """Test analysis of non-existent file."""
    analyzer = CodeAnalyzer()
    with pytest.raises(FileNotFoundError):
        await analyzer.analyze_file('non_existent_file.py')

@pytest.mark.asyncio
async def test_invalid_directory():
    """Test analysis of non-existent directory."""
    analyzer = CodeAnalyzer()
    with pytest.raises(NotADirectoryError):
        await analyzer.analyze_directory('non_existent_dir') 