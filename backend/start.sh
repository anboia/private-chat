#!/bin/bash

# OpenAI Proxy Server Startup Script

echo "🚀 Starting OpenAI Proxy Server..."
echo

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if requirements are installed
if ! python -c "import fastapi, uvicorn, httpx, redis, pydantic, structlog, prometheus_client" &> /dev/null; then
    echo "📦 Installing dependencies..."
    echo "🔧 Using prebuilt wheels when possible..."
    pip install --upgrade pip
    if ! pip install --only-binary=pydantic-core -r requirements.txt; then
        echo "❌ Installation with prebuilt wheels failed. Trying with compilation..."
        if ! pip install -r requirements.txt; then
            echo "❌ Installation failed. You may need to install build tools."
            echo "   On macOS: xcode-select --install"
            echo "   On Linux: sudo apt-get install build-essential"
            echo "   Please see troubleshooting section in README.md"
            exit 1
        fi
    fi
    echo
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env with your OpenAI API key before continuing"
    echo
fi

# Check Redis connection
echo "🔍 Checking Redis connection..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is running"
    else
        echo "❌ Redis is not responding. Please start Redis server:"
        echo "   - On macOS: brew services start redis"
        echo "   - On Linux: sudo systemctl start redis-server"
        echo "   - On Windows: redis-server"
        echo
        echo "🚀 Starting anyway (caching will be disabled)..."
    fi
else
    echo "⚠️  Redis CLI not found. Make sure Redis is installed and running"
    echo "🚀 Starting anyway (caching will be disabled)..."
fi

echo
echo "🌟 Starting FastAPI server on http://localhost:8000"
echo "📊 Metrics available at http://localhost:8000/metrics"
echo "❤️  Health check at http://localhost:8000/health"
echo

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload