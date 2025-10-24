#!/bin/bash
# Development helper script for Stella Agent

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🤖 Stella Agent - Development Setup${NC}"
echo "===================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip -q
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo -e "${YELLOW}Installing dependencies...${NC}"
echo "This may take a few minutes..."
pip install -r requirements.txt -q
echo "✓ Production dependencies installed"

# Ask if user wants dev dependencies
read -p "Install development dependencies? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install -r requirements-dev.txt -q
    echo "✓ Development dependencies installed"
    
    # Setup pre-commit hooks
    read -p "Setup pre-commit hooks? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pre-commit install
        echo "✓ Pre-commit hooks installed"
    fi
fi

# Check for .env file
echo ""
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    read -p "Create .env from template? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✓ .env file created from template"
        echo -e "${YELLOW}⚠️  Please edit .env with your credentials${NC}"
    fi
else
    echo "✓ .env file exists"
fi

# Done
echo ""
echo -e "${GREEN}✨ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys and credentials"
echo "2. Run 'python main.py' to start the server"
echo "3. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "Useful commands:"
echo "  make run          - Start the server"
echo "  make test         - Run tests"
echo "  make lint         - Check code quality"
echo "  make format       - Format code"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
