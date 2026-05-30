# src/agents/nodes/query_planner.py
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.state import GraphState
from src.utils.prompt_loader import load_prompt
from src.utils.token_governor import TokenGovernor
from langchain_ollama import ChatOllama

QUERY_PLANNER_SYSTEM_PROMPT = load_prompt("query_planner.md")

async def query_planner_agent_node(state: GraphState) -> dict:
    """
    LangGraph Agent Node: Query Planner (Powered by Gemini 1.5 Flash)
    Translates graph components into precise RSS search queries with robust token auditing.
    """
    ticker = state.get("ticker", "").upper().strip()
    structural_weights = state.get("structural_weights", [])
    logs = state.get("execution_logs", [])
    
    logs.append("Query Planner Agent activated. Building target vectors via Gemini Flash.")
    
    # 1. Segment graph nodes by category type
    sector_nodes = [w["source"] for w in structural_weights if w["node_type"] == "SECTOR"]
    commodity_nodes = [w["source"] for w in structural_weights if w["node_type"] == "COMMODITY"]
    mover_nodes = [w["source"] for w in structural_weights if w["node_type"] == "MACRO_MOVER"]
    
    llm_context = {
        "target_ticker": ticker,
        "discovered_sectors": sector_nodes,
        "discovered_commodities": commodity_nodes,
        "discovered_macro_movers": mover_nodes
    }
    
    # 2. Compile system guidelines string context
    prompt = ChatPromptTemplate.from_messages([
        ("system", QUERY_PLANNER_SYSTEM_PROMPT.replace("{", "{{").replace("}", "}}")),
        ("user", "Construct optimized RSS search vectors for the following market layout:\n{context}")
    ])
    
    # Instantiate Gemini 2.5 Flash
    llm = ChatOllama(
        model="gemma3:4b",
        temperature=0.1,
        base_url="http://ollama_service:11434"  # Pointing to Ollama service within Docker Compose network
    )
    
    # To programmatically grab token metrics without a callback wrapper, 
    # we call the raw chain generation instead of immediately stripping it with structured dict generation.
    chain = prompt | llm
    
    try:
        # 3. Fire the generation step
        ai_message = await chain.ainvoke({"context": json.dumps(llm_context)})
        
        # --- TOKEN GOVERNOR INSTRUMENTATION TRACKING ---
        # Gemini records token volumes inside the native usage_metadata frame of the AIMessage response
        usage_metadata = getattr(ai_message, "usage_metadata", {}) or {}
        input_tokens = usage_metadata.get("input_tokens", 0)
        output_tokens = usage_metadata.get("output_tokens", 0)
        
        if input_tokens or output_tokens:
            usage_log = TokenGovernor.track_usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                node_name="Query Planner Agent (Gemini Flash)"
            )
            logs.append(usage_log)
        else:
            logs.append("[Query Planner Agent] Metrics -> Logged via pipeline trace wrapper context.")
        # -----------------------------------------------

        # 4. Extract and parse the output text programmatically into a JSON dictionary safely
        raw_content = ai_message.content
        
        # Resolve the Pylance type issue by ensuring we are dealing with a clean string string
        if isinstance(raw_content, list):
            # If Gemini wraps the content inside a block list, extract the text element
            text_blocks = [block for block in raw_content if isinstance(block, str)]
            clean_string = "".join(text_blocks).strip()
        elif isinstance(raw_content, str):
            clean_string = raw_content.strip()
        else:
            raise ValueError("Unexpected content layout structure received from the Gemini Gateway.")

        # Strip away markdown backticks if Gemini added any text wrapping strings
        if clean_string.startswith("```json"):
            clean_string = clean_string.split("```json")[1].split("```")[0].strip()
        elif clean_string.startswith("```"):
            clean_string = clean_string.split("```")[1].split("```")[0].strip()
            
        generated_queries = json.loads(clean_string)
        logs.append("Query Planner Agent successfully mapped out targeted search arrays.")
        
    except Exception as e:
        # Fallback dictionary to avoid pipeline execution interruption
        logs.append(f"⚠️ Query Planner Gemini exception caught: {str(e)}. Falling back to programmatic defaults.")
        generated_queries = {
            "company_query": f"{ticker} stock India news headlines",
            "sector_queries": {s: f"{s} sector India market updates" for s in sector_nodes},
            "commodity_queries": {c: f"{c} price commodity India trends" for c in commodity_nodes},
            "mover_queries": {m: f"{m} economy India impact factor" for m in mover_nodes}
        }
    return {
        "generated_search_queries": generated_queries,
        "execution_logs": logs
    }