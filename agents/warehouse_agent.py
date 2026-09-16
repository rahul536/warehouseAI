import argparse
import json
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from openai import OpenAI

from src.wms_tools import (
    get_inventory,
    get_item_inventory,
    get_movements,
    get_order_allocation,
    get_order_details,
)

from agents.shortage_graph import investigate_order_shortage
from ui.core.rag.retrieve import retrieve_knowledge, format_chunks_for_context

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_INSTRUCTIONS = """
You are WarehouseAI, a helpful warehouse operations assistant.

You answer questions using data from two sources:
1. Live WMS database tools (orders, inventory, movements, allocation)
2. Knowledge base documents (SOPs, procedures, logistics documentation)

Use WMS tools for questions about:
- Orders, order details, order allocation
- Inventory levels, item inventory, blocked stock
- Warehouse movements, recent activity
- Shortage investigation and root-cause analysis

Use the knowledge base tool for questions about:
- Standard operating procedures (SOPs)
- Warehouse processes and workflows
- Logistics procedures and requirements
- Equipment specifications and maintenance
- Documentation and reference materials

Rules:
- Never invent warehouse data or knowledge base content.
- Clearly state when a tool returns NOT_FOUND, NO_MOVEMENTS, or NO_RESULTS.
- Explain quantities and shortages in simple operational language.
- For allocation shortages, distinguish physical stock, allocated stock,
  blocked stock, and available stock.
- All available tools are read-only. Do not claim to change warehouse data.
- If the user asks why an order is partially allocated, asks to investigate a
  shortage, or asks for a root-cause analysis, use investigate_order_shortage.
- When using knowledge base information, cite the source document and location.
"""

TOOLS = [
    {
        "type": "function",
        "name": "get_order_details",
        "description": "Get the requested and allocated quantities for every line in an order.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "Warehouse order number, for example ORD10004.",
                }
            },
            "required": ["order_number"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_order_allocation",
        "description": "Get allocation status, inventory availability, blocked stock, and shortages for an order.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "Warehouse order number, for example ORD10004.",
                }
            },
            "required": ["order_number"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_item_inventory",
        "description": "Get physical, allocated, blocked, and available inventory for one item.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "Item identifier, for example ITEM014.",
                }
            },
            "required": ["item_id"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_inventory",
        "description": "Get an overview of inventory for multiple items, sorted by lowest availability.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Maximum number of inventory items to return.",
                }
            },
            "required": ["limit"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_movements",
        "description": "Get recent warehouse movements for one item.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "Item identifier, for example ITEM014.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Maximum number of movements to return.",
                },
            },
            "required": ["item_id", "limit"],
            "additionalProperties": False,
        },
    },
        {
        "type": "function",
        "name": "investigate_order_shortage",
        "description": (
            "Investigate why an order is partially allocated. "
            "This runs a controlled workflow: allocation check, shortage-item "
            "identification, inventory check, recent-movement lookup, and summary."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "Warehouse order number, for example ORD10004.",
                }
            },
            "required": ["order_number"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "retrieve_knowledge",
        "description": (
            "Search the knowledge base for SOPs, procedures, logistics documentation, "
            "and warehouse reference materials. Use this for questions about processes, "
            "workflows, equipment specifications, and documentation."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for knowledge base documents.",
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
]


def call_wms_tool(tool_name: str, arguments: dict) -> dict:
    """Route a model-selected function call to the matching WMS tool."""

    if tool_name == "get_order_details":
        return get_order_details(arguments["order_number"])

    if tool_name == "get_order_allocation":
        return get_order_allocation(arguments["order_number"])

    if tool_name == "get_item_inventory":
        return get_item_inventory(arguments["item_id"])

    if tool_name == "get_inventory":
        return get_inventory(limit=arguments["limit"])

    if tool_name == "get_movements":
        return get_movements(
            item_id=arguments["item_id"],
            limit=arguments["limit"],
            )
    if tool_name == "investigate_order_shortage":
        return investigate_order_shortage(arguments["order_number"])

    if tool_name == "retrieve_knowledge":
        result = retrieve_knowledge(
            query=arguments["query"],
            n_results=5,  # Default to 5 results
        )
        
        # Add formatted context for easier AI consumption
        if result["status"] == "FOUND":
            result["formatted_context"] = format_chunks_for_context(result["chunks"])
        
        return result

    return {"error": f"Unknown tool requested: {tool_name}"}


def ask_warehouse_ai(question: str) -> str:
    client = OpenAI()

    response = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_INSTRUCTIONS,
        input=question,
        tools=TOOLS,
        parallel_tool_calls=False,
        store=False,
    )

    conversation_items = list(response.output)

    while True:
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
                tool_result = call_wms_tool(function_call.name, arguments)
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

            conversation_items.append(
                {
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": json.dumps(tool_result_for_ai),
                }
            )

        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_INSTRUCTIONS,
            input=conversation_items,
            tools=TOOLS,
            parallel_tool_calls=False,
            store=False,
        )

        conversation_items.extend(response.output)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ask WarehouseAI a warehouse operations question."
    )
    parser.add_argument("question", help="Your warehouse question in quotation marks.")
    args = parser.parse_args()

    answer = ask_warehouse_ai(args.question)

    print("\nWarehouseAI:")
    print(answer)


if __name__ == "__main__":
    main()