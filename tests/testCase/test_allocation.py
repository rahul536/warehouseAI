import json

from src.wms_tools import get_order_allocation


result = get_order_allocation("ORD10004")

print(json.dumps(result, indent=2))