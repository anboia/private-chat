# Grafana Setup for OpenAI Proxy Monitoring

## Installation

### Option 1: Using Docker (Recommended)
```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  grafana/grafana-oss
```

### Option 2: Local Installation

#### macOS (using Homebrew)
```bash
brew install grafana
brew services start grafana
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install -y adduser libfontconfig1
wget https://dl.grafana.com/oss/release/grafana_10.1.5_amd64.deb
sudo dpkg -i grafana_10.1.5_amd64.deb
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

#### Manual Download
```bash
wget https://dl.grafana.com/oss/release/grafana-10.1.5.linux-amd64.tar.gz
tar -zxvf grafana-10.1.5.linux-amd64.tar.gz
cd grafana-10.1.5
./bin/grafana-server
```

## Access

- **Grafana Web UI**: http://localhost:3000
- **Default credentials**: admin/admin (change on first login)

## Configuration Steps

### Option A: Manual Configuration

#### 1. Add Prometheus Data Source
1. Login to Grafana (http://localhost:3000)
2. Go to **Configuration** → **Data Sources**
3. Click **Add data source**
4. Select **Prometheus**
5. Set URL to: `http://localhost:9091`
6. Click **Save & Test**

#### 2. Import Dashboard
1. Go to **Dashboards** → **Import**
2. Upload the `grafana-dashboard.json` file
3. Select the Prometheus data source
4. Click **Import**

### Option B: Automated Configuration

#### 1. Auto-provision Data Source
Place the `grafana-datasource.json` file in Grafana's provisioning directory:
```bash
# For Docker
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -v $(pwd)/grafana-datasource.json:/etc/grafana/provisioning/datasources/prometheus.json \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  grafana/grafana-oss

# For local installation
sudo cp grafana-datasource.json /etc/grafana/provisioning/datasources/prometheus.json
sudo systemctl restart grafana-server
```

## Dashboard Features

The dashboard includes 12 panels monitoring:

### Performance Metrics
- **Request Rate**: Real-time requests per second
- **Response Time**: Average response time and percentiles
- **Active Requests**: Current number of processing requests
- **Error Rate**: Errors per second with color-coded thresholds

### Business Metrics  
- **Token Usage**: Prompt, completion, and total token consumption rates
- **Cache Performance**: Hit/miss rates and overall hit ratio
- **OpenAI API Errors**: Error types and frequencies
- **Client Distribution**: Top clients by request volume

### Operational Insights
- **Status Code Distribution**: HTTP response codes breakdown
- **Request Volume by Endpoint**: Traffic distribution across API endpoints
- **Cache Hit Ratio**: Performance indicator with threshold colors

## Dashboard Customization

### Adding New Panels
1. Click **Add panel**
2. Use PromQL queries based on available metrics:
   ```promql
   # Custom examples
   rate(openai_proxy_requests_total{endpoint="chat/completions"}[5m])
   sum(openai_proxy_tokens_total) by (client_key)
   histogram_quantile(0.95, rate(openai_proxy_request_duration_seconds_bucket[5m]))
   ```

### Time Ranges
- Default: Last 1 hour
- Auto-refresh: Every 10 seconds
- Customizable via top-right controls

## Next Steps

1. Start Prometheus: Follow `PROMETHEUS_SETUP.md`
2. Start Grafana using one of the methods above
3. Configure the data source as described
4. Import the dashboard for instant visualization