from src.db import get_connection

def get_order_details(order_number: str) -> dict:
    """
    Return the basic line-level details for an order.
    Uses the same confirmed order table/field names as the allocation tool.
    """

    query = """
        SELECT
            op_order_number,
            op_order_position,
            op_order_item,
            op_order_quantity,
            COALESCE(op_allocated_quantity, 0) AS allocated_quantity
        FROM order_position_details
        WHERE op_order_number = %(order_number)s
        ORDER BY op_order_position;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, {"order_number": order_number})
            rows = cursor.fetchall()

    if not rows:
        return {
            "order_number": order_number,
            "status": "NOT_FOUND",
            "lines": [],
        }

    lines = []

    for row in rows:
        (
            order_number,
            position,
            item_id,
            requested_quantity,
            allocated_quantity,
        ) = row

        lines.append(
            {
                "position": position,
                "item_id": item_id,
                "requested_quantity": float(requested_quantity),
                "allocated_quantity": float(allocated_quantity),
            }
        )

    return {
        "order_number": order_number,
        "status": "FOUND",
        "lines": lines,
    }

def get_order_allocation(order_number: str) -> dict:
    """
    Return allocation and inventory availability for every line in an order.

    Assumes these tables and columns:
      - order_position_details
      - inventory_details

    Update `inventory_details` below if your inventory table has a different name.
    """

    query = """
        WITH order_lines AS (
            SELECT
                op_order_number,
                op_order_position,
                op_order_item,
                op_order_quantity AS requested_quantity,
                COALESCE(op_allocated_quantity, 0) AS order_allocated_quantity
            FROM order_position_details
            WHERE op_order_number = %(order_number)s
        ),
        inventory_by_item AS (
            SELECT
                iv_item_id,
                COALESCE(SUM(iv_physical_quantity), 0) AS physical_quantity,
                COALESCE(SUM(iv_allocated_quantity), 0) AS inventory_allocated_quantity,
                COALESCE(SUM(iv_blocked_quantity), 0) AS blocked_quantity,
                COALESCE(SUM(iv_available_quantity), 0) AS available_quantity
            FROM inventory_details
            GROUP BY iv_item_id
        )
        SELECT
            ol.op_order_number,
            ol.op_order_position,
            ol.op_order_item,
            ol.requested_quantity,
            ol.order_allocated_quantity,
            COALESCE(inv.physical_quantity, 0) AS physical_quantity,
            COALESCE(inv.inventory_allocated_quantity, 0) AS inventory_allocated_quantity,
            COALESCE(inv.blocked_quantity, 0) AS blocked_quantity,
            COALESCE(inv.available_quantity, 0) AS available_quantity,
            GREATEST(
                ol.requested_quantity - ol.order_allocated_quantity,
                0
            ) AS allocation_shortage
        FROM order_lines ol
        LEFT JOIN inventory_by_item inv
            ON inv.iv_item_id = ol.op_order_item
        ORDER BY ol.op_order_position;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, {"order_number": order_number})
            rows = cursor.fetchall()

    if not rows:
        return {
            "order_number": order_number,
            "status": "NOT_FOUND",
            "items": [],
        }

    items = []
    has_shortage = False

    for row in rows:
        (
            _order_number,
            position,
            item_id,
            requested,
            allocated,
            physical,
            inventory_allocated,
            blocked,
            available,
            shortage,
        ) = row

        if shortage > 0:
            has_shortage = True

        items.append(
            {
                "position": position,
                "item_id": item_id,
                "requested": float(requested),
                "allocated": float(allocated),
                "physical": float(physical),
                "inventory_allocated": float(inventory_allocated),
                "blocked": float(blocked),
                "available": float(available),
                "shortage": float(shortage),
            }
        )

    return {
        "order_number": order_number,
        "status": "PARTIAL" if has_shortage else "FULLY_ALLOCATED",
        "items": items,
    }

