from pydantic import BaseModel, Field
from typing import List

class PredictionBlock(BaseModel):
    direction: str = Field(..., description="Predicted short-term trend (BULLISH/BEARISH)")
    # FIX: Change from Field("7_DAYS", ...) to Field(default="7_DAYS", ...)
    horizon: str = Field(default="7_DAYS", description="The analytical forecast window")
    confidence_score: float = Field(..., description="The model's confidence weight (0.0 to 1.0)")

class Proofs(BaseModel):
    macro_chain_discovered: str = Field(..., description="Discovered relationship pipeline paths")
    fundamental_analysis: str = Field(..., description="Synthesis text from fundamental agent")
    sentiment_summary: str = Field(..., description="Synthesis text from sentiment agent")
    synthesis_rationale: str = Field(..., description="Final compiled structural justification")

class Response(BaseModel):
    ticker: str
    # FIX: Assign the default value directly using = 945.20
    current_price: float = Field(default=945.20, description="Mock current price point")
    execution_latency_seconds: float
    # FIX: Do the same for cached_response just to be clean and safe
    cached_response: bool = Field(default=False, description="Whether payload was resolved via Redis")
    prediction: PredictionBlock
    analytical_proofs: Proofs
    execution_logs: List[str] = Field(..., description="Traceability audit logs from graph execution")