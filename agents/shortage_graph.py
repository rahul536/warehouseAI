import operator
import sys
from pathlib import Path
from typing import Annotated, Literal, TypedDict

# Add project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from langgraph.graph import END, START, StateGraph

from src.wms_tools import (
    get_item_inventory,
    get_movements,
    get_order_allocation,
)


class ShortageInvestigationState(TypedDict, total=False):
    order_number: str
    allocation: dict
    shortage_items: list[dict]
    item_inventories: dict[str, dict]
    movements: dict[str, dict]
    trace: Annotated[list[str], operator.add]
    summary: str


def safe_tool_call(tool_function, *args, **kwargs) -> dict:
    """Return a safe result if a database lookup fails."""

    try:
        return tool_function(*args, **kwargs)
    except Exception:
        return {
            "status": "ERROR",
            "message": "Warehouse data could not be retrieved.",
        }


def load_allocation(state: ShortageInvestigationState) -> dict:
    order_number = state["order_number"]

    allocation = safe_tool_call(
        get_order_allocation,
        order_number,
    )

    return {
        "allocation": allocation,
        "trace": [
            f"Checked allocation status for order {order_number}."
        ],
    }


def extract_shortages(state: ShortageInvestigationState) -> dict:
    allocation = state["allocation"]

    shortage_items = [
        item
        for item in allocation.get("items", [])
        if item.get("shortage", 0) > 0
    ]

    return {
        "shortage_items": shortage_items,
        "trace": [
            f"Found {len(shortage_items)} order line(s) with an allocation shortage."
        ],
    }


def should_investigate(
    state: ShortageInvestigationState,
) -> Literal["investigate", "complete"]:
    if state.get("shortage_items"):
        return "investigate"

    return "complete"


def inspect_shortage_items(state: ShortageInvestigationState) -> dict:
    inventories = {}

    for item in state["shortage_items"]:
        item_id = item["item_id"]

        inventories[item_id] = safe_tool_call(
            get_item_inventory,
            item_id,
        )

    return {
        "item_inventories": inventories,
        "trace": [
            "Checked the physical, allocated, blocked, and available inventory "
            "for each shortage item."
        ],
    }


def fetch_movements(state: ShortageInvestigationState) -> dict:
    movement_results = {}

    for item in state["shortage_items"]:
        item_id = item["item_id"]

        movement_results[item_id] = safe_tool_call(
            get_movements,
            item_id,
            limit=5,
        )

    return {
        "movements": movement_results,
        "trace": [
            "Retrieved the five most recent movements for each shortage item."
        ],
    }


def summarize(state: ShortageInvestigationState) -> dict:
    allocation = state["allocation"]
    order_number = state["order_number"]

    if allocation.get("status") == "NOT_FOUND":
        return {
            "summary": f"Order {order_number} was not found.",
            "trace": ["Completed investigation."],
        }

    shortage_items = state.get("shortage_items", [])

    if not shortage_items:
        return {
            "summary": (
                f"Order {order_number} has no allocation shortages. "
                "All order lines are fully allocated."
            ),
            "trace": ["Completed investigation."],
        }

    lines = [
        f"Shortage investigation for {order_number}:",
    ]

    inventories = state.get("item_inventories", {})
    movements = state.get("movements", {})

    for item in shortage_items:
        item_id = item["item_id"]
        inventory = inventories.get(item_id, {})
        movement_result = movements.get(item_id, {})

        lines.append(
            f"- {item_id}: requested {item['requested']}, "
            f"allocated {item['allocated']}, shortage {item['shortage']}."
        )

        if inventory.get("status") == "FOUND":
            lines.append(
                f"  Inventory: physical {inventory['physical']}, "
                f"allocated {inventory['allocated']}, "
                f"blocked {inventory['blocked']}, "
                f"available {inventory['available']}."
            )

        if movement_result.get("status") == "FOUND":
            lines.append(
                f"  Recent movements checked: "
                f"{movement_result['movement_count']} record(s)."
            )

    lines.append(
        "Recommended next action: review blocked stock and recent movements "
        "for the shortage item(s)."
    )

    return {
        "summary": "\n".join(lines),
        "trace": ["Completed investigation."],
    }


workflow = StateGraph(ShortageInvestigationState)

workflow.add_node("load_allocation", load_allocation)
workflow.add_node("extract_shortages", extract_shortages)
workflow.add_node("inspect_shortage_items", inspect_shortage_items)
workflow.add_node("fetch_movements", fetch_movements)
workflow.add_node("summarize", summarize)

workflow.add_edge(START, "load_allocation")
workflow.add_edge("load_allocation", "extract_shortages")

workflow.add_conditional_edges(
    "extract_shortages",
    should_investigate,
    {
        "investigate": "inspect_shortage_items",
        "complete": "summarize",
    },
)

workflow.add_edge("inspect_shortage_items", "fetch_movements")
workflow.add_edge("fetch_movements", "summarize")
workflow.add_edge("summarize", END)

shortage_investigation_graph = workflow.compile()

def investigate_order_shortage(order_number: str) -> dict:
    """Run the complete LangGraph shortage-investigation workflow."""

    result = shortage_investigation_graph.invoke(
        {
            "order_number": order_number,
        }
    )

    allocation = result.get("allocation", {})

    return {
        "order_number": order_number,
        "status": allocation.get("status", "ERROR"),
        "summary": result.get("summary", "No investigation summary was produced."),
        "shortage_items": result.get("shortage_items", []),
        "workflow_trace": result.get("trace", []),
    }