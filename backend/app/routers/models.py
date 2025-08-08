import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.openai_client import openai_client
from app.services.cache import cache_service
from app.services.metrics import metrics_service, RequestMetricsContext

router = APIRouter()


@router.get("/models")
async def models(request: Request):
    client_key = request.state.client_key
    openai_key = request.state.openai_key
    
    async with RequestMetricsContext(
        metrics_service, "models", "GET", client_key
    ) as metrics_ctx:
        
        try:
            # Check cache (models list doesn't change frequently)
            request_data = {"endpoint": "models"}
            cached_response = await cache_service.get("models", request_data)
            if cached_response:
                metrics_service.record_cache_operation("get", "hit")
                metrics_ctx.set_status_code(200)
                
                return JSONResponse(
                    content=json.loads(cached_response),
                    status_code=200
                )
            else:
                metrics_service.record_cache_operation("get", "miss")
            
            # Make request to OpenAI
            response_text = await openai_client.models(openai_key)
            
            # Cache the response with shorter TTL (models list can change)
            await cache_service.set("models", request_data, response_text, ttl=300)  # 5 minutes
            metrics_service.record_cache_operation("set", "success")
            
            metrics_ctx.set_status_code(200)
            return JSONResponse(
                content=json.loads(response_text),
                status_code=200
            )
            
        except Exception as e:
            metrics_ctx.set_status_code(500)
            raise e