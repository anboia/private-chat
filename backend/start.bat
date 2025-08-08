@echo off
REM OpenAI Proxy Server Startup Script for Windows

echo 🚀 Starting OpenAI Proxy Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import fastapi, uvicorn, httpx, redis, pydantic, structlog, prometheus_client" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing dependencies...
    echo 🔧 Using prebuilt wheels for Windows compatibility...
    pip install --only-binary=pydantic-core --upgrade pip
    pip install --only-binary=pydantic-core -r requirements.txt
    if errorlevel 1 (
        echo ❌ Installation failed. Trying alternative approach...
        pip install --upgrade pip setuptools wheel
        pip install -r requirements.txt
        if errorlevel 1 (
            echo ❌ Installation still failed. Please see troubleshooting section in README.md
            pause
            exit /b 1
        )
    )
    echo.
)

REM Check if .env file exists
if not exist .env (
    echo ⚠️  No .env file found. Creating from template...
    copy .env.example .env >nul
    echo 📝 Please edit .env with your OpenAI API key before continuing
    echo.
)

REM Check Redis connection
echo 🔍 Checking Redis connection...
where redis-cli >nul 2>&1
if not errorlevel 1 (
    redis-cli ping >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Redis is running
    ) else (
        echo ❌ Redis is not responding. Please start Redis server:
        echo    - Install Redis for Windows
        echo    - Or use WSL: sudo service redis-server start
        echo.
        echo 🚀 Starting anyway ^(caching will be disabled^)...
    )
) else (
    echo ⚠️  Redis CLI not found. Make sure Redis is installed and running
    echo 🚀 Starting anyway ^(caching will be disabled^)...
)

echo.
echo 🌟 Starting FastAPI server on http://localhost:8000
echo 📊 Metrics available at http://localhost:8000/metrics
echo ❤️  Health check at http://localhost:8000/health
echo.

REM Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause