# src/agents/nodes/graph_router.py
from src.agents.state import GraphState
from src.graph.provider import GraphProvider

async def graph_routing_engine_node(state: GraphState) -> dict:
    """
    LangGraph Entry Point Node: Graph Router
    Consumes a stock ticker, extracts its complete upstream systemic macro dependencies 
    from the thread-safe cached NetworkX manager singleton, and registers them to state.
    """
    ticker = state.get("ticker", "").upper().strip()
    logs = [f"Graph Router activated for ticker input: {ticker}."]

    if not ticker:
        logs.append("❌ CRITICAL ERROR: Empty ticker symbol submitted to the execution pipeline.")
        return {
            "macro_path": [],
            "structural_weights": [],
            "execution_logs": logs
        }

    try:
        # Retrieve the single pre-cached application instance out of memory context
        graph_manager = GraphProvider.get_graph()
        
        # Execute the full recursive ancestor traversal sweep
        macro_path, structural_weights = graph_manager.extract_influences(ticker)
        
        logs.append(f"Successfully traversed topology graph. Discovered {len(structural_weights)} systemic macro drivers.")
        for item in structural_weights:
            logs.append(
                f"Mapped Factor Driver -> '{item['source']}' ({item['node_type']}) | "
                f"Edge Type: {item['edge_type']} | Correlation Weight: {item['weight']}"
            )
            
    except Exception as e:
        logs.append(f"❌ CRITICAL GRAPH ROUTER ERROR: {str(e)}")
        macro_path, structural_weights = [ticker], []

    return {
        "macro_path": macro_path,
        "structural_weights": structural_weights,
        "execution_logs": logs
    }