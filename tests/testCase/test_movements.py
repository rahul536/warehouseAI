import json

from src.wms_tools import get_movements


result = get_movements("ITEM001")

print(json.dumps(result, indent=2))