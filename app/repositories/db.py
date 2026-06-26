"""
Database connection helper.

Reads DATABASE_URL from the environment.
Used exclusively by repository classes — never by controllers.
"""

import os
import sqlite3
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent  # project root

def _resolve_db_path() -> str:
    raw = os.environ.get("DATABASE_URL", "data/app.db")
    # Strip optional sqlite:/// prefix
    path_str = raw.replace("sqlite:///", "")
    return str(_ROOT / path_str)


def get_connection() -> sqlite3.Connection:
    """Return a new sqlite3 connection with row_factory set to Row."""
    conn = sqlite3.connect(_resolve_db_path())
    conn.row_factory = sqlite3.Row
    return conn
