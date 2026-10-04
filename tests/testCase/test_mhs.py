import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
import json

from src.wms_tools import get_material_handling


result = get_material_handling(limit=10)

print(json.dumps(result, indent=2))