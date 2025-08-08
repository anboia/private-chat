# OpenAI Proxy Server

A FastAPI-based proxy server that mirrors the OpenAI API interface, acting as a transparent intermediary between clients and OpenAI.

## Features

- **Complete API Compatibility**: Mirrors OpenAI API v1 endpoints
- **Multi-tenant Authentication**: Map client keys to OpenAI keys
- **Rate Limiting**: Per-API-key request and token limits
- **Redis Caching**: Cache embeddings and deterministic responses
- **Streaming Support**: Full SSE streaming for chat completions
- **Comprehensive Monitoring**: Prometheus metrics and structured logging
- **Error Handling**: Exponential backoff with OpenAI-compatible error formatting

## Supported Endpoints

- `/v1/chat/completions` (streaming + non-streaming)
- `/v1/completions`
- `/v1/embeddings`
- `/v1/models`
- `/health` (health check)
- `/metrics` (Prometheus metrics)

## Prerequisites

- Python 3.11 or higher
- Redis server (for caching)

## Installation & Setup

### 1. Install Python Dependencies

**Option A: Using pip (default):**
```bash
pip install -r requirements.txt
```

**Option B: Using conda (recommended for Windows):**
```bash
# Create and activate conda environment
conda env create -f environment.yml
conda activate openai-proxy

# Or create manually
conda create -n openai-proxy python=3.11
conda activate openai-proxy
conda install -c conda-forge fastapi uvicorn httpx redis-py pydantic structlog prometheus_client python-dotenv
pip install pydantic-settings slowapi aioredis
```

### 2. Install and Start Redis

**Windows (using Chocolatey):**
```bash
choco install redis-64
redis-server
```

**Windows (using WSL/Ubuntu):**
```bash
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
# Required: Your OpenAI API key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: Client API keys (comma-separated)
CLIENT_API_KEYS=client-key-1,client-key-2,client-key-3

# Optional: Map client keys to specific OpenAI keys
# API_KEY_MAPPING={"client-key-1": "sk-openai-key-1", "client-key-2": "sk-openai-key-2"}

# Redis connection (default works for local Redis)
CACHE__REDIS_URL=redis://localhost:6379

# Rate limiting (optional)
RATE_LIMIT__REQUESTS_PER_MINUTE=60
RATE_LIMIT__TOKENS_PER_MINUTE=100000
```

### 4. Start the Server

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the convenience script
python -m app.main
```

The proxy will be available at `http://localhost:8000`

## Quick Start Script

For convenience, you can use the startup script:

```bash
# Make script executable (Linux/macOS)
chmod +x start.sh

# Run the script
./start.sh

# On Windows
start.bat
```

## Verification

1. **Check Redis Connection:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

2. **Test Health Endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Test API (replace with your client key):**
   ```bash
   curl -X POST "http://localhost:8000/v1/chat/completions" \
     -H "Authorization: Bearer your-client-key" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [{"role": "user", "content": "Hello!"}]
     }'
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Default OpenAI API key | **Required** |
| `CLIENT_API_KEYS` | Comma-separated client keys | "" |
| `API_KEY_MAPPING` | JSON mapping of client to OpenAI keys | "" |
| `CACHE__REDIS_URL` | Redis connection URL | redis://localhost:6379 |
| `RATE_LIMIT__REQUESTS_PER_MINUTE` | Request rate limit per key | 60 |
| `RATE_LIMIT__TOKENS_PER_MINUTE` | Token rate limit per key | 100000 |
| `LOG_LEVEL` | Logging level | INFO |

### API Key Mapping

Map different client keys to different OpenAI keys:

```bash
API_KEY_MAPPING='{"client-key-1": "sk-openai-key-1", "client-key-2": "sk-openai-key-2"}'
```

If no mapping is provided, all client keys use the default `OPENAI_API_KEY`.

## Usage

### Python Client

```python
import openai

# Configure to use your proxy
openai.api_base = "http://localhost:8000/v1"
openai.api_key = "your-client-key"

# Use exactly like OpenAI API
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Streaming Example

```python
for chunk in openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
):
    content = chunk.choices[0].delta.get("content", "")
    if content:
        print(content, end="", flush=True)
```

### Using with Modern OpenAI Library

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-client-key",
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
    "status": "healthy",
    "redis_connected": true
}
```

### Prometheus Metrics
Available at `http://localhost:8000/metrics`:

- Request counts and durations by endpoint
- Token usage tracking
- Cache hit/miss rates
- Rate limiting events
- OpenAI API errors

### Logs
Structured JSON logs include:
- Request/response details
- Token usage
- Latency measurements
- Error information
- Cache operations

## Rate Limiting

Token bucket implementation per API key:
- **Request Limits**: 60 requests/minute (default)
- **Token Limits**: 100,000 tokens/minute (default)

Rate limit exceeded responses return HTTP 429 with `Retry-After` header.

## Caching

Redis caching strategy:
- **Embeddings**: Always cached (deterministic)
- **Chat/Completions**: Cached when temperature=0 and seed provided
- **Models**: Cached for 5 minutes

## Error Handling

- **Exponential Backoff**: Up to 3 retry attempts
- **OpenAI Compatible**: All errors match OpenAI API format
- **Proper Status Codes**: HTTP codes match OpenAI conventions

## Troubleshooting

### Redis Connection Issues
```bash
# Check if Redis is running
redis-cli ping

# Start Redis (varies by OS)
redis-server

# Check Redis logs
redis-cli monitor
```

### Common Issues

1. **"Redis connection failed"**: Make sure Redis is installed and running on port 6379
2. **"Invalid API key"**: Check your `OPENAI_API_KEY` in `.env`
3. **Rate limiting**: Adjust limits in `.env` or wait for rate limit reset
4. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

### Windows-Specific Issues

#### Pydantic Build Errors
If you encounter `pydantic-core` build errors on Windows:

**Quick Fix (Recommended):**
```bash
# Use prebuilt wheels only
pip install --only-binary=pydantic-core --upgrade pip
pip install --only-binary=pydantic-core -r requirements.txt
```

**Alternative Solutions:**

1. **Use conda instead of pip:**
   ```bash
   conda install -c conda-forge fastapi uvicorn httpx redis-py pydantic structlog prometheus_client python-dotenv
   ```

2. **Install Microsoft Visual C++ Build Tools:**
   - Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Or install [Visual Studio Community](https://visualstudio.microsoft.com/vs/community/) with C++ development tools
   - Then retry: `pip install -r requirements.txt`

3. **Use Python from Microsoft Store:**
   - Install Python from Microsoft Store (often has better compatibility)
   - Create new virtual environment and retry installation

4. **Use WSL (Windows Subsystem for Linux):**
   ```bash
   # In WSL Ubuntu
   sudo apt update
   sudo apt install python3 python3-pip python3-venv build-essential
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

#### Redis on Windows
**Option 1 - Redis for Windows:**
- Download from [Redis Windows releases](https://github.com/microsoftarchive/redis/releases)
- Or use chocolatey: `choco install redis-64`

**Option 2 - WSL Redis:**
```bash
# In WSL
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**Option 3 - Docker Desktop:**
```bash
# If you have Docker Desktop
docker run -d -p 6379:6379 redis:alpine
```

## Development

### Project Structure
```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration and settings
├── models/              # Pydantic request/response schemas
├── routers/             # API endpoint handlers
├── middleware/          # Auth, rate limiting, logging
├── services/            # OpenAI client, cache, metrics
└── utils/               # Utilities and helpers
```

### Running in Development Mode
```bash
# With auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# With debug logging
DEBUG=true uvicorn app.main:app --reload
```

### Testing
```bash
# Install dev dependencies
pip install pytest httpx pytest-asyncio

# Run tests
pytest
```

## Security Notes

- Bearer token authentication required for all API endpoints
- API keys are never logged or exposed
- Multi-tenant isolation per client key
- Rate limiting prevents abuse
- Input validation on all requests

## License

MIT License