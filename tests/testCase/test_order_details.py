import json

from src.wms_tools import get_order_details


result = get_order_details("ORD10004")

print(json.dumps(result, indent=2))