def get_item_inventory(item_id: str) -> dict:
    """
    Return the total inventory position for one item across all inventory records.
    Reuse the inventory table and field names that already work in
    get_order_allocation().
    """

    query = """
        SELECT
            iv_item_id,
            COALESCE(SUM(iv_physical_quantity), 0) AS physical_quantity,
            COALESCE(SUM(iv_allocated_quantity), 0) AS allocated_quantity,
            COALESCE(SUM(iv_blocked_quantity), 0) AS blocked_quantity,
            COALESCE(SUM(iv_available_quantity), 0) AS available_quantity
        FROM inventory_details
        WHERE iv_item_id = %(item_id)s
        GROUP BY iv_item_id;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, {"item_id": item_id})
            row = cursor.fetchone()

    if not row:
        return {
            "item_id": item_id,
            "status": "NOT_FOUND",
        }

    (
        returned_item_id,
        physical,
        allocated,
        blocked,
        available,
    ) = row

    return {
        "item_id": returned_item_id,
        "status": "FOUND",
        "physical": float(physical),
        "allocated": float(allocated),
        "blocked": float(blocked),
        "available": float(available),
    }

def get_movements(item_id: str, limit: int = 20) -> dict:
    """
    Return the most recent warehouse movements for one item.

    A movement can represent a receipt, allocation, pick, transfer,
    adjustment, block, or another WMS event.
    """

    query = """
        SELECT
            mo_movement_id,
            mo_movement_type,
            mo_movement_status,
            mo_movement_item,
            mo_movement_quantity,
            mo_movement_quantity_unit,

            mo_movement_from_entry_area,
            mo_movement_from_location_id,
            mo_movement_from_aisle_number,
            mo_movement_from_rack_number,
            mo_movement_from_bin_hor,
            mo_movement_from_bin_ver,

            mo_movement_to_location_id,
            mo_movement_to_aisle_number,
            mo_movement_to_rack_number,
            mo_movement_to_bin_hor,
            mo_movement_to_bin_ver,
            mo_movement_to_exit_area,

            mo_movement_date,
            mo_movement_time,
            mo_created_at
        FROM movement_details
        WHERE mo_movement_item = %(item_id)s
        ORDER BY
            mo_movement_date DESC,
            mo_movement_time DESC,
            mo_movement_id DESC
        LIMIT %(limit)s;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                {
                    "item_id": item_id,
                    "limit": limit,
                },
            )
            rows = cursor.fetchall()

    movements = []

    for row in rows:
        (
            movement_id,
            movement_type,
            movement_status,
            returned_item_id,
            quantity,
            quantity_unit,
            from_entry_area,
            from_location_id,
            from_aisle,
            from_rack,
            from_bin_horizontal,
            from_bin_vertical,
            to_location_id,
            to_aisle,
            to_rack,
            to_bin_horizontal,
            to_bin_vertical,
            to_exit_area,
            movement_date,
            movement_time,
            created_at,
        ) = row

        movements.append(
            {
                "movement_id": movement_id,
                "movement_type": movement_type,
                "movement_status": movement_status,
                "item_id": returned_item_id,
                "quantity": float(quantity),
                "unit": quantity_unit,
                "from_location": {
                    "entry_area": from_entry_area,
                    "location_id": from_location_id,
                    "aisle": from_aisle,
                    "rack": from_rack,
                    "bin_horizontal": from_bin_horizontal,
                    "bin_vertical": from_bin_vertical,
                },
                "to_location": {
                    "location_id": to_location_id,
                    "aisle": to_aisle,
                    "rack": to_rack,
                    "bin_horizontal": to_bin_horizontal,
                    "bin_vertical": to_bin_vertical,
                    "exit_area": to_exit_area,
                },
                "movement_date": str(movement_date),
                "movement_time": str(movement_time),
                "created_at": str(created_at),
            }
        )

    return {
        "item_id": item_id,
        "status": "FOUND" if movements else "NO_MOVEMENTS",
        "movement_count": len(movements),
        "movements": movements,
    }

def get_inventory(limit: int = 50) -> dict:
    """
    Return an item-level inventory overview.

    Inventory records are aggregated by item, so an item stored across
    multiple locations appears as one summary record.
    """

    query = """
        SELECT
            iv_item_id,
            COALESCE(SUM(iv_physical_quantity), 0) AS physical_quantity,
            COALESCE(SUM(iv_allocated_quantity), 0) AS allocated_quantity,
            COALESCE(SUM(iv_blocked_quantity), 0) AS blocked_quantity,
            COALESCE(SUM(iv_available_quantity), 0) AS available_quantity
        FROM inventory_details
        GROUP BY iv_item_id
        ORDER BY available_quantity ASC, iv_item_id ASC
        LIMIT %(limit)s;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, {"limit": limit})
            rows = cursor.fetchall()

    items = []

    for row in rows:
        (
            item_id,
            physical,
            allocated,
            blocked,
            available,
        ) = row

        items.append(
            {
                "item_id": item_id,
                "physical": float(physical),
                "allocated": float(allocated),
                "blocked": float(blocked),
                "available": float(available),
            }
        )

    return {
        "status": "FOUND",
        "item_count": len(items),
        "items": items,
    }

