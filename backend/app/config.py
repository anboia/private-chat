import os
from functools import lru_cache
from typing import Dict, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class RateLimitSettings(BaseModel):
    requests_per_minute: int = Field(default=60, description="Requests per minute per API key")
    tokens_per_minute: int = Field(default=100000, description="Tokens per minute per API key")


class CacheSettings(BaseModel):
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    embeddings_ttl: int = Field(default=3600, description="Embeddings cache TTL in seconds")
    default_ttl: int = Field(default=300, description="Default cache TTL in seconds")


class Settings(BaseSettings):
    environment: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")
    
    openai_api_base: str = Field(default="https://api.openai.com/v1", description="OpenAI API base URL")
    openai_api_key: str = Field(description="Default OpenAI API key")
    
    client_api_keys: str = Field(default="", description="Comma-separated client API keys")
    api_key_mapping: str = Field(default="", description="JSON mapping of client keys to OpenAI keys")
    
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    
    retry_max_attempts: int = Field(default=3, description="Maximum retry attempts")
    retry_backoff_factor: float = Field(default=2.0, description="Exponential backoff factor")
    
    log_level: str = Field(default="INFO", description="Logging level")
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def get_openai_key_for_client(client_key: str) -> Optional[str]:
    if not settings.api_key_mapping:
        return settings.openai_api_key
    
    try:
        import json
        mapping = json.loads(settings.api_key_mapping)
        return mapping.get(client_key, settings.openai_api_key)
    except (json.JSONDecodeError, KeyError):
        return settings.openai_api_key


def get_valid_client_keys() -> set:
    if not settings.client_api_keys:
        return set()
    return set(key.strip() for key in settings.client_api_keys.split(",") if key.strip())