# Prometheus Setup for OpenAI Proxy

## Installation

### Option 1: Using Docker (Recommended)
```bash
docker run -d \
  --name prometheus \
  -p 9091:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### Option 2: Local Installation

#### macOS (using Homebrew)
```bash
brew install prometheus
prometheus --config.file=prometheus.yml --web.listen-address=:9091
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install prometheus
sudo systemctl stop prometheus
prometheus --config.file=prometheus.yml --web.listen-address=:9091
```

#### Manual Download
```bash
# Download latest release
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvf prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0.linux-amd64
./prometheus --config.file=../prometheus.yml --web.listen-address=:9091
```

## Configuration

The `prometheus.yml` file is already configured to scrape metrics from:
- **FastAPI endpoint**: `localhost:8000/metrics`
- **Prometheus metrics server**: `localhost:9090/metrics`

## Access

- **Prometheus Web UI**: http://localhost:9091
- **Query metrics**: Use PromQL in the web interface
- **Targets status**: http://localhost:9091/targets

## Example Queries

```promql
# Request rate per second
rate(openai_proxy_requests_total[5m])

# Average response time
rate(openai_proxy_request_duration_seconds_sum[5m]) / rate(openai_proxy_request_duration_seconds_count[5m])

# Cache hit ratio
rate(openai_proxy_cache_operations_total{result="hit"}[5m]) / rate(openai_proxy_cache_operations_total[5m])

# Active requests
openai_proxy_active_requests

# Token usage rate
rate(openai_proxy_tokens_total[5m])
```

## Next Steps

1. Start your OpenAI proxy server: `./start.sh`
2. Start Prometheus (using one of the methods above)
3. Visit http://localhost:9091 to explore metrics
4. For better visualization, consider setting up Grafana