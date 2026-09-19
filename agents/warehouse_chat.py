import json
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from openai import OpenAI

from agents.warehouse_agent import (
    MODEL,
    SYSTEM_INSTRUCTIONS,
    TOOLS,
    call_wms_tool,
)
from src.metrics import MetricsTracker, format_time_ms, format_cost_usd, calculate_cost


def run_chat_turn(
    client: OpenAI,
    history: list,
    question: str,
    tool_trace: list | None = None,
    metrics_tracker: MetricsTracker | None = None,
) -> str:
    """Run one user turn, including any WMS function calls."""

    if metrics_tracker:
        metrics_tracker.start_request()

    history.append(
        {
            "role": "user",
            "content": question,
        }
    )

    # Track total AI time and tokens across all API calls
    total_ai_start = time.time() if metrics_tracker else None
    total_input_tokens = 0
    total_output_tokens = 0

    response = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_INSTRUCTIONS,
        input=history,
        tools=TOOLS,
        parallel_tool_calls=False,
        store=False,
    )

    if metrics_tracker and hasattr(response, 'usage') and response.usage:
        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

    while True:
        # Keep every model output item so later turns retain the full context.
        history.extend(response.output)

        function_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            if metrics_tracker:
                total_ai_time = (time.time() - total_ai_start) * 1000
                metrics_tracker.current_request_metrics.ai_time_ms = total_ai_time
                metrics_tracker.current_request_metrics.input_tokens = total_input_tokens
                metrics_tracker.current_request_metrics.output_tokens = total_output_tokens
                metrics_tracker.current_request_metrics.total_tokens = total_input_tokens + total_output_tokens
                metrics_tracker.current_request_metrics.estimated_cost_usd = calculate_cost(
                    MODEL, total_input_tokens, total_output_tokens
                )
                metrics_tracker.current_request_metrics.model = MODEL
                metrics_tracker.end_request(MODEL)
            return response.output_text

        for function_call in function_calls:
            arguments = json.loads(function_call.arguments)

            if metrics_tracker:
                metrics_tracker.start_tool_call()

            try:
                tool_result = call_wms_tool(
                    function_call.name,
                    arguments,
                )
            except Exception:
                tool_result = {
                    "status": "ERROR",
                    "message": (
                        "Warehouse data could not be retrieved. "
                        "Please try again."
                    ),
                }

            if metrics_tracker:
                metrics_tracker.end_tool_call()

            # For knowledge retrieval, format the context for AI consumption
            tool_result_for_ai = tool_result
            if function_call.name == "retrieve_knowledge":
                if tool_result.get("status") == "FOUND" and "formatted_context" in tool_result:
                    # Use formatted context for the AI response
                    tool_result_for_ai = tool_result["formatted_context"]
                else:
                    tool_result_for_ai = "No relevant knowledge base documents found."

            if tool_trace is not None:
                trace_entry = {
                    "tool": function_call.name,
                    "arguments": arguments,
                    "status": tool_result.get("status", "COMPLETED"),
                }

                if function_call.name == "investigate_order_shortage":
                    trace_entry["workflow_trace"] = tool_result.get("workflow_trace", [],)

                if function_call.name == "retrieve_knowledge":
                    # Add chunk count to trace for display
                    if tool_result.get("status") == "FOUND":
                        trace_entry["chunk_count"] = tool_result.get("chunk_count", 0)

                tool_trace.append(trace_entry)

            history.append(
                {
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": json.dumps(tool_result_for_ai),
                }
            )

        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_INSTRUCTIONS,
            input=history,
            tools=TOOLS,
            parallel_tool_calls=False,
            store=False,
        )

        if metrics_tracker and hasattr(response, 'usage') and response.usage:
            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens


def main() -> None:
    client = OpenAI()
    history = []
    metrics_tracker = MetricsTracker()

    print("WarehouseAI chat is ready.")
    print("Type 'exit' or 'quit' to end the chat.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("WarehouseAI: Goodbye.")
            
            # Print session summary
            summary = metrics_tracker.get_session_summary()
            if summary["total_requests"] > 0:
                print("\n" + "="*50)
                print("SESSION METRICS")
                print("="*50)
                print(f"Total requests: {summary['total_requests']}")
                print(f"Total time: {format_time_ms(summary['total_latency_ms'])}")
                print(f"AI time: {format_time_ms(summary['total_ai_time_ms'])}")
                print(f"Tool time: {format_time_ms(summary['total_tool_time_ms'])}")
                print(f"Total tokens: {summary['total_tokens']:,}")
                print(f"Input tokens: {summary['total_input_tokens']:,}")
                print(f"Output tokens: {summary['total_output_tokens']:,}")
                print(f"Total cost: {format_cost_usd(summary['total_cost_usd'])}")
                print(f"Avg latency: {format_time_ms(summary['avg_latency_ms'])}")
                print("="*50)
            
            break

        if not question:
            continue

        try:
            answer = run_chat_turn(client, history, question, metrics_tracker=metrics_tracker)
            print(f"\nWarehouseAI: {answer}\n")

        except Exception as error:
            print(f"\nWarehouseAI: Unable to complete the request: {error}\n")


if __name__ == "__main__":
    main()