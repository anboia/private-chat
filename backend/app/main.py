import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.utils.logging import configure_logging
from app.services.openai_client import openai_client
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging import LoggingMiddleware
from app.routers import chat, completions, embeddings, models, health, metrics
from app.services.cache import cache_service
from app.services.metrics import metrics_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    await openai_client.initialize()
    await cache_service.initialize()
    await metrics_service.initialize()
    yield
    await openai_client.close()
    await cache_service.close()
    await metrics_service.close()


app = FastAPI(
    title="OpenAI Proxy Server",
    description="A transparent proxy server for the OpenAI API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

app.include_router(health.router, prefix="", tags=["health"])
app.include_router(metrics.router, prefix="", tags=["metrics"])
app.include_router(chat.router, prefix="/v1", tags=["chat"])
app.include_router(completions.router, prefix="/v1", tags=["completions"])
app.include_router(embeddings.router, prefix="/v1", tags=["embeddings"])
app.include_router(models.router, prefix="/v1", tags=["models"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )