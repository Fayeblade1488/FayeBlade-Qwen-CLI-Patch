# Contributing to Qwen CLI Integration

Thank you for your interest in contributing! We welcome contributions from the community.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## How Can I Contribute?

### Reporting Bugs
- Use the GitHub Issues page
- Check if the bug has already been reported
- Include detailed steps to reproduce
- Provide system information (OS, Python version, etc.)
- Include error messages and logs

### Suggesting Enhancements
- Use GitHub Issues with the "enhancement" label
- Explain the use case and benefit
- Provide examples of how it would work
- Consider backward compatibility

### Code Contributions
- Fix bugs
- Implement new features
- Improve documentation
- Add tests
- Optimize performance

## Development Setup

### Prerequisites
- Python 3.7 or higher
- Git
- GitKraken CLI (optional, for testing Git features)
- Venice AI API key (for testing image generation)

### Initial Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/FayeBlade-Qwen-CLI-Patch.git
   cd FayeBlade-Qwen-CLI-Patch
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   
   # Development tools
   pip install pytest flake8 black isort pylint safety bandit
   ```

4. **Set Environment Variables**
   ```bash
   export VENICE_API_KEY="your_test_api_key"
   ```

5. **Run Tests**
   ```bash
   make test
   # Or directly:
   pytest tests/ -v
   ```

### Project Structure
```
FayeBlade-Qwen-CLI-Patch/
├── qwen_cli_integrator.py       # Main CLI entry point
├── venice_integration.py        # Venice AI module
├── gitkraken_integration.py     # GitKraken CLI wrapper
├── external_api_integrator.py   # External API support
├── auto_config.py               # Config utilities
├── requirements.txt             # Python dependencies
├── Makefile                     # Build automation
├── tests/                       # Test files
│   └── test_integration.py
└── docs/                        # Documentation
```

## Coding Standards

### Python Style Guide
- Follow PEP 8
- Use Black for code formatting: `black --line-length 120 .`
- Sort imports with isort: `isort --profile black .`
- Maximum line length: 120 characters

### Code Quality
```bash
# Format code
black --line-length 120 .

# Sort imports
isort --profile black .

# Lint code
flake8 . --max-line-length=120

# Type checking (if applicable)
mypy . --ignore-missing-imports
```

### Documentation
- Add docstrings to all functions and classes
- Use Google-style or NumPy-style docstrings
- Update README.md if adding new features
- Update AGENT_GUIDE.md for AI agent-relevant changes

Example docstring:
```python
def generate_image(prompt: str, model: str = "lustify-sdxl") -> Dict[str, Any]:
    """
    Generate an image using Venice AI.
    
    Args:
        prompt: Description of the image to generate
        model: The model to use for generation (default: lustify-sdxl)
        
    Returns:
        Dictionary with success status and image path
        
    Raises:
        ValueError: If prompt is empty
        APIError: If API request fails
    """
```

### Testing
- Write tests for new features
- Ensure existing tests pass
- Aim for >80% code coverage
- Test both success and failure cases

Example test:
```python
def test_image_generation():
    """Test basic image generation"""
    integrator = QwenCLIIntegrator()
    result = integrator.venice_generate_image(
        prompt="test image",
        model="lustify-sdxl"
    )
    assert result["success"] is True
    assert "generated_image_path" in result
```

### Security
- Never commit API keys or secrets
- Use environment variables for configuration
- Validate all user inputs
- Sanitize file paths
- Follow practices in [SECURITY.md](SECURITY.md)

## Submitting Changes

### Workflow

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation
   - Follow coding standards

3. **Test Your Changes**
   ```bash
   make test
   make lint
   make check  # If available
   ```

4. **Commit Your Changes**
   
   Use conventional commits format:
   ```bash
   git add .
   git commit -m "feat: add new image generation parameter"
   git commit -m "fix: resolve API timeout issue"
   git commit -m "docs: update installation instructions"
   ```
   
   Commit types:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code formatting
   - `refactor:` Code restructuring
   - `test:` Adding tests
   - `chore:` Maintenance tasks

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template
   - Link related issues

### Pull Request Guidelines

**Good PR Title Examples:**
- `feat: add support for new Venice AI model`
- `fix: resolve timeout in image upscaling`
- `docs: improve installation instructions`

**PR Description Should Include:**
- Summary of changes
- Motivation and context
- How to test the changes
- Related issues (e.g., "Fixes #123")
- Breaking changes (if any)
- Screenshots (for UI changes)

**Checklist:**
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No API keys or secrets committed
- [ ] Commit messages follow conventions
- [ ] PR description is complete

## Code Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, maintainers will merge
4. Delete your branch after merge

### Review Timeline
- Initial review: Within 3-5 days
- Follow-up reviews: Within 1-2 days
- Merge: After approval and CI passes

## Development Tips

### Running Locally
```bash
# Test CLI commands
python qwen_cli_integrator.py --help
python qwen_cli_integrator.py venice generate --prompt "test"

# Run specific tests
pytest tests/test_venice.py -v
pytest tests/test_venice.py::test_image_generation -v

# Generate coverage report
pytest --cov=. --cov-report=html
```

### Debugging
```bash
# Enable verbose output
python qwen_cli_integrator.py venice generate --prompt "test" --verbose

# Use Python debugger
import pdb; pdb.set_trace()
```

### Common Issues

**Import Errors:**
```bash
# Ensure you're in the virtual environment
which python  # Should point to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

**API Errors:**
```bash
# Verify API key
echo $VENICE_API_KEY

# Test API connectivity
python auto_config.py --verify
```

## Community

### Communication Channels
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: General questions and ideas
- Pull Requests: Code contributions

### Getting Help
- Check existing issues and documentation
- Read QUICKSTART_GUIDE.md and AGENT_GUIDE.md
- Ask in GitHub Discussions
- Be respectful and patient

## Recognition

Contributors will be acknowledged in:
- Release notes
- Contributors section
- GitHub contributors page

Thank you for contributing! 🎉

---

**Questions?** Open an issue or discussion on GitHub.

**Last Updated**: 2025-09-30