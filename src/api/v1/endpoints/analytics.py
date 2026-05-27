# src/api/v1/analytics.py
import json
import time
from fastapi import APIRouter, HTTPException, status

from src.schemas.request import Request
from src.schemas.response import Response, PredictionBlock, Proofs
from src.agents.graph_builder import app_graph
from src.agents.state import GraphState

# Set prefix to empty string so it maps exactly to your outer router orchestration layout
router = APIRouter(prefix="", tags=["Intelligence Engine"])

@router.post(
    "/analyze",
    response_model=Response,
    status_code=status.HTTP_200_OK,
    summary="Analyze equity ticker through macro knowledge graph",
)
async def analyze_ticker(payload: Request):
    """
    API Gateway Endpoint: Ingests an equity asset symbol, triggers the fully
    compiled linear LangGraph multi-agent topology, and returns a consolidated multi-vector analysis.
    """
    start_time = time.perf_counter()
    target_ticker = payload.ticker.upper().strip()
    
    try:
        # 1. Initialize the strict state payload contract matching GraphState
        initial_state: GraphState = {
            "ticker": target_ticker,
            "execution_logs": [f"API Gateway: Initialized pipeline request trace vector for {target_ticker}."]
        }
        
        # 2. Invoke the compiled LangGraph execution thread asynchronously
        final_state = await app_graph.ainvoke(initial_state)
        latency = round(time.perf_counter() - start_time, 2)
        
        # 3. Extract and compile the structural macro path sequence string
        macro_path_list = final_state.get("macro_path", [])
        macro_path_string = " ──► ".join(macro_path_list) if macro_path_list else "No topology path extracted"
        
        # 4. Parse the localized sentiment critique JSON block into a beautiful string layout
        raw_sentiment = final_state.get("sentiment_critique", "{}")
        formatted_sentiment_summary = ""
        
        try:
            if raw_sentiment.strip().startswith("{"):
                sentiment_dict = json.loads(raw_sentiment)
                summary_lines = []
                for factor, data in sentiment_dict.items():
                    score = data.get("score", 0.0)
                    rationale = data.get("rationale", "")
                    # Visual sign indicator for high-speed terminal reporting interpretation
                    sign = "⬆️" if score > 0 else "⬇️" if score < 0 else "↔️"
                    summary_lines.append(f"• [{factor}] {sign} Score: {score:+.1f} | Rationale: {rationale}")
                formatted_sentiment_summary = "\n".join(summary_lines)
            else:
                formatted_sentiment_summary = raw_sentiment
        except Exception:
            # Safe parsing fallback string mapping if JSON structure anomalies occur
            formatted_sentiment_summary = str(raw_sentiment)

        # 5. Build and emit the verified Pydantic compliance schema response
        return Response(
            ticker=target_ticker,  # Maintains the clean base asset symbol identity mapping
            execution_latency_seconds=latency,
            prediction=PredictionBlock(
                direction=final_state.get("direction", "NEUTRAL"),
                confidence_score=final_state.get("confidence_score", 0.0)
            ),
            analytical_proofs=Proofs(
                macro_chain_discovered=macro_path_string,
                fundamental_analysis=final_state.get("fundamental_critique", "No fundamental narrative processed."),
                sentiment_summary=formatted_sentiment_summary,
                synthesis_rationale=final_state.get("synthesis_rationale", "No master synthesis thesis reached.")
            ),
            execution_logs=final_state.get("execution_logs", [])
        )
        
    except Exception as e:
        # Prevent orchestration errors from wiping trace clarity by surface mapping internal exception contexts
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph orchestration pipeline critical execution fault: {str(e)}"
        )