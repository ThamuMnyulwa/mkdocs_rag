#!/bin/bash

# Setup script for MkDocs RAG Demo
# This script sets up both frontend and backend

set -e

echo "🚀 MkDocs RAG Demo - Setup Script"
echo "=================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_MAJOR=3
REQUIRED_MINOR=12

MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt "$REQUIRED_MAJOR" ] || ([ "$MAJOR" -eq "$REQUIRED_MAJOR" ] && [ "$MINOR" -lt "$REQUIRED_MINOR" ]); then
    echo "❌ Python 3.12+ is required. You have Python $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version check passed: $PYTHON_VERSION"
echo ""

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY environment variable not set"
    echo ""
    echo "To get a Gemini API key:"
    echo "1. Visit https://ai.google.dev/"
    echo "2. Click 'Get API key'"
    echo "3. Copy your key"
    echo ""
    read -p "Enter your Gemini API key: " api_key
    export GOOGLE_API_KEY=$api_key
else
    echo "✅ GOOGLE_API_KEY is set"
fi

echo ""
echo "📦 Installing backend dependencies..."
cd backend

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   Or visit: https://docs.astral.sh/uv/"
    exit 1
fi

uv sync > /dev/null 2>&1
echo "✅ Backend dependencies installed"

# Create .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "GOOGLE_API_KEY=$GOOGLE_API_KEY" >> .env
    echo "✅ Created backend/.env file"
else
    echo "✅ backend/.env already exists"
fi

echo ""
echo "📦 Installing frontend dependencies..."
cd ../frontend
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Frontend dependencies installed"

echo ""
echo "🔍 Indexing documentation..."
cd ../backend
uv run python -m scripts.index_docs

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the demo:"
echo ""
echo "Option 1: Run both services automatically"
echo "  ./run.sh"
echo ""
echo "Option 2: Run manually in separate terminals"
echo "  Terminal 1 (Backend):"
echo "    cd backend"
echo "    uv run uvicorn main:app --reload"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend"
echo "    mkdocs serve"
echo ""
echo "Then open http://localhost:8000 in your browser"
echo ""

