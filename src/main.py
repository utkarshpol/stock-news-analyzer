# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.graph.provider import GraphProvider
from src.api.v1.endpoints.analytics import router as analytics_v1_router
from dotenv import load_dotenv
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Context Manager.
    Kept here because it explicitly manages the lifecycle state of the 'app' instance.
    """
    try:
        # Pre-compile the graph into memory on server bootup
        _ = GraphProvider.get_graph()
        print("🚀 Knowledge Graph successfully compiled and indexed in high-speed memory.")
    except Exception as e:
        print(f"❌ CRITICAL: Failed to load Knowledge Graph on boot: {str(e)}")
        raise e
    yield

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