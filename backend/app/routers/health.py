from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.cache import cache_service

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "redis_connected": cache_service.redis is not None
    }
    
    # Test Redis connection if available
    if cache_service.redis:
        try:
            await cache_service.redis.ping()
            health_status["redis_connected"] = True
        except Exception:
            health_status["redis_connected"] = False
            health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return JSONResponse(
        content=health_status,
        status_code=status_code
    )