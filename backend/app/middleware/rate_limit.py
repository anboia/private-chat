import time
from typing import Dict, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.models.errors import ErrorResponse


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def consume(self, tokens: int) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def time_until_available(self, tokens: int) -> float:
        if self.tokens >= tokens:
            return 0.0
        needed_tokens = tokens - self.tokens
        return needed_tokens / self.refill_rate


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.request_buckets: Dict[str, TokenBucket] = {}
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.excluded_paths = {"/health", "/metrics", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        client_key = getattr(request.state, 'client_key', None)
        if not client_key:
            return await call_next(request)

        # Check request rate limit
        if not self._check_request_limit(client_key):
            return self._rate_limit_response("Request rate limit exceeded")

        # Estimate token usage for token rate limiting
        # This is a rough estimate - actual usage will be tracked after the request
        estimated_tokens = self._estimate_tokens(request)
        if not self._check_token_limit(client_key, estimated_tokens):
            return self._rate_limit_response("Token rate limit exceeded")

        response = await call_next(request)
        return response

    def _check_request_limit(self, client_key: str) -> bool:
        if client_key not in self.request_buckets:
            # requests per minute / 60 = requests per second
            rate = settings.rate_limit.requests_per_minute / 60.0
            self.request_buckets[client_key] = TokenBucket(
                capacity=settings.rate_limit.requests_per_minute,
                refill_rate=rate
            )
        
        return self.request_buckets[client_key].consume(1)

    def _check_token_limit(self, client_key: str, tokens: int) -> bool:
        if client_key not in self.token_buckets:
            # tokens per minute / 60 = tokens per second
            rate = settings.rate_limit.tokens_per_minute / 60.0
            self.token_buckets[client_key] = TokenBucket(
                capacity=settings.rate_limit.tokens_per_minute,
                refill_rate=rate
            )
        
        return self.token_buckets[client_key].consume(tokens)

    def _estimate_tokens(self, request: Request) -> int:
        # Rough estimation based on request body size
        # In a real implementation, you might parse the request to get a better estimate
        body_size = int(request.headers.get("content-length", "0"))
        # Rough approximation: 1 token per 4 characters
        return max(100, body_size // 4)

    def _rate_limit_response(self, message: str) -> Response:
        error_response = ErrorResponse.create(
            message=message,
            error_type="rate_limit_exceeded",
            code="rate_limit_exceeded"
        )
        return Response(
            content=error_response.model_dump_json(),
            status_code=429,
            headers={
                "content-type": "application/json",
                "retry-after": "60"
            }
        )