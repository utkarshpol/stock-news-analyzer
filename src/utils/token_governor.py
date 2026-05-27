# src/agents/utils/token_governor.py
import threading

class TokenGovernor:
    # Absolute ceiling per graph invocation to prevent runaway agent loops
    MAX_TOKENS_PER_SESSION = 50_000

    _total_input_tokens = 0
    _total_output_tokens = 0
    _total_accumulated_tokens = 0
    _lock = threading.Lock()

    @classmethod
    def track_usage(cls, input_tokens: int, output_tokens: int, node_name: str) -> str:
        """
        Atomically records and monitors total token volume metrics.
        Raises an execution error if the safety governor thresholds are breached.
        """
        session_tokens = input_tokens + output_tokens
        
        with cls._lock:
            cls._total_input_tokens += input_tokens
            cls._total_output_tokens += output_tokens
            cls._total_accumulated_tokens += session_tokens
            
            # Safety trip-wire ceiling check
            if cls._total_accumulated_tokens > cls.MAX_TOKENS_PER_SESSION:
                raise RuntimeError(
                    f"CRITICAL TOKEN LIMIT BREACHED: Running session accumulated {cls._total_accumulated_tokens} "
                    f"tokens, exceeding safety threshold of {cls.MAX_TOKENS_PER_SESSION} tokens."
                )
                
            log_msg = (
                f"[{node_name}] Metrics -> Input: {input_tokens} | Output: {output_tokens} | "
                f"Running Session Total: {cls._total_accumulated_tokens} tokens"
            )
            print(log_msg)
            return log_msg

    @classmethod
    def get_session_summary(cls) -> dict:
        """Retrieves aggregated token metrics for API metadata exposure."""
        with cls._lock:
            return {
                "total_input_tokens": cls._total_input_tokens,
                "total_output_tokens": cls._total_output_tokens,
                "total_accumulated_tokens": cls._total_accumulated_tokens
            }