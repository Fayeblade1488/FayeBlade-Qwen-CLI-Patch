# 🚀 Qwen CLI Integration: GitKraken & Venice AI 🎨

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/Fayeblade1488/FayeBlade-Qwen-CLI-Patch?style=social)](https://github.com/Fayeblade1488/FayeBlade-Qwen-CLI-Patch/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/Fayeblade1488/FayeBlade-Qwen-CLI-Patch)](https://github.com/Fayeblade1488/FayeBlade-Qwen-CLI-Patch/issues)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<img width="1536" height="1024" alt="Qwen CLI Integration Banner" src="https://github.com/user-attachments/assets/a23c49db-d0b8-4468-aa5a-a85e1b3ab0f3" />

```
╔══════════════════════════════════════════════════════════════════════╗
║                          Qwen CLI Integrator                         ║
║                GitKraken + Venice AI + External APIs                 ║
║                                                                      ║
║  🔐 Secure API Key Management     🧠 AI-Powered Workflows            ║
║  🖼️ Uncensored Image Generation   📡 Real-time Model Updates         ║
║  ⚡ Auto-Configuration             🛡️ Security-First Approach         ║
╚══════════════════════════════════════════════════════════════════════╝
```

**A unified CLI tool integrating GitKraken, Venice AI image generation, and external API providers**

[Features](#-features) •
[Installation](#-installation) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🔧 Prerequisites](#-prerequisites)
- [📦 Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
- [📚 Documentation](#-documentation)
- [🔒 Security](#-security)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 📖 Overview

This repository provides a comprehensive integration between Qwen CLI and powerful tools:

1. **GitKraken CLI**: A complete, AI-powered Git workflow enhancement suite that allows for seamless Git operations with AI assistance
2. **Venice AI Integration**: An uncensored AI system that provides both image generation and chat capabilities
3. **External API Integration**: Support for multiple AI providers including Venice AI, with config loading from Raycast format

The integration is designed to work within the Qwen CLI ecosystem, allowing users to leverage advanced Git workflows and AI-powered services directly from their command line. **Note: While the system can read provider configurations from Raycast's format, Raycast is NOT required for usage.**

## ✨ Features

### 🎯 GitKraken CLI Integration
- 🤖 **AI-Powered Git Operations**: Automated commit messages, conflict resolution, and PR creation
- 📊 **Workspace Management**: Organize and manage multiple repositories
- 🔄 **Issue Tracking**: Seamlessly integrate with issue management systems
- 🔑 **Authentication**: Secure provider token management

### 🖼️ Venice AI Integration  
- 🎨 **Uncensored Image Generation**: Using `lustify-sdxl` model (default: 50 steps)
- ⬆️ **Image Upscaling**: 4x enhancement with quality preservation
- 📐 **Flexible Aspect Ratios**: Square, tall, and wide formats supported
- ⚡ **Automatic Processing**: Optional auto-upscale after generation

### 🔌 External API Support
- 📡 **Multi-Provider**: Support for various AI API providers
- 🔄 **Config Auto-Update**: Automatic Raycast configuration synchronization
- 🛠️ **Extensible**: Easy integration of new providers

## 🔧 Prerequisites

- **Python 3.7+** (3.11+ recommended)
- **GitKraken CLI** (optional, for Git operations)
- **Venice AI API Key** (required for image generation)

### System Requirements
- **OS**: macOS, Linux, or Windows
- **Memory**: 2GB+ RAM recommended
- **Storage**: 100MB+ for dependencies

## 📦 Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/Fayeblade1488/FayeBlade-Qwen-CLI-Patch.git
cd FayeBlade-Qwen-CLI-Patch

# Install dependencies
pip install -r requirements.txt

# Set up your Venice API key
export VENICE_API_KEY="your_api_key_here"

# Verify installation
python qwen_cli_integrator.py --help
```

### Alternative Installation (Development)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -r requirements.txt
pip install pytest flake8 black  # Optional dev tools
```

## 🚀 Quick Start

### Command Line Interface

The main interface is through the `qwen_cli_integrator.py` script:

```bash
python qwen_cli_integrator.py --help
```

#### GitKraken Commands

Generate a commit message with AI:
```bash
python qwen_cli_integrator.py gitkraken ai_commit
```

List workspaces:
```bash
python qwen_cli_integrator.py gitkraken workspace_list
```

Start a new work item:
```bash
python qwen_cli_integrator.py gitkraken work_start "my-feature" --issue "ISS-123"
```

#### Venice AI Commands

Generate an uncensored image:
```bash
python qwen_cli_integrator.py venice generate --prompt "fantasy landscape at sunset"
```

Generate an image with specific parameters:
```bash
python qwen_cli_integrator.py venice generate \
  --prompt "cyberpunk cityscape" \
  --model lustify-sdxl \
  --aspect-ratio wide \
  --steps 30 \
  --cfg-scale 7.0 \
  --upscale
```

Upscale an existing image:
```bash
python qwen_cli_integrator.py venice upscale --input my_image.png --scale 4
```

List available models:
```bash
python qwen_cli_integrator.py venice list-models
```

### Python API

You can also use the integrations directly in Python:

```python
from qwen_cli_integrator import QwenCLIIntegrator

integrator = QwenCLIIntegrator()

# GitKraken example
result = integrator.gitkraken_command('workspace_list')
print(result)

# Venice example
result = integrator.venice_generate_image(
    prompt="abstract art with vibrant colors",
    model="lustify-sdxl",
    upscale=True
)
print(result)
```

## Configuration

### GitKraken CLI

Make sure the `gk` command is in your PATH. If GitKraken CLI is installed but not in PATH, you may need to add it:

```bash
# For macOS with Homebrew
export PATH="/opt/homebrew/bin:$PATH"

# For Linux with snap
export PATH="$HOME/snap/bin:$PATH"
```

### Venice AI

Set your Venice API key as an environment variable:

```bash
export VENICE_API_KEY="your_api_key_here"
```

Or pass it directly to the VeniceAIImageGenerator constructor in code.

## Safety Notice

When using the uncensored image generation capabilities, please be aware that the generated content may not be filtered for adult content. Use appropriate discretion and consider your usage context.

## API Endpoints Used

- GitKraken CLI: Local command-line interface
- Venice AI: `https://api.venice.ai/api/v1/image/generate` and related endpoints

## Troubleshooting

1. **GitKraken CLI not found**: Ensure that the `gk` command is in your system PATH
2. **Venice API key error**: Make sure you have set the `VENICE_API_KEY` environment variable
3. **Rate limiting**: You may encounter rate limits with the Venice API depending on your account tier

## Development

### Setting Up Development Environment

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Fayeblade1488/FayeBlade-Qwen-CLI-Patch.git
   cd FayeBlade-Qwen-CLI-Patch
   ```

2. **Create a Virtual Environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**:
   ```bash
   export VENICE_API_KEY="your_venice_api_key"
   ```

### Project Structure

```
.
├── gitkraken_integration.py      # GitKraken CLI wrapper
├── venice_integration.py         # Venice AI image generation & verification
├── external_api_integrator.py    # External AI provider integration
├── qwen_cli_integrator.py        # Main CLI orchestrator
├── auto_config.py                # Auto-configuration script
├── tests/                        # Pytest suite (e.g. tests/test_integration.py)
├── AGENT_GUIDE.md                # Documentation for AI agents
├── QUICKSTART_GUIDE.md           # Beginner-friendly guide
└── README.md                     # This file
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_integration.py
```

### Code Quality

This project follows:
- **Python PEP 8** style guidelines
- **Google-style docstrings** for all public functions/methods/classes
- **Type hints** where applicable
- **Security-first approach**: API keys are never logged or stored in configs

## 📚 Documentation

Comprehensive documentation is available:

- **[🚀 Quick Start Guide](QUICKSTART_GUIDE.md)** - Get started in minutes
- **[🤖 Agent Guide](AGENT_GUIDE.md)** - For AI CLI agents and automation
- **[🔒 Security Policy](SECURITY.md)** - Security best practices and reporting
- **[🤝 Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[🛡️ Code of Conduct](CODE_OF_CONDUCT.md)** - Community standards

### API Documentation

All modules are fully documented with docstrings:

```python
# View help for any module
import venice_integration
help(venice_integration.VeniceAIImageGenerator)
```

## 🔒 Security

### 🔑 API Key Management
- ❌ **Never** commit API keys to version control
- ✅ **Always** use environment variables (`VENICE_API_KEY`)
- 🔒 Keys are automatically redacted from all logs and output
- 🔄 Rotate keys regularly

### 🛡️ Network Security
- All requests use **HTTPS** with TLS 1.2+
- Automatic retry with exponential backoff
- Connection and read timeout protection
- Secure session management

### 🔍 Vulnerability Reporting
- See [SECURITY.md](SECURITY.md) for reporting guidelines
- Response within 48 hours
- Regular dependency updates via Dependabot

### ⚠️ Content Safety
This tool provides access to **uncensored image generation**. Users are responsible for:
- Complying with local laws and regulations
- Using the tool in appropriate contexts
- Understanding Venice AI's terms of service

## 🛠️ Architecture

### Component Overview

1. **QwenCLIIntegrator** (`qwen_cli_integrator.py`)
   - Main orchestrator class
   - Delegates commands to appropriate integration modules
   - Handles CLI argument parsing and command routing

2. **GitKrakenCLI** (`gitkraken_integration.py`)
   - Wraps GitKraken CLI (`gk`) commands
   - Provides Python API for all GitKraken features
   - Includes AI-powered Git workflows

3. **VeniceAIImageGenerator** (`venice_integration.py`)
   - Handles image generation and upscaling
   - Supports uncensored models
   - Automatic retry logic and error handling

4. **VeniceAIVerifier** (`venice_integration.py`)
   - API key verification
   - Model fetching and discovery

5. **VeniceAIConfigUpdater** (`venice_integration.py`)
   - Auto-generates Raycast configuration
   - Keeps model lists up-to-date

6. **ExternalAPIIntegrator** (`external_api_integrator.py`)
   - Generic external AI provider support
   - Reads Raycast-format configuration files
   - Extensible for multiple providers

### Data Flow

```
User Command → qwen_cli_integrator.py → Specific Integration Module → External API/CLI
                                      ↓
                               Response Processing & Redaction
                                      ↓
                               Return to User (Secure)
```

## 🤝 Contributing

We welcome contributions from the community! 🎉

### Quick Contribution Guide

1. 🍴 **Fork the Repository**
2. 🌱 **Create a Feature Branch**: `git checkout -b feature/amazing-feature`
3. ✨ **Make Your Changes**:
   - Write tests for new functionality
   - Follow PEP 8 and project coding standards
   - Add docstrings to all functions
   - Ensure all tests pass: `pytest tests/`
4. 📝 **Commit**: Use [conventional commits](https://www.conventionalcommits.org/)
   ```bash
   git commit -m "feat: add new image generation parameter"
   git commit -m "fix: resolve API timeout issue"
   git commit -m "docs: update installation instructions"
   ```
5. 🚀 **Push**: `git push origin feature/amazing-feature`
6. 🎯 **Open a Pull Request**

### Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/FayeBlade-Qwen-CLI-Patch.git
cd FayeBlade-Qwen-CLI-Patch

# Install dev dependencies
pip install -r requirements.txt
pip install pytest flake8 black isort

# Run tests
pytest tests/ -v

# Format code
black --line-length 120 .
isort --profile black .
```

### Reporting Issues

Found a bug? 🐞
- Use [GitHub Issues](https://github.com/Fayeblade1488/FayeBlade-Qwen-CLI-Patch/issues)
- Use issue templates provided
- Include: OS, Python version, steps to reproduce, error messages
- Redact any sensitive information (API keys, personal data)

### Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## ❓ FAQ

<details>
<summary><b>Do I need Raycast installed to use this?</b></summary>
No! While the system can read Raycast configuration format, Raycast is completely optional.
</details>

<details>
<summary><b>Is my API key safe?</b></summary>
Yes. API keys are:
<ul>
<li>Never logged or printed</li>
<li>Never stored in configuration files</li>
<li>Only loaded from environment variables</li>
<li>Automatically redacted from all output</li>
</ul>
</details>

<details>
<summary><b>What models support uncensored generation?</b></summary>
The default model is <code>lustify-sdxl</code>. Use <code>python qwen_cli_integrator.py venice list-models</code> to see all available models.
</details>

<details>
<summary><b>Can I use this with other AI providers?</b></summary>
Yes! The <code>ExternalAPIIntegrator</code> supports any OpenAI-compatible API. Add your provider configuration in Raycast format.
</details>

<details>
<summary><b>How do I troubleshoot installation issues?</b></summary>
See the <a href="QUICKSTART_GUIDE.md">Quick Start Guide</a> for detailed troubleshooting steps.
</details>

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### What this means:
✅ Commercial use  
✅ Modification  
✅ Distribution  
✅ Private use  
⚠️ No liability  
⚠️ No warranty  

## 🚀 Roadmap

- [ ] Add support for more Venice AI models
- [ ] Implement batch image generation
- [ ] Add video generation capabilities
- [ ] Create web UI interface
- [ ] Docker container support
- [ ] CI/CD pipeline enhancements

## 👏 Acknowledgments

- [GitKraken](https://www.gitkraken.com/) for their excellent CLI tool
- [Venice AI](https://venice.ai/) for uncensored AI capabilities
- All [contributors](https://github.com/Fayeblade1488/FayeBlade-Qwen-CLI-Patch/graphs/contributors)

## 📞 Support

- 🐞 **Bug Reports**: [GitHub Issues](https://github.com/Fayeblade1488/FayeBlade-Qwen-CLI-Patch/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Fayeblade1488/FayeBlade-Qwen-CLI-Patch/discussions)
- 📧 **Security**: See [SECURITY.md](SECURITY.md)

---

<div align="center">

**[⬆ Back to Top](#-qwen-cli-integration-gitkraken--venice-ai-)**

Made with ❤️ by [Faye Blade](https://github.com/Fayeblade1488)

</div>
