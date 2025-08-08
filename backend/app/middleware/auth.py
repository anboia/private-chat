from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_valid_client_keys, get_openai_key_for_client
from app.models.errors import ErrorResponse


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.security = HTTPBearer(auto_error=False)
        self.excluded_paths = {"/health", "/metrics", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        # Allow OPTIONS requests (CORS preflight) without authentication
        if request.method == "OPTIONS":
            return await call_next(request)
            
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return self._unauthorized_response("Missing or invalid authorization header")

        token = auth_header[7:]  # Remove "Bearer " prefix
        
        valid_keys = get_valid_client_keys()
        if valid_keys and token not in valid_keys:
            return self._unauthorized_response("Invalid API key")

        openai_key = get_openai_key_for_client(token)
        if not openai_key:
            return self._unauthorized_response("Unable to map client key to OpenAI key")

        request.state.client_key = token
        request.state.openai_key = openai_key
        
        return await call_next(request)

    def _unauthorized_response(self, message: str) -> Response:
        error_response = ErrorResponse.create(
            message=message,
            error_type="authentication_error",
            code="invalid_api_key"
        )
        return Response(
            content=error_response.model_dump_json(),
            status_code=401,
            headers={"content-type": "application/json"}
        )