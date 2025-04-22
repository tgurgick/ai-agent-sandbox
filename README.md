# AI Agent Sandbox

A collection of intelligent agents for code analysis, documentation, and development tasks.

## Transparency Note
This project was developed with the assistance of Cursor, an AI-powered IDE. The development process leveraged AI to help with code generation, testing, and documentation. All code is open source and transparent, with no hidden API calls or external dependencies beyond those explicitly listed in requirements.txt.

## Features

- Configurable model management
- Pattern-based and AI-powered code analysis
- Extensible agent architecture
- Comprehensive testing framework

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-agent-sandbox.git
cd ai-agent-sandbox
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export OPENAI_API_KEY=your_api_key_here
```

## Usage

Basic usage example:

```python
from agents.common.model_manager import ModelManager, ModelType

# Initialize a simple model manager
manager = ModelManager(ModelType.SIMPLE)

# Get a completion
result = await manager.get_completion("Your prompt here")
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development plans and guidelines.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
