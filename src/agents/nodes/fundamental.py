# src/agents/nodes/fundamental.py
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from src.agents.state import GraphState
from src.services.market_data import MarketDataService
from src.services.cache_services import CacheService  # <-- Ingest the Redis Service handle
from src.utils.prompt_loader import load_prompt
from src.utils.token_governor import TokenGovernor
from langchain_core.globals import get_llm_cache

FUNDAMENTAL_SYSTEM_PROMPT = load_prompt("fundamental.md")
market_service = MarketDataService()

async def fundamental_agent_node(state: GraphState) -> dict:
    """
    LangGraph Agent Node: Fundamental Agent
    Ingests live Yahoo Finance corporate metrics, leverages CacheService to prevent duplicate 
    API overhead, populates raw data points into state, and triggers Gemma 3 local inference.
    """
    ticker = state.get("ticker", "").upper().strip()
    logs = ["Fundamental Agent activated. Appraising financial statement context vectors."]

    if not ticker:
        logs.append("❌ Error: Ticker input missing. Fundamental analysis aborted.")
        return {
            "fundamental_critique": "Analysis failed: Ticker missing.",
            "execution_logs": logs
        }

    # 1. Check Redis Application Caching Layer for existing metric schemas
    metrics_cache_key = f"metrics:fundamental:{ticker}"
    cached_payload = await CacheService.get(metrics_cache_key)
    
    if cached_payload:
        logs.append(f"🎯 Redis Cache Hit: Reusing persistent valuation matrix for {ticker}.")
        current_price = cached_payload.get("current_price", 0.0)
        metrics = cached_payload.get("metrics", {})
    else:
        logs.append(f"🔄 Redis Cache Miss: Querying live yfinance thread delegates for {ticker}...")
        # Fetch live metrics programmatically via Yahoo Finance thread delegate
        current_price, metrics = await market_service.get_corporate_fundamentals(ticker)
        
        # Save payload back to Redis container with a 15-minute TTL (900 seconds)
        await CacheService.set(
            key=metrics_cache_key,
            value={"current_price": current_price, "metrics": metrics},
            ttl_seconds=900
        )
        logs.append(f"💾 Ingested fresh yfinance context data. Spot Price: {current_price} INR. Committed to Redis cache.")
    
    # 2. Setup ChatOllama to execute the qualitative evaluation
    llm = ChatOllama(
        model="gemma3:4b",
        temperature=0.1,
        base_url="http://ollama_service:11434"  # Pointing to Ollama service within Docker Compose network
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", FUNDAMENTAL_SYSTEM_PROMPT.replace("{", "{{").replace("}", "}}")),
        ("user", "Analyze the corporate fundamental profile for target ticker: {ticker}\n\nMetrics Payload:\n{metrics_json}")
    ])
    
    chain = prompt | llm
    metrics_json_str = json.dumps(metrics, indent=2)

    try:
        # Check if the global LangChain Cache will catch this exact prompt string execution
        llm_cache = get_llm_cache()
        if llm_cache:
            logs.append("📡 LangChain global caching layer online. Scanning Redis string hashes...")

        response = await chain.ainvoke({
            "ticker": ticker,
            "metrics_json": metrics_json_str
        })
        
        # --- TOKEN GOVERNOR INSTRUMENTATION TRACKING ---
        usage = getattr(response, "usage_metadata", {}) or {}
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        
        if input_tokens or output_tokens:
            usage_log = TokenGovernor.track_usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                node_name="Fundamental Agent (Gemma 3 Local)"
            )
            logs.append(usage_log)
        else:
            # If input/output tokens evaluate to 0 while a global cache layer is mounted, it's a hit!
            if llm_cache:
                logs.append("⚡ LLM Cache Hit: Fast-forwarding prompt synthesis straight out of Redis storage.")
        # -----------------------------------------------

        # Handle type-narrowing safely for content responses
        raw_content = response.content
        if isinstance(raw_content, list):
            text_blocks = [block for block in raw_content if isinstance(block, str)]
            critique = "".join(text_blocks).strip()
        else:
            critique = raw_content.strip()

        logs.append("Fundamental critique narrative compiled successfully.")

    except Exception as e:
        logs.append(f"⚠️ Fundamental evaluation failed to compile: {str(e)}")
        critique = f"Programmatic data fallback mode activated. Core metrics pulled: {metrics_json_str}"

    # 3. Return updates mapped directly to your strict GraphState keys
    return {
        "current_price": current_price,
        "market_metrics": metrics,
        "fundamental_critique": critique,
        "execution_logs": logs
    }