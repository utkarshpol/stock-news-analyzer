# src/services/market_data.py
import asyncio
import yfinance as yf
from typing import Dict, Any, Tuple

class MarketDataService:
    @staticmethod
    def _fetch_yf_data(ticker_symbol: str) -> Tuple[float, Dict[str, Any]]:
        """Synchronous yfinance execution frame."""
        # Append standard NSE suffix for Indian market lookup compatibility
        formatted_ticker = f"{ticker_symbol.upper().strip()}.NS"
        ticker_obj = yf.Ticker(formatted_ticker)
        
        # Extract live trailing info context maps safely
        info = ticker_obj.info or {}
        
        # Extract spot price safely across standard possible structural keys
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
        
        # Isolate baseline corporate metric parameters
        metrics = {
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "price_to_book": info.get("priceToBook"),
            "debt_to_equity": info.get("debtToEquity"),  # Expressed as a percentage (e.g., 85.5 = 0.85)
            "return_on_equity": info.get("returnOnEquity"),
            "operating_margins": info.get("operatingMargins"),
            "free_cashflow": info.get("freeCashflow"),
            "market_cap": info.get("marketCap")
        }
        
        return float(current_price), metrics

    async def get_corporate_fundamentals(self, ticker_symbol: str) -> Tuple[float, Dict[str, Any]]:
        """
        Asynchronously fetches core fundamental data structures from Yahoo Finance 
        without freezing the underlying async engine execution loop.
        """
        try:
            # Delegate blocking synchronous I/O operations to an internal worker thread pool
            current_price, metrics = await asyncio.to_thread(self._fetch_yf_data, ticker_symbol)
            return current_price, metrics
        except Exception:
            # Safe empty schema fallback structure if ticker allocation or network blocks occur
            return 0.0, {k: None for k in ["pe_ratio", "forward_pe", "price_to_book", "debt_to_equity", "return_on_equity", "operating_margins", "free_cashflow", "market_cap"]}