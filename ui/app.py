import sys
from pathlib import Path

# Add warehouseAI project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import json
import sys

from src.wms_tools import (
    get_inventory,
    get_item_inventory,
    get_movements,
    get_order_allocation,
    get_order_details,
)


def print_result(result: dict) -> None:
    """Display tool output as readable JSON."""
    print(json.dumps(result, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="WarehouseAI WMS database tool console"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available WMS tools",
    )

    order_details = subparsers.add_parser(
        "order-details",
        help="Get an order's line items",
    )
    order_details.add_argument("order_number")

    order_allocation = subparsers.add_parser(
        "order-allocation",
        help="Get allocation and inventory availability for an order",
    )
    order_allocation.add_argument("order_number")

    item_inventory = subparsers.add_parser(
        "item-inventory",
        help="Get the inventory position for one item",
    )
    item_inventory.add_argument("item_id")

    inventory = subparsers.add_parser(
        "inventory",
        help="Get an inventory overview across items",
    )
    inventory.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of items to return (default: 20)",
    )

    movements = subparsers.add_parser(
        "movements",
        help="Get recent movements for one item",
    )
    movements.add_argument("item_id")
    movements.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of movements to return (default: 20)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "order-details":
            result = get_order_details(args.order_number)

        elif args.command == "order-allocation":
            result = get_order_allocation(args.order_number)

        elif args.command == "item-inventory":
            result = get_item_inventory(args.item_id)

        elif args.command == "inventory":
            result = get_inventory(limit=args.limit)

        elif args.command == "movements":
            result = get_movements(args.item_id, limit=args.limit)

        else:
            parser.error("Unknown command.")
            return

        print_result(result)

    except Exception as error:
        print(f"WarehouseAI could not complete the request: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()