import json

from src.wms_tools import get_item_inventory


result = get_item_inventory("ITEM014")

print(json.dumps(result, indent=2))