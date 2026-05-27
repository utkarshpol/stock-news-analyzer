# src/agents/nodes/ingestion.py
import asyncio
from src.agents.state import GraphState
from src.services.scrapers.rss_feeds import AsyncRSSFetcher

async def scrape_orchestrator_node(state: GraphState) -> dict:
    """
    LangGraph Ingestion Node: Scrape Orchestrator
    Takes structured query strings from state, runs parallel async network jobs,
    and groups live news context under their corresponding graph node keys.
    """
    # 1. Retrieve the search configurations outputted by Gemini Flash
    queries = state.get("generated_search_queries", {}) or {}
    ticker = state.get("ticker", "").upper().strip()
    logs = ["Scrape Orchestrator activated. Dispatching concurrent worker vectors."]

    if not queries:
        logs.append("⚠️ No structured query schema detected in graph state. Skipping network calls.")
        return {
            "scraped_market_data": {},
            "execution_logs": logs
        }

    fetcher = AsyncRSSFetcher()
    
    # We create tracking containers to dynamically schedule parallel coroutines
    tasks = []
    node_mapping_keys = []

    # --- Vector A: Queue Direct Asset Company Query ---
    if "company_query" in queries and queries["company_query"]:
        tasks.append(fetcher.fetch_feed_headlines(queries["company_query"], max_results=6))
        node_mapping_keys.append(ticker)

    # --- Vector B: Queue Sector Queries ---
    sector_queries = queries.get("sector_queries", {}) or {}
    for sector_name, query_str in sector_queries.items():
        tasks.append(fetcher.fetch_feed_headlines(query_str, max_results=4))
        node_mapping_keys.append(sector_name)

    # --- Vector C: Queue Commodity Queries ---
    commodity_queries = queries.get("commodity_queries", {}) or {}
    for commodity_name, query_str in commodity_queries.items():
        tasks.append(fetcher.fetch_feed_headlines(query_str, max_results=4))
        node_mapping_keys.append(commodity_name)

    # --- Vector D: Queue Macro Mover Queries ---
    mover_queries = queries.get("mover_queries", {}) or {}
    for mover_name, query_str in mover_queries.items():
        tasks.append(fetcher.fetch_feed_headlines(query_str, max_results=4))
        node_mapping_keys.append(mover_name)

    # 2. Execute all network requests concurrently via asyncio.gather
    logs.append(f"Launching {len(tasks)} parallel asynchronous RSS scraping operations.")
    results = await asyncio.gather(*tasks)

    # 3. Zip results back into our standardized dictionary shape
    scraped_market_data = {}
    for node_key, articles in zip(node_mapping_keys, results):
        scraped_market_data[node_key] = articles
        logs.append(f"Successfully scraped {len(articles)} fresh articles for node factor: '{node_key}'.")

    logs.append("Asynchronous data ingestion vector sweep successfully finalized.")

    # 4. Return variables directly mapped to your strict GraphState keys
    return {
        "scraped_market_data": scraped_market_data,
        "execution_logs": logs
    }