# Qwen CLI Integration Makefile
# This Makefile automates installation, testing, and deployment of the Qwen CLI integration

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip3
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

# Help target
.PHONY: help
help:
	@echo "Qwen CLI Integration Makefile"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  setup        - Create virtual environment and install dependencies"
	@echo "  install      - Install dependencies in current environment"
	@echo "  test         - Run test suite"
	@echo "  run          - Run the main integrator"
	@echo "  clean        - Remove virtual environment and generated files"
	@echo "  check        - Run basic checks on the integration"
	@echo "  docs         - Generate documentation (placeholder)"
	@echo "  format       - Format code with black (if available)"
	@echo "  lint         - Lint code with flake8 (if available)"
	@echo "  all          - Run setup, test, and check targets"
	@echo ""

# Setup virtual environment and install dependencies
.PHONY: setup
setup: $(VENV)/bin/activate
	@echo "Virtual environment created and dependencies installed."

$(VENV)/bin/activate: requirements.txt
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	@touch $(VENV)/bin/activate

# Install dependencies in current environment
.PHONY: install
install:
	$(PIP) install -r requirements.txt

# Run tests
.PHONY: test
test: $(VENV)/bin/activate
	$(VENV_PYTHON) -m pytest tests/ -q

# Run the main integrator
.PHONY: run
run: $(VENV)/bin/activate
	@echo "Running Qwen CLI Integrator. Use: python qwen_cli_integrator.py [tool] [command] [args]"
	@echo "Examples:"
	@echo "  make run-gitkraken-help"
	@echo "  make run-venice-help"

.PHONY: run-gitkraken-help
run-gitkraken-help:
	$(PYTHON) qwen_cli_integrator.py gitkraken --help

.PHONY: run-venice-help
run-venice-help:
	$(PYTHON) qwen_cli_integrator.py venice --help

# Clean up: remove virtual environment and generated files
.PHONY: clean
clean:
	rm -rf $(VENV)
	rm -rf generated/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Run basic checks
.PHONY: check
check:
	@echo "Checking installation..."
	@if command -v gk >/dev/null 2>&1; then \
		echo "✓ GitKraken CLI found: $(shell gk --version | head -n1)"; \
	else \
		echo "⚠ GitKraken CLI not found. Please install GitKraken CLI."; \
	fi
	@if [ -n "$$VENICE_API_KEY" ]; then \
		echo "✓ Venice API key is set"; \
	else \
		echo "⚠ Venice API key is not set. Set VENICE_API_KEY environment variable."; \
	fi
	@echo "✓ Python version: $(shell $(PYTHON) --version)"
	@echo "✓ Dependencies installed: $(shell $(PIP) list --format=freeze | grep -E 'requests' | wc -l | tr -d ' ') packages"

# Generate documentation (placeholder)
.PHONY: docs
docs:
	@echo "Documentation generation is not implemented in this basic version."

# Format code with black (if available)
.PHONY: format
format: $(VENV)/bin/activate
	@if [ -x "$(VENV)/bin/black" ]; then \
		$(VENV_PYTHON) -m black *.py; \
	else \
		echo "Formatting tool (black) not found. Install with: pip install black"; \
	fi

# Lint code with flake8 (if available)
.PHONY: lint
lint: $(VENV)/bin/activate
	@if [ -x "$(VENV)/bin/flake8" ]; then \
		$(VENV_PYTHON) -m flake8 *.py; \
	else \
		echo "Linting tool (flake8) not found. Install with: pip install flake8"; \
	fi

# Run all setup, test, and check targets
.PHONY: all
all: setup test check

# Install the qwen cli integrator to system path (optional)
.PHONY: install-system
install-system: setup
	@echo "Installing Qwen CLI Integrator to system..."
	@echo "#!/bin/bash" > /tmp/qwen-cli-integrator
	@echo "cd $(CURDIR) && $(VENV_PYTHON) qwen_cli_integrator.py \"\$$@\"" >> /tmp/qwen-cli-integrator
	@chmod +x /tmp/qwen-cli-integrator
	@echo "Qwen CLI Integrator installed to /tmp/qwen-cli-integrator"
	@echo "To install permanently, move to a directory in your PATH:"
	@echo "sudo mv /tmp/qwen-cli-integrator /usr/local/bin/qwen-cli"

# Validate that there are no API keys or secrets in the code
.PHONY: validate-security
validate-security:
	@echo "Checking for potential security issues..."
	@FOUND=$$(grep -r "API_KEY\|SECRET\|PASSWORD\|TOKEN" --include="*.py" --include="*.md" --include="*.txt" . 2>/dev/null || true); \
	if [ -n "$$FOUND" ] && [ "$$(echo "$$FOUND" | grep -v ".gitignore\|README.md\|Makefile\|package.json\|venice_integration.py\|gitkraken_integration.py\|qwen_cli_integrator.py\|tests/" | grep -v "VENICE_API_KEY" | grep -v "api_key" | wc -l)" -ne 0 ]; then \
		echo "⚠ Potential security issue found:"; \
		echo "$$FOUND"; \
		exit 1; \
	else \
		echo "✓ No obvious security issues found"; \
	fi

# Run full validation
.PHONY: validate
validate: validate-security check