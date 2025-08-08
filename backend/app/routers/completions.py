import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.models.completions import CompletionRequest
from app.services.openai_client import openai_client
from app.services.cache import cache_service
from app.services.metrics import metrics_service, RequestMetricsContext

router = APIRouter()


@router.post("/completions")
async def completions(request: Request, completion_request: CompletionRequest):
    client_key = request.state.client_key
    openai_key = request.state.openai_key
    
    async with RequestMetricsContext(
        metrics_service, "completions", "POST", client_key
    ) as metrics_ctx:
        
        try:
            request_data = completion_request.model_dump(exclude_unset=True)
            
            # Check cache for non-streaming requests
            if not completion_request.stream and cache_service.should_cache_request("completions", request_data):
                cached_response = await cache_service.get("completions", request_data)
                if cached_response:
                    metrics_service.record_cache_operation("get", "hit")
                    metrics_ctx.set_status_code(200)
                    
                    # Extract and record token usage from cached response
                    token_usage = await metrics_service.extract_token_usage(cached_response)
                    metrics_service.record_token_usage(
                        "completions", 
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
            response_text = await openai_client.completions(openai_key, request_data)
            
            # Parse response and record token usage
            token_usage = await metrics_service.extract_token_usage(response_text)
            metrics_service.record_token_usage(
                "completions", 
                client_key,
                **token_usage
            )
            
            # Cache the response if appropriate
            if cache_service.should_cache_request("completions", request_data):
                await cache_service.set("completions", request_data, response_text)
                metrics_service.record_cache_operation("set", "success")
            
            metrics_ctx.set_status_code(200)
            return JSONResponse(
                content=json.loads(response_text),
                status_code=200
            )
            
        except Exception as e:
            metrics_ctx.set_status_code(500)
            raise e