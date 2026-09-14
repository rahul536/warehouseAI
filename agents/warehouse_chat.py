import json

from openai import OpenAI

from agents.warehouse_agent import (
    MODEL,
    SYSTEM_INSTRUCTIONS,
    TOOLS,
    call_wms_tool,
)


def run_chat_turn(client: OpenAI, history: list, question: str, tool_trace: list | None = None,) -> str:
    """Run one user turn, including any WMS function calls."""

    history.append(
        {
            "role": "user",
            "content": question,
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

    while True:
        # Keep every model output item so later turns retain the full context.
        history.extend(response.output)

        function_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            return response.output_text

        for function_call in function_calls:
            arguments = json.loads(function_call.arguments)

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


def main() -> None:
    client = OpenAI()
    history = []

    print("WarehouseAI chat is ready.")
    print("Type 'exit' or 'quit' to end the chat.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("WarehouseAI: Goodbye.")
            break

        if not question:
            continue

        try:
            answer = run_chat_turn(client, history, question)
            print(f"\nWarehouseAI: {answer}\n")

        except Exception as error:
            print(f"\nWarehouseAI: Unable to complete the request: {error}\n")


if __name__ == "__main__":
    main()