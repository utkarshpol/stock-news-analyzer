# src/utils/prompt_loader.py
import os

def load_prompt(filename: str) -> str:
    """Reads and returns system prompt strings from the prompts markdown repository."""
    # 1. Evaluates to: /Users/utkarshpol/Desktop/StockAnalysis/backend/src/utils
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Use ".." to back up one level out of 'utils' into 'src'
    # Then step straight down into 'agents' -> 'prompts'
    prompt_path = os.path.normpath(os.path.join(current_dir, "..", "agents", "prompts", filename))
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()