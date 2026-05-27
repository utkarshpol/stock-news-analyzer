# src/agents/graph_builder.py
from langgraph.graph import StateGraph, END
from src.agents.state import GraphState

# --- Step 2: Import your Graph Engine / Router Node ---
# NOTE: Replace this placeholder with the actual import path to your NetworkX graph node
from src.agents.nodes.graph_router import graph_routing_engine_node

# --- Step 3: Import Ingestion Nodes ---
from src.agents.nodes.query_planner import query_planner_agent_node
from src.agents.nodes.scrape_orchestrator import scrape_orchestrator_node

# --- Step 4: Import Analytics Workers ---
from src.agents.nodes.fundamental import fundamental_agent_node
from src.agents.nodes.sentiment import sentiment_agent_node

# --- Step 5: Import Final Aggregator Master ---
from src.agents.nodes.synthesis import synthesis_agent_node

def create_workflow():
    """
    Builds and compiles a strictly linear LangGraph pipeline matching 
    our Graph-RAG Multi-Vector Architecture flow.
    """
    # 1. Initialize the state graph with your strict GraphState schema
    workflow = StateGraph(GraphState)
    
    # 2. Register every node component explicitly with a unique string key
    workflow.add_node("graph_router_key", graph_routing_engine_node)
    workflow.add_node("query_planner_key", query_planner_agent_node)
    workflow.add_node("scrape_orchestrator_key", scrape_orchestrator_node)
    workflow.add_node("sentiment_agent_key", sentiment_agent_node)
    workflow.add_node("fundamental_agent_key", fundamental_agent_node)
    workflow.add_node("synthesis_agent_key", synthesis_agent_node)
    
    # 3. Set the absolute pipeline entryway to the NetworkX Router Engine
    workflow.set_entry_point("graph_router_key")
    
    # 4. Bind the sequential execution paths explicitly
    # Flow: Router -> Query Planner -> Scraper -> Sentiment -> Fundamental -> Synthesis -> END
    workflow.add_edge("graph_router_key", "query_planner_key")
    workflow.add_edge("query_planner_key", "scrape_orchestrator_key")
    workflow.add_edge("scrape_orchestrator_key", "sentiment_agent_key")
    workflow.add_edge("sentiment_agent_key", "fundamental_agent_key")
    workflow.add_edge("fundamental_agent_key", "synthesis_agent_key")
    workflow.add_edge("synthesis_agent_key", END)
    
    # 5. Compile the topology into an executable runnable application
    return workflow.compile()

# Instantiate the compiled runnable graph for your API or test framework to access
app_graph = create_workflow()