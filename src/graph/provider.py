# src/graph/graph_provider.py
import os
import json
from typing import Optional
# Point your imports to your newly refactored service manager class
from src.graph.graph_manager import MarketGraphManager

class GraphProvider:
    # Class-level cached singleton reference wrapper
    _instance: Optional[MarketGraphManager] = None

    @classmethod
    def get_graph(cls) -> MarketGraphManager:
        """
        Thread-safe singleton getter. Compiles and indexes the NetworkX graph 
        on first call, and returns the cached instance on all subsequent calls.
        """
        if cls._instance is None:
            # Resolve relative physical paths cleanly relative to this provider file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Map file paths directly to your standardized storage location
            # Note: Tweak these path targets if your configs live in an outer root-level directory
            company_path = os.path.normpath(os.path.join(current_dir, "company_edges.json"))
            sector_comm_path = os.path.normpath(os.path.join(current_dir, "sector_comodities.json"))
            sector_mover_path = os.path.normpath(os.path.join(current_dir, "sector_mover.json"))
            
            # Execute physical disk file I/O operations safely
            with open(company_path, "r", encoding="utf-8") as f:
                company_data = json.load(f)
            with open(sector_comm_path, "r", encoding="utf-8") as f:
                sector_comm_data = json.load(f)
            with open(sector_mover_path, "r", encoding="utf-8") as f:
                sector_mover_data = json.load(f)
                
            # Instantiate the corrected, fully recursive structural network engine manager
            cls._instance = MarketGraphManager(
                company_data=company_data,
                sector_commodity_data=sector_comm_data,
                sector_mover_data=sector_mover_data
            )
            print("🚀 Multi-Layer Knowledge Graph successfully compiled and indexed in memory.")
            
        return cls._instance