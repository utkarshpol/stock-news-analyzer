# src/services/graph_manager.py
import networkx as nx
from typing import List, Dict, Any

class MarketGraphManager:
    def __init__(self, company_data: dict, sector_commodity_data: dict, sector_mover_data: dict):
        """
        Initializes an in-memory Directed Graph dynamically compiled from structured JSON configurations
        using signed weights to encode directionality natively.
        """
        self.graph = nx.DiGraph()
        self._bootstrap_graph(company_data, sector_commodity_data, sector_mover_data)

    def _normalize(self, text: str) -> str:
        """Helper to ensure node names match across all layers regardless of case or spaces."""
        return text.upper().strip().replace(" ", "_")

    def _get_signed_weight(self, relationship_dict: dict) -> float:
        """Calculates signed float weight. Positive for direct relationships, Negative for inverse."""
        raw_weight = float(relationship_dict.get("weight", 1.0))
        direction = relationship_dict.get("direction", "direct").lower().strip()
        return -raw_weight if direction == "inverse" else raw_weight

    def _bootstrap_graph(self, company_data: dict, sector_commodity_data: dict, sector_mover_data: dict) -> None:
        """Parses configurations and wires signed edges across layers."""
        
        # --- LAYER 1: Wire Macro Movers -> Sectors ---
        for sector_name, content in sector_mover_data.items():
            norm_sector = self._normalize(sector_name)
            self.graph.add_node(norm_sector, node_type="SECTOR", display_name=sector_name)
            
            for mover in content.get("movers", []):
                norm_mover = self._normalize(mover["name"])
                signed_w = self._get_signed_weight(mover)
                
                self.graph.add_node(norm_mover, node_type="MACRO_MOVER", display_name=mover["name"])
                self.graph.add_edge(norm_mover, norm_sector, weight=signed_w, edge_type="MOVER_TO_SECTOR")

        # --- LAYER 2: Wire Commodities -> Sectors ---
        for sector_name, content in sector_commodity_data.items():
            norm_sector = self._normalize(sector_name)
            self.graph.add_node(norm_sector, node_type="SECTOR", display_name=sector_name)
            
            for commodity in content.get("commodities", []):
                norm_comm = self._normalize(commodity["name"])
                signed_w = self._get_signed_weight(commodity)
                
                self.graph.add_node(norm_comm, node_type="COMMODITY", display_name=commodity["name"])
                self.graph.add_edge(norm_comm, norm_sector, weight=signed_w, edge_type="COMMODITY_TO_SECTOR")

        # --- LAYER 3: Wire Sectors -> Tickers & Direct Overrides ---
        for ticker, asset_rules in company_data.items():
            norm_ticker = self._normalize(ticker)
            norm_sector = self._normalize(asset_rules["sector"])
            
            self.graph.add_node(norm_ticker, node_type="TICKER", display_name=ticker)
            self.graph.add_node(norm_sector, node_type="SECTOR", display_name=asset_rules["sector"])
            
            self.graph.add_edge(norm_sector, norm_ticker, edge_type="SECTOR_TO_TICKER", weight=1.0)
            
            for comm in asset_rules.get("commodities", []):
                norm_comm = self._normalize(comm["name"])
                signed_w = self._get_signed_weight(comm)
                self.graph.add_node(norm_comm, node_type="COMMODITY", display_name=comm["name"])
                self.graph.add_edge(norm_comm, norm_ticker, weight=signed_w, edge_type="DIRECT_COMMODITY_OVERRIDE")
                
            for mover in asset_rules.get("movers", []):
                norm_mover = self._normalize(mover["name"])
                signed_w = self._get_signed_weight(mover)
                self.graph.add_node(norm_mover, node_type="MACRO_MOVER", display_name=mover["name"])
                self.graph.add_edge(norm_mover, norm_ticker, weight=signed_w, edge_type="DIRECT_MOVER_OVERRIDE")

    def extract_influences(self, ticker: str) -> tuple[List[str], List[Dict[str, Any]]]:
        """
        Recursively extracts EVERY upstream node affecting the target stock ticker
        by traversing all ancestor layers (Direct & Indirect relationships).
        """
        normalized_ticker = self._normalize(ticker)
        if normalized_ticker not in self.graph:
            return [ticker.upper()], []

        # Find ALL ancestors in the directed graph layout recursively
        ancestors = nx.ancestors(self.graph, normalized_ticker)
        
        # Track the linear order traversed
        macro_path = [self.graph.nodes[node].get("display_name", node) for node in ancestors]
        macro_path.append(ticker.upper())

        structural_weights = []
        
        # Check explicit dependencies for the asset and its parent components
        nodes_to_check = list(ancestors) + [normalized_ticker]
        
        for current_node in nodes_to_check:
            # We look at all incoming edges to extract real-world operational signs
            for u, v, data in self.graph.in_edges(current_node, data=True):
                # Ensure we only track items that affect our ticker ecosystem path execution
                source_display_name = self.graph.nodes[u].get("display_name", u)
                
                # Deduplicate nodes so we don't return duplicate vector instructions to the query planner
                if not any(sw["source"] == source_display_name for sw in structural_weights):
                    structural_weights.append({
                        "source": source_display_name,
                        "node_type": self.graph.nodes[u].get("node_type"),
                        "edge_type": data.get("edge_type"),
                        "weight": data.get("weight", 1.0)
                    })

        return macro_path, structural_weights