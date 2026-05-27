from pydantic import BaseModel, Field

class Request(BaseModel):
    ticker: str = Field(
        ..., 
        description="The stock ticker symbol (e.g., TATAMOTORS, RELIANCE)",
        examples=["TATAMOTORS"]  # v2 uses examples as a list
    )