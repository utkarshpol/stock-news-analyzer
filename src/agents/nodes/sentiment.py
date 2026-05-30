# src/agents/nodes/sentiment.py
import json
import asyncio
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.state import GraphState
from src.utils.prompt_loader import load_prompt
from src.utils.token_governor import TokenGovernor
from langchain_ollama import ChatOllama

# Load the system guidelines markdown contract
SENTIMENT_SYSTEM_PROMPT = load_prompt("sentiment.md")

async def _analyze_single_factor_sentiment(llm, factor_name: str, articles: list) -> dict:
    """Helper coroutine to evaluate sentiment for a single macro or asset factor."""
    if not articles:
        return {
            "factor": factor_name,
            "score": 0.0,
            "rationale": "No news coverage detected within the last 24 hours.",
            "input_tokens": 0,
            "output_tokens": 0
        }

    # Format the headlines array cleanly for prompt consumption
    formatted_headlines = "\n".join([f"- {a['title']} (Source: {a['source']})" for a in articles])

    prompt = ChatPromptTemplate.from_messages([
        ("system", SENTIMENT_SYSTEM_PROMPT.replace("{", "{{").replace("}", "}}")),
        ("user", "Analyze the 24-hour news data stream for the factor: '{factor}'\n\nHeadlines:\n{headlines}")
    ])

    chain = prompt | llm

    try:
        response = await chain.ainvoke({"factor": factor_name, "headlines": formatted_headlines})
        
        # Track token usage from this specific call's metadata frame
        usage = getattr(response, "usage_metadata", {}) or {}
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)

        # Parse string safely handling potential list/string type anomalies
        raw_content = response.content
        if isinstance(raw_content, list):
            text_blocks = [block for block in raw_content if isinstance(block, str)]
            clean_str = "".join(text_blocks).strip()
        else:
            clean_str = raw_content.strip()

        # Strip markdown wrapper syntax if present
        if clean_str.startswith("```json"):
            clean_str = clean_str.split("```json")[1].split("```")[0].strip()
        elif clean_str.startswith("```"):
            clean_str = clean_str.split("```")[1].split("```")[0].strip()

        parsed_json = json.loads(clean_str)
        
        return {
            "factor": factor_name,
            "score": float(parsed_json.get("score", 0.0)),
            "rationale": parsed_json.get("rationale", "No rationale specified."),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
    except Exception as e:
        return {
            "factor": factor_name,
            "score": 0.0,
            "rationale": f"Failed to compute sentiment analysis programmatically: {str(e)}",
            "input_tokens": 0,
            "output_tokens": 0
        }

async def sentiment_agent_node(state: GraphState) -> dict:
    """
    LangGraph Agent Node: Sentiment Agent
    Iterates over the scraped real-time market data map concurrently,
    appraises localized directional news shocks via Gemini Flash, and saves the matrix.
    """
    scraped_data = state.get("scraped_market_data", {}) or {}
    logs = ["Sentiment Agent activated. Appraising market risk vector shocks."]

    if not scraped_data:
        logs.append("⚠️ Scraped data map is completely empty. Defaulting sentiment matrix to neutral.")
        return {
            "sentiment_critique": "Sentiment analysis skipped: No input news available.",
            "execution_logs": logs
        }

    # Instantiate Gemini 2.5 Flash with low temperature for analytical consistency
    llm = ChatOllama(
        model="gemma3:4b",
        temperature=0.1,
        base_url="http://ollama_service:11434"  # Pointing to Ollama service within Docker Compose network
    )

    # 1. Schedule sentiment evaluation tasks for every active graph node concurrently
    tasks = []
    for factor_name, articles in scraped_data.items():
        tasks.append(_analyze_single_factor_sentiment(llm, factor_name, articles))

    logs.append(f"Spawning {len(tasks)} concurrent sentiment scoring threads via Gemini Flash.")
    results = await asyncio.gather(*tasks)

    # 2. Process results, aggregate metrics, and build the final critique matrix payload
    sentiment_map = {}
    total_input_tokens = 0
    total_output_tokens = 0

    for res in results:
        factor = res["factor"]
        sentiment_map[factor] = {
            "score": res["score"],
            "rationale": res["rationale"]
        }
        total_input_tokens += res["input_tokens"]
        total_output_tokens += res["output_tokens"]
        
        logs.append(f"Factor Score -> '{factor}': {res['score']} | {res['rationale']}")

    # 3. Log token metrics to your global Token Governor
    if total_input_tokens or total_output_tokens:
        usage_log = TokenGovernor.track_usage(
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            node_name="Sentiment Agent (Concurrent Pool)"
        )
        logs.append(usage_log)

    # Convert the mapped evaluation dict into a structured string block for downstream logging storage
    sentiment_critique_block = json.dumps(sentiment_map, indent=2)

    # 4. Return variables directly matching our GraphState keys
    return {
        "sentiment_critique": sentiment_critique_block,
        "execution_logs": logs
    }