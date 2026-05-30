# src/agents/nodes/synthesis.py
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.state import GraphState
from src.utils.prompt_loader import load_prompt
from src.utils.token_governor import TokenGovernor
from langchain_ollama import ChatOllama

SYNTHESIS_SYSTEM_PROMPT = load_prompt("synthesis.md")

async def synthesis_agent_node(state: GraphState) -> dict:
    """
    LangGraph Agent Node: Synthesis Agent (Master Aggregator)
    Acts as the final pipeline brain, fusing quantitative graph dependencies,
    24-hour sentiment shocks, and fundamental health parameters into a final decision.
    """
    ticker = state.get("ticker", "").upper().strip()
    structural_weights = state.get("structural_weights", [])
    sentiment_critique = state.get("sentiment_critique", "{}")
    fundamental_critique = state.get("fundamental_critique", "")
    logs = ["Synthesis Agent activated. Compiling master structural investment matrix."]

    # 1. Format the multi-agent context parameters for the LLM input frame
    context_payload = {
        "target_asset": ticker,
        "structural_graph_weights": structural_weights,
        "realtime_sentiment_matrix": json.loads(sentiment_critique) if sentiment_critique.startswith("{") else sentiment_critique,
        "corporate_fundamental_health": fundamental_critique
    }

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYNTHESIS_SYSTEM_PROMPT.replace("{", "{{").replace("}", "}}")),
        ("user", "Synthesize a market payload decision for the asset context layout:\n{context_json}")
    ])

    # Instantiate Gemini 2.5 Flash 
    llm = ChatOllama(
        model="gemma3:4b",
        temperature=0.1,
        base_url="http://ollama_service:11434"  # Pointing to Ollama service within Docker Compose network
    )

    chain = prompt | llm

    try:
        # 2. Fire the consolidated inference generation request
        response = await chain.ainvoke({"context_json": json.dumps(context_payload, indent=2)})

        # --- TOKEN GOVERNOR INSTRUMENTATION TRACKING ---
        usage = getattr(response, "usage_metadata", {}) or {}
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        
        if input_tokens or output_tokens:
            usage_log = TokenGovernor.track_usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                node_name="Synthesis Agent (Gemini Flash Master)"
            )
            logs.append(usage_log)
        # -----------------------------------------------

        # Handle type-narrowing safely for the returned message block
        raw_content = response.content
        if isinstance(raw_content, list):
            text_blocks = [block for block in raw_content if isinstance(block, str)]
            clean_str = "".join(text_blocks).strip()
        else:
            clean_str = raw_content.strip()

        # Strip markdown syntax wraps securely
        if clean_str.startswith("```json"):
            clean_str = clean_str.split("```json")[1].split("```")[0].strip()
        elif clean_str.startswith("```"):
            clean_str = clean_str.split("```")[1].split("```")[0].strip()

        # 3. Parse final structured payload choices
        parsed_decision = json.loads(clean_str)
        direction = parsed_decision.get("direction", "NEUTRAL").upper().strip()
        confidence = float(parsed_decision.get("confidence_score", 0.5))
        rationale = parsed_decision.get("synthesis_rationale", "No operational thesis provided.")
        
        logs.append(f"🏁 Synthesis finalized. Conclusion: {direction} | Conviction Score: {confidence * 100:.1f}%")

    except Exception as e:
        logs.append(f"❌ Synthesis synthesis failure: {str(e)}. Triggering safe protective fallback state.")
        direction = "NEUTRAL"
        confidence = 0.0
        rationale = f"Pipeline execution fell back due to compilation fault: {str(e)}"

    # 4. Return variables directly matching our GraphState keys to terminate the workflow
    return {
        "direction": direction,
        "confidence_score": confidence,
        "synthesis_rationale": rationale,
        "execution_logs": logs
    }