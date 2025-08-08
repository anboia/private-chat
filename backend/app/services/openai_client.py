import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional
import httpx
import structlog
from fastapi import HTTPException

from app.config import settings
from app.models.errors import ErrorResponse

logger = structlog.get_logger()


class OpenAIClient:
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None

    async def initialize(self):
        timeout = httpx.Timeout(60.0, connect=10.0)
        self.client = httpx.AsyncClient(
            timeout=timeout,
            limits=httpx.Limits(max_keepalive_connections=100, max_connections=200)
        )

    async def close(self):
        if self.client:
            await self.client.aclose()

    def _make_request_with_retry(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        json_data: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ):
        if stream:
            return self.client.stream(method, url, headers=headers, json=json_data)
        else:
            return self._make_regular_request_with_retry(method, url, headers, json_data)
    
    async def _make_regular_request_with_retry(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        json_data: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        last_exception = None
        
        for attempt in range(settings.retry_max_attempts):
            try:
                response = await self.client.request(
                    method, url, headers=headers, json=json_data
                )
                response.raise_for_status()
                return response
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code in [429, 500, 502, 503, 504] and attempt < settings.retry_max_attempts - 1:
                    wait_time = (settings.retry_backoff_factor ** attempt)
                    await logger.awarning(
                        "Request failed, retrying",
                        attempt=attempt + 1,
                        status_code=e.response.status_code,
                        wait_time=wait_time
                    )
                    await asyncio.sleep(wait_time)
                    last_exception = e
                    continue
                else:
                    await self._handle_openai_error(e.response, is_streaming=False)
            except (httpx.RequestError, httpx.TimeoutException) as e:
                if attempt < settings.retry_max_attempts - 1:
                    wait_time = (settings.retry_backoff_factor ** attempt)
                    await logger.awarning(
                        "Request error, retrying",
                        attempt=attempt + 1,
                        error=str(e),
                        wait_time=wait_time
                    )
                    await asyncio.sleep(wait_time)
                    last_exception = e
                    continue
                else:
                    raise HTTPException(
                        status_code=502,
                        detail=ErrorResponse.create(
                            message=f"Failed to connect to OpenAI: {str(e)}",
                            error_type="service_unavailable"
                        ).model_dump()
                    )
        
        if last_exception:
            raise last_exception

    async def _handle_openai_error(self, response: httpx.Response, is_streaming: bool = False):
        try:
            if is_streaming:
                # For streaming responses, we need to read the content first
                content = await response.aread()
                error_data = json.loads(content)
            else:
                error_data = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=error_data
            )
        except (json.JSONDecodeError, KeyError):
            raise HTTPException(
                status_code=response.status_code,
                detail=ErrorResponse.create(
                    message=f"OpenAI API error: {response.status_code}",
                    error_type="api_error"
                ).model_dump()
            )

    async def chat_completions(
        self,
        openai_key: str,
        request_data: Dict[str, Any],
        stream: bool = False
    ) -> AsyncGenerator[str, None]:
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{settings.openai_api_base}/chat/completions"
        
        if stream:
            async with self._make_request_with_retry(
                "POST", url, headers, request_data, stream=True
            ) as response:
                if response.status_code != 200:
                    # For streaming errors, we need to yield an error event
                    content = await response.aread()
                    try:
                        error_data = json.loads(content)
                        error_message = error_data.get('error', {}).get('message', 'Unknown error')
                    except (json.JSONDecodeError, KeyError):
                        error_message = f"OpenAI API error: {response.status_code}"
                    
                    yield f"data: {json.dumps({'error': error_message})}\n\n"
                    return
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data.strip() == "[DONE]":
                            break
                        yield f"data: {data}\n\n"
        else:
            response = await self._make_regular_request_with_retry(
                "POST", url, headers, request_data
            )
            yield response.text

    async def completions(
        self,
        openai_key: str,
        request_data: Dict[str, Any]
    ) -> str:
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{settings.openai_api_base}/completions"
        response = await self._make_regular_request_with_retry(
            "POST", url, headers, request_data
        )
        return response.text

    async def embeddings(
        self,
        openai_key: str,
        request_data: Dict[str, Any]
    ) -> str:
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{settings.openai_api_base}/embeddings"
        response = await self._make_regular_request_with_retry(
            "POST", url, headers, request_data
        )
        return response.text

    async def models(self, openai_key: str) -> str:
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{settings.openai_api_base}/models"
        response = await self._make_regular_request_with_retry(
            "GET", url, headers
        )
        return response.text


openai_client = OpenAIClient()