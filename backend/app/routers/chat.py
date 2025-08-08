from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import status
import json

from app.models.chat import ChatCompletionRequest
from app.services.openai_client import openai_client
from app.services.cache import cache_service
from app.services.metrics import metrics_service, RequestMetricsContext
from app.utils.streaming import create_sse_response

router = APIRouter()


@router.post("/chat/completions")
async def chat_completions(request: Request, chat_request: ChatCompletionRequest):
    client_key = request.state.client_key
    openai_key = request.state.openai_key
    
    async with RequestMetricsContext(
        metrics_service, "chat/completions", "POST", client_key
    ) as metrics_ctx:
        
        try:
            request_data = chat_request.model_dump(exclude_unset=True)
            
            # Check cache for non-streaming requests
            if not chat_request.stream and cache_service.should_cache_request("chat", request_data):
                cached_response = await cache_service.get("chat", request_data)
                if cached_response:
                    metrics_service.record_cache_operation("get", "hit")
                    metrics_ctx.set_status_code(200)
                    
                    # Extract and record token usage from cached response
                    token_usage = await metrics_service.extract_token_usage(cached_response)
                    metrics_service.record_token_usage(
                        "chat/completions", 
                        client_key,
                        **token_usage
                    )
                    
                    return JSONResponse(
                        content=json.loads(cached_response),
                        status_code=200
                    )
                else:
                    metrics_service.record_cache_operation("get", "miss")
            
            # Make request to OpenAI
            if chat_request.stream:
                async def stream_generator():
                    async for chunk in openai_client.chat_completions(
                        openai_key, request_data, stream=True
                    ):
                        yield chunk
                
                metrics_ctx.set_status_code(200)
                return StreamingResponse(
                    stream_generator(),
                    media_type="text/plain",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                    }
                )
            else:
                response_generator = openai_client.chat_completions(
                    openai_key, request_data, stream=False
                )
                response_text = await response_generator.__anext__()
                
                # Parse response and record token usage
                token_usage = await metrics_service.extract_token_usage(response_text)
                metrics_service.record_token_usage(
                    "chat/completions", 
                    client_key,
                    **token_usage
                )
                
                # Cache the response if appropriate
                if cache_service.should_cache_request("chat", request_data):
                    await cache_service.set("chat", request_data, response_text)
                    metrics_service.record_cache_operation("set", "success")
                
                metrics_ctx.set_status_code(200)
                return JSONResponse(
                    content=json.loads(response_text),
                    status_code=200
                )
                
        except Exception as e:
            metrics_ctx.set_status_code(500)
            raise e