# src/agents/nodes/fundamental.py
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from src.agents.state import GraphState
from src.services.market_data import MarketDataService
from src.utils.prompt_loader import load_prompt
from src.utils.token_governor import TokenGovernor

FUNDAMENTAL_SYSTEM_PROMPT = load_prompt("fundamental.md")
market_service = MarketDataService()

async def fundamental_agent_node(state: GraphState) -> dict:
    """
    LangGraph Agent Node: Fundamental Agent
    Ingests live Yahoo Finance corporate metrics, populates raw data points into state, 
    and leverages Gemini Flash to synthesize a company structural health critique.
    """
    ticker = state.get("ticker", "").upper().strip()
    logs = ["Fundamental Agent activated. Fetching live financial statement data frames."]

    if not ticker:
        logs.append("❌ Error: Ticker input missing. Fundamental analysis aborted.")
        return {
            "fundamental_critique": "Analysis failed: Ticker missing.",
            "execution_logs": logs
        }

    # 1. Fetch live metrics programmatically via Yahoo Finance thread delegate
    current_price, metrics = await market_service.get_corporate_fundamentals(ticker)
    logs.append(f"Successfully ingested yfinance context data. Spot Price: {current_price} INR.")
    
    # 2. Setup Gemini 2.5 Flash to execute the qualitative evaluation
    llm = ChatOllama(
        model="gemma3:4b",
        temperature=0.1
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", FUNDAMENTAL_SYSTEM_PROMPT.replace("{", "{{").replace("}", "}}")),
        ("user", "Analyze the corporate fundamental profile for target ticker: {ticker}\n\nMetrics Payload:\n{metrics_json}")
    ])
    
    chain = prompt | llm
    metrics_json_str = json.dumps(metrics, indent=2)

    try:
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
                node_name="Fundamental Agent (Gemini Flash)"
            )
            logs.append(usage_log)
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