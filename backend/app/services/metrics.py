import time
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import structlog

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'openai_proxy_requests_total',
    'Total number of requests',
    ['endpoint', 'method', 'status_code', 'client_key']
)

REQUEST_DURATION = Histogram(
    'openai_proxy_request_duration_seconds',
    'Request duration in seconds',
    ['endpoint', 'method', 'client_key']
)

TOKEN_USAGE = Counter(
    'openai_proxy_tokens_total',
    'Total number of tokens processed',
    ['endpoint', 'client_key', 'type']  # type: prompt, completion, total
)

CACHE_OPERATIONS = Counter(
    'openai_proxy_cache_operations_total',
    'Total number of cache operations',
    ['operation', 'result']  # operation: get, set; result: hit, miss, error
)

ACTIVE_REQUESTS = Gauge(
    'openai_proxy_active_requests',
    'Number of active requests',
    ['endpoint', 'client_key']
)

OPENAI_API_ERRORS = Counter(
    'openai_proxy_openai_errors_total',
    'Total number of OpenAI API errors',
    ['error_type', 'status_code']
)


class MetricsService:
    def __init__(self):
        self.metrics_server_started = False

    async def initialize(self):
        """Initialize the metrics service and start Prometheus metrics server"""
        if not self.metrics_server_started:
            try:
                # Start Prometheus metrics server on port 9090
                start_http_server(9090)
                self.metrics_server_started = True
                await logger.ainfo("Prometheus metrics server started on port 9090")
            except Exception as e:
                await logger.aerror("Failed to start metrics server", error=str(e))

    async def close(self):
        """Cleanup metrics service"""
        pass

    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration: float,
        client_key: str
    ):
        """Record a completed request"""
        REQUEST_COUNT.labels(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            client_key=client_key
        ).inc()
        
        REQUEST_DURATION.labels(
            endpoint=endpoint,
            method=method,
            client_key=client_key
        ).observe(duration)

    def record_token_usage(
        self,
        endpoint: str,
        client_key: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0
    ):
        """Record token usage"""
        if prompt_tokens > 0:
            TOKEN_USAGE.labels(
                endpoint=endpoint,
                client_key=client_key,
                type='prompt'
            ).inc(prompt_tokens)
        
        if completion_tokens > 0:
            TOKEN_USAGE.labels(
                endpoint=endpoint,
                client_key=client_key,
                type='completion'
            ).inc(completion_tokens)
        
        if total_tokens > 0:
            TOKEN_USAGE.labels(
                endpoint=endpoint,
                client_key=client_key,
                type='total'
            ).inc(total_tokens)

    def record_cache_operation(self, operation: str, result: str):
        """Record cache operations"""
        CACHE_OPERATIONS.labels(
            operation=operation,
            result=result
        ).inc()

    def record_active_request_start(self, endpoint: str, client_key: str):
        """Record the start of an active request"""
        ACTIVE_REQUESTS.labels(
            endpoint=endpoint,
            client_key=client_key
        ).inc()

    def record_active_request_end(self, endpoint: str, client_key: str):
        """Record the end of an active request"""
        ACTIVE_REQUESTS.labels(
            endpoint=endpoint,
            client_key=client_key
        ).dec()

    def record_openai_error(self, error_type: str, status_code: int):
        """Record OpenAI API errors"""
        OPENAI_API_ERRORS.labels(
            error_type=error_type,
            status_code=status_code
        ).inc()

    async def extract_token_usage(self, response_text: str) -> Dict[str, int]:
        """Extract token usage from OpenAI response"""
        try:
            import json
            response_data = json.loads(response_text)
            usage = response_data.get('usage', {})
            return {
                'prompt_tokens': usage.get('prompt_tokens', 0),
                'completion_tokens': usage.get('completion_tokens', 0),
                'total_tokens': usage.get('total_tokens', 0)
            }
        except (json.JSONDecodeError, KeyError):
            return {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}


class RequestMetricsContext:
    """Context manager for tracking request metrics"""
    
    def __init__(self, metrics_service: MetricsService, endpoint: str, method: str, client_key: str):
        self.metrics_service = metrics_service
        self.endpoint = endpoint
        self.method = method
        self.client_key = client_key
        self.start_time = None
        self.status_code = None

    async def __aenter__(self):
        self.start_time = time.time()
        self.metrics_service.record_active_request_start(self.endpoint, self.client_key)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics_service.record_request(
                self.endpoint,
                self.method,
                self.status_code or 500,
                duration,
                self.client_key
            )
        
        self.metrics_service.record_active_request_end(self.endpoint, self.client_key)

    def set_status_code(self, status_code: int):
        self.status_code = status_code


metrics_service = MetricsService()