import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# Add project root to Python path and load .env
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
load_dotenv(project_root / ".env")

def get_connection():
    """Create a connection to the WarehouseAI PostgreSQL database."""
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )