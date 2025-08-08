import hashlib
import json
from typing import Any, Dict, Optional
import redis.asyncio as redis
import structlog

from app.config import settings

logger = structlog.get_logger()


class CacheService:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def initialize(self):
        try:
            self.redis = redis.from_url(
                settings.cache.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            await self.redis.ping()
            await logger.ainfo("Redis connection established", redis_url=settings.cache.redis_url)
        except Exception as e:
            await logger.awarning(f"Redis connection failed: {e}. Caching will be disabled. Make sure Redis is running locally on port 6379.")
            self.redis = None

    async def close(self):
        if self.redis:
            await self.redis.close()

    def _generate_cache_key(self, endpoint: str, request_data: Dict[str, Any]) -> str:
        # Create a deterministic cache key based on endpoint and request data
        data_str = json.dumps(request_data, sort_keys=True, separators=(',', ':'))
        hash_obj = hashlib.sha256(f"{endpoint}:{data_str}".encode())
        return f"openai_proxy:{endpoint}:{hash_obj.hexdigest()[:16]}"

    async def get(self, endpoint: str, request_data: Dict[str, Any]) -> Optional[str]:
        if not self.redis:
            return None

        try:
            cache_key = self._generate_cache_key(endpoint, request_data)
            cached_response = await self.redis.get(cache_key)
            
            if cached_response:
                await logger.adebug("Cache hit", cache_key=cache_key)
                return cached_response
            else:
                await logger.adebug("Cache miss", cache_key=cache_key)
                return None
                
        except Exception as e:
            await logger.awarning("Cache get error", error=str(e))
            return None

    async def set(
        self,
        endpoint: str,
        request_data: Dict[str, Any],
        response_data: str,
        ttl: Optional[int] = None
    ) -> bool:
        if not self.redis:
            return False

        try:
            cache_key = self._generate_cache_key(endpoint, request_data)
            
            # Use endpoint-specific TTL or default
            if ttl is None:
                if endpoint == "embeddings":
                    ttl = settings.cache.embeddings_ttl
                else:
                    ttl = settings.cache.default_ttl

            await self.redis.setex(cache_key, ttl, response_data)
            await logger.adebug("Cache set", cache_key=cache_key, ttl=ttl)
            return True
            
        except Exception as e:
            await logger.awarning("Cache set error", error=str(e))
            return False

    async def delete(self, endpoint: str, request_data: Dict[str, Any]) -> bool:
        if not self.redis:
            return False

        try:
            cache_key = self._generate_cache_key(endpoint, request_data)
            deleted = await self.redis.delete(cache_key)
            return bool(deleted)
            
        except Exception as e:
            await logger.awarning("Cache delete error", error=str(e))
            return False

    async def clear_pattern(self, pattern: str) -> int:
        if not self.redis:
            return 0

        try:
            keys = await self.redis.keys(f"openai_proxy:*{pattern}*")
            if keys:
                deleted = await self.redis.delete(*keys)
                await logger.ainfo("Cache cleared", pattern=pattern, deleted=deleted)
                return deleted
            return 0
            
        except Exception as e:
            await logger.awarning("Cache clear error", error=str(e))
            return 0

    def should_cache_request(self, endpoint: str, request_data: Dict[str, Any]) -> bool:
        # Only cache deterministic requests
        if endpoint == "embeddings":
            return True
        
        # Don't cache streaming requests
        if request_data.get("stream", False):
            return False
        
        # Don't cache requests with temperature > 0 (non-deterministic)
        if request_data.get("temperature", 1.0) > 0:
            return False
        
        # Don't cache requests with random seed
        if "seed" not in request_data:
            return False
        
        return False  # Conservative approach - only cache embeddings by default


cache_service = CacheService()