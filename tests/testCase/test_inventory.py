import json

from src.wms_tools import get_inventory


result = get_inventory(limit=10)

print(json.dumps(result, indent=2))