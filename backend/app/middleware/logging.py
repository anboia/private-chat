import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        # Log request
        await logger.ainfo(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            client_ip=request.client.host if request.client else None,
        )
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # Log response
        await logger.ainfo(
            "Request completed",
            request_id=request_id,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
            response_headers=dict(response.headers),
        )
        
        return response