from typing import Dict, List, Any, Optional
import re
import json
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
        self.analysis_categories = [
            'security',
            'performance',
            'code_style',
            'potential_bugs',
            'best_practices'
        ]
        
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
        prompt = f"""Analyze the following Python code for potential issues, improvements, and best practices:

{content}

Provide a structured analysis including the following categories:
1. Security concerns - Identify potential security vulnerabilities, sensitive data exposure, or unsafe practices
2. Performance issues - Find inefficient code patterns, potential bottlenecks, or resource-intensive operations
3. Code style and readability - Evaluate code organization, naming conventions, and overall maintainability
4. Potential bugs - Identify possible logical errors, edge cases, or problematic patterns
5. Best practice violations - Check against Python best practices and common conventions

For each category, provide:
- A list of specific issues found
- The line numbers where issues occur
- A brief explanation of each issue
- Suggested improvements where applicable

Format the response as a JSON object with these categories as keys. Each category should contain an array of issues, where each issue has:
- "line": line number
- "description": description of the issue
- "severity": "low", "medium", or "high"
- "suggestion": optional improvement suggestion"""

        try:
            response = await self.model_manager.get_completion(prompt)
            return self._parse_ai_response(response)
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {e}")
            return {'error': str(e)}
            
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the AI response into a structured format.
        
        Args:
            response: The raw AI response
            
        Returns:
            Dict containing parsed analysis results
        """
        try:
            # Try to parse as JSON
            parsed = json.loads(response)
            
            # Validate structure
            if not isinstance(parsed, dict):
                raise ValueError("Response is not a JSON object")
                
            # Ensure all categories exist
            for category in self.analysis_categories:
                if category not in parsed:
                    parsed[category] = []
                    
            return parsed
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract structured information
            self.logger.warning("Failed to parse AI response as JSON, attempting to extract information")
            return self._extract_structured_info(response)
            
    def _extract_structured_info(self, response: str) -> Dict[str, Any]:
        """
        Extract structured information from a non-JSON response.
        
        Args:
            response: The raw AI response
            
        Returns:
            Dict containing extracted analysis results
        """
        result = {category: [] for category in self.analysis_categories}
        
        # Look for category headers and their content
        for category in self.analysis_categories:
            category_pattern = f"{category}.*?:"
            category_match = re.search(category_pattern, response, re.IGNORECASE)
            
            if category_match:
                # Find the next category or end of response
                next_category = None
                for other_category in self.analysis_categories:
                    if other_category != category:
                        next_match = re.search(f"{other_category}.*?:", response[category_match.end():], re.IGNORECASE)
                        if next_match:
                            next_category = category_match.end() + next_match.start()
                            break
                            
                # Extract content between current category and next
                content_end = next_category if next_category else len(response)
                category_content = response[category_match.end():content_end]
                
                # Extract issues from content
                issues = re.finditer(r"line\s*(\d+).*?severity\s*:\s*(low|medium|high)", category_content, re.IGNORECASE)
                for issue in issues:
                    result[category].append({
                        'line': int(issue.group(1)),
                        'severity': issue.group(2).lower(),
                        'description': 'Issue found',  # Simplified for now
                        'suggestion': 'Check the code'  # Simplified for now
                    })
                    
        return result 