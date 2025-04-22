from typing import Dict, List, Any, Optional
import re
from pathlib import Path
from ..common.base import AgentBase
from ..common.model_manager import ModelType

class CodeAnalyzer(AgentBase):
    """Agent for analyzing code for various issues and improvements."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the CodeAnalyzer.
        
        Args:
            config_path: Optional path to custom configuration file
        """
        super().__init__(config_path)
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load analysis patterns from configuration."""
        return self.get_config('agents.code_analyzer.patterns', {})
        
    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single file for issues.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dict containing analysis results
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            content = file_path.read_text()
            results = {
                'file': str(file_path),
                'pattern_analysis': await self._pattern_analysis(content),
                'ai_analysis': await self._ai_analysis(content) if self.model_manager.model_type != ModelType.SIMPLE else None
            }
            
            return results
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
            raise
            
    async def analyze_directory(self, dir_path: str) -> Dict[str, Any]:
        """
        Analyze all files in a directory recursively.
        
        Args:
            dir_path: Path to the directory to analyze
            
        Returns:
            Dict containing analysis results for all files
        """
        try:
            dir_path = Path(dir_path)
            if not dir_path.is_dir():
                raise NotADirectoryError(f"Not a directory: {dir_path}")
                
            results = {'files': []}
            for file_path in dir_path.rglob('*.py'):  # Currently only analyzing Python files
                try:
                    file_results = await self.analyze_file(str(file_path))
                    results['files'].append(file_results)
                except Exception as e:
                    self.logger.warning(f"Error analyzing {file_path}: {e}")
                    
            return results
        except Exception as e:
            self.logger.error(f"Error analyzing directory {dir_path}: {e}")
            raise
            
    async def _pattern_analysis(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform pattern-based analysis on code content.
        
        Args:
            content: The code content to analyze
            
        Returns:
            Dict containing pattern analysis results
        """
        results = {}
        for category, patterns in self.patterns.items():
            results[category] = []
            for pattern in patterns:
                matches = re.finditer(pattern['pattern'], content, re.MULTILINE)
                for match in matches:
                    results[category].append({
                        'pattern': pattern['pattern'],
                        'severity': pattern.get('severity', 'medium'),
                        'line': content[:match.start()].count('\n') + 1,
                        'match': match.group()
                    })
                    
        return results
        
    async def _ai_analysis(self, content: str) -> Dict[str, Any]:
        """
        Perform AI-based analysis on code content.
        
        Args:
            content: The code content to analyze
            
        Returns:
            Dict containing AI analysis results
        """
        prompt = f"""Analyze the following code for potential issues, improvements, and best practices:

{content}

Provide a structured analysis including:
1. Security concerns
2. Performance issues
3. Code style and readability
4. Potential bugs
5. Best practice violations

Format the response as a JSON object with these categories."""

        try:
            response = await self.model_manager.get_completion(prompt)
            # TODO: Parse the response into a structured format
            return {'raw_response': response}
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {e}")
            return {'error': str(e)} 