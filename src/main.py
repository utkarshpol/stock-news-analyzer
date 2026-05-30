# src/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

# Redis & LangChain Caching imports
from redis.asyncio import Redis
from langchain_community.cache import AsyncRedisCache
from langchain_core.globals import set_llm_cache

from src.graph.provider import GraphProvider
from src.api.v1.endpoints.analytics import router as analytics_v1_router

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Context Manager.
    Manages bootup compilation of the Knowledge Graph and configures the Redis global caching tier.
    """
    # 1. --- BOOTUP ACTIONS ---
    try:
        # Pre-compile the graph into memory on server bootup
        _ = GraphProvider.get_graph()
        print("🚀 Knowledge Graph successfully compiled and indexed in high-speed memory.")
    except Exception as e:
        print(f"❌ CRITICAL: Failed to load Knowledge Graph on boot: {str(e)}")
        raise e

    try:
        # Pull the injected URL from docker-compose.yml environment variables
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        # Initialize an asynchronous Redis client connection
        app.state.redis = Redis.from_url(redis_url, decode_responses=False)
        
        # Bind the global LangChain Cache to Redis with a 1-hour (3600s) TTL expiration
        set_llm_cache(AsyncRedisCache(app.state.redis, ttl=3600))
        print(f"📡 High-speed Redis caching vector successfully bound to Agent Matrix layer.")
    except Exception as e:
        print(f"⚠️ WARNING: Redis initialization failed. Running pipeline without cache: {str(e)}")
        app.state.redis = None

    yield

    # 2. --- SHUTDOWN ACTIONS ---
    if app.state.redis:
        print("🛑 Closing Redis connection pool...")
        await app.state.redis.close()
        print("🔌 Redis connection successfully terminated.")


# Instantiate the app
app = FastAPI(
    title="Autonomous Financial Intelligence & Graph-RAG Platform",
    version="1.0.0",
    description="Automated orchestration engine mapping macro ripple effects on Indian equities.",
    lifespan=lifespan
)

# Mount Routers under structured API version paths
app.include_router(analytics_v1_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)