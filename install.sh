#!/bin/bash

# Qwen CLI Integration Installation Script
# This script automates the setup of the Qwen CLI integration

set -e  # Exit immediately if a command exits with a non-zero status

# Colors for output formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Qwen CLI Integration Setup${NC}"
echo "=========================="

# Check if Python 3.7+ is installed
echo -e "${BLUE}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Found Python version: $PYTHON_VERSION"

# Check if Python version is 3.7 or higher
if [[ $(printf '%s\n' "3.7" "$PYTHON_VERSION" | sort -V | head -n1) == "3.7" ]] || [[ "$PYTHON_VERSION" == "3.7" ]]; then
    echo -e "${GREEN}✓ Python version requirement satisfied${NC}"
else
    echo -e "${RED}Error: Python 3.7 or higher is required.${NC}"
    exit 1
fi

# Check if GitKraken CLI is installed
echo -e "${BLUE}Checking GitKraken CLI installation...${NC}"
if command -v gk &> /dev/null; then
    GK_VERSION=$(gk --version 2>&1 | head -n1)
    echo -e "${GREEN}✓ GitKraken CLI found: $GK_VERSION${NC}"
else
    echo -e "${YELLOW}⚠ GitKraken CLI not found. Please install from https://www.gitkraken.com/cli${NC}"
fi

# Check if pip is available
echo -e "${BLUE}Checking pip availability...${NC}"
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓ pip found${NC}"
else
    echo -e "${YELLOW}⚠ pip not found. Attempting to install...${NC}"
    python3 -m ensurepip --upgrade
fi

# Install dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}Error: requirements.txt not found${NC}"
    exit 1
fi

# Check for Venice API key
echo -e "${BLUE}Checking Venice API key...${NC}"
if [ -z "$VENICE_API_KEY" ]; then
    echo -e "${YELLOW}⚠ Venice API key not set. Set the VENICE_API_KEY environment variable to use Venice AI features.${NC}"
    echo "Example: export VENICE_API_KEY='your_api_key_here'"
else
    echo -e "${GREEN}✓ Venice API key is set${NC}"
fi

# Run the test suite
echo -e "${BLUE}Running test suite...${NC}"
python3 -m pytest tests/ -q

echo
echo -e "${GREEN}Setup completed successfully!${NC}"
echo
echo -e "${BLUE}Usage Examples:${NC}"
echo "1. GitKraken: python qwen_cli_integrator.py gitkraken ai_commit"
echo "2. Venice: python qwen_cli_integrator.py venice generate --prompt 'fantasy landscape'"
echo "3. Help: python qwen_cli_integrator.py --help"
echo
echo -e "${BLUE}For more information, see README.md${NC}"