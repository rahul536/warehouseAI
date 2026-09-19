"""Performance metrics tracking for WarehouseAI."""

import time
from typing import Optional #typing for optional type hints. optional type hints allow for variables that can be of a specified type or None
from dataclasses import dataclass, field


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    total_latency_ms: float = 0.0
    ai_time_ms: float = 0.0
    tool_time_ms: float = 0.0
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    model: str = ""
    request_count: int = 0


# OpenAI pricing (as of 2024) - USD per 1M tokens
MODEL_PRICING = {
    "gpt-4o-mini": {
        "input": 0.150,  # $0.15 per 1M input tokens
        "output": 0.600,  # $0.60 per 1M output tokens
    },
    "gpt-4o": {
        "input": 2.50,   # $2.50 per 1M input tokens
        "output": 10.00,  # $10.00 per 1M output tokens
    },
    "gpt-4-turbo": {
        "input": 10.00,
        "output": 30.00,
    },
    "gpt-4": {
        "input": 30.00,
        "output": 60.00,
    },
    "text-embedding-3-small": {
        "input": 0.020,
        "output": 0.020,
    },
    "text-embedding-3-large": {
        "input": 0.130,
        "output": 0.130,
    },
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated cost in USD for token usage."""
    if model not in MODEL_PRICING:
        # Default to gpt-4o-mini pricing if model not found
        pricing = MODEL_PRICING["gpt-4o-mini"]
    else:
        pricing = MODEL_PRICING[model]
    
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    
    return input_cost + output_cost


def format_time_ms(ms: float) -> str:
    """Format milliseconds into human-readable string."""
    if ms < 1000:
        return f"{ms:.0f}ms"
    elif ms < 60000:
        return f"{ms/1000:.2f}s"
    else:
        minutes = int(ms / 60000)
        seconds = (ms % 60000) / 1000
        return f"{minutes}m {seconds:.0f}s"


def format_cost_usd(cost: float) -> str:
    """Format cost in USD."""
    if cost < 0.01:
        return f"${cost:.4f}"
    elif cost < 1.0:
        return f"${cost:.3f}"
    else:
        return f"${cost:.2f}"


class MetricsTracker:
    """Track performance metrics across requests."""
    
    def __init__(self):
        self.session_metrics = RequestMetrics()
        self.request_start_time: Optional[float] = None
        self.ai_start_time: Optional[float] = None
        self.tool_start_time: Optional[float] = None
        self.current_request_metrics = RequestMetrics()
    
    def start_request(self):
        """Start timing a new request."""
        self.request_start_time = time.time()
        self.current_request_metrics = RequestMetrics()
    
    def end_request(self, model: str = "") -> RequestMetrics:
        """End timing and finalize request metrics."""
        if self.request_start_time is None:
            return self.current_request_metrics
        
        total_latency = (time.time() - self.request_start_time) * 1000
        self.current_request_metrics.total_latency_ms = total_latency
        self.current_request_metrics.model = model
        
        # Add to session totals
        self.session_metrics.total_latency_ms += total_latency
        self.session_metrics.ai_time_ms += self.current_request_metrics.ai_time_ms
        self.session_metrics.tool_time_ms += self.current_request_metrics.tool_time_ms
        self.session_metrics.total_tokens += self.current_request_metrics.total_tokens
        self.session_metrics.input_tokens += self.current_request_metrics.input_tokens
        self.session_metrics.output_tokens += self.current_request_metrics.output_tokens
        self.session_metrics.estimated_cost_usd += self.current_request_metrics.estimated_cost_usd
        self.session_metrics.request_count += 1
        
        return self.current_request_metrics
    
    def start_ai_call(self):
        """Start timing an AI API call."""
        self.ai_start_time = time.time()
    
    def end_ai_call(self, input_tokens: int, output_tokens: int, model: str):
        """End timing an AI API call and record token usage."""
        if self.ai_start_time is None:
            return
        
        ai_time = (time.time() - self.ai_start_time) * 1000
        self.current_request_metrics.ai_time_ms += ai_time
        self.current_request_metrics.input_tokens += input_tokens
        self.current_request_metrics.output_tokens += output_tokens
        self.current_request_metrics.total_tokens += (input_tokens + output_tokens)
        self.current_request_metrics.estimated_cost_usd += calculate_cost(
            model, input_tokens, output_tokens
        )
        self.current_request_metrics.model = model
        self.ai_start_time = None
    
    def start_tool_call(self):
        """Start timing a tool/database call."""
        self.tool_start_time = time.time()
    
    def end_tool_call(self):
        """End timing a tool/database call."""
        if self.tool_start_time is None:
            return
        
        tool_time = (time.time() - self.tool_start_time) * 1000
        self.current_request_metrics.tool_time_ms += tool_time
        self.tool_start_time = None
    
    def get_session_summary(self) -> dict:
        """Get aggregated session metrics."""
        return {
            "total_requests": self.session_metrics.request_count,
            "total_latency_ms": self.session_metrics.total_latency_ms,
            "total_ai_time_ms": self.session_metrics.ai_time_ms,
            "total_tool_time_ms": self.session_metrics.tool_time_ms,
            "total_tokens": self.session_metrics.total_tokens,
            "total_input_tokens": self.session_metrics.input_tokens,
            "total_output_tokens": self.session_metrics.output_tokens,
            "total_cost_usd": self.session_metrics.estimated_cost_usd,
            "avg_latency_ms": (
                self.session_metrics.total_latency_ms / self.session_metrics.request_count
                if self.session_metrics.request_count > 0 else 0
            ),
        }
    
    def reset_session(self):
        """Reset all session metrics."""
        self.session_metrics = RequestMetrics()
        self.current_request_metrics = RequestMetrics()
