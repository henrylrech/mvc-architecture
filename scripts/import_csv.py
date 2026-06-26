"""
One-time import script: CSV → SQLite.
Run once before starting the app:
    python scripts/import_csv.py

Reads DATABASE_URL env var (default: data/app.db).
"""

import csv
import os
import sqlite3
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CSV_PATH = DATA_DIR / "Matriculados Região Sul.csv"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

raw_url = os.environ.get("DATABASE_URL", "data/app.db")
# Strip optional "sqlite:///" prefix
db_path_str = raw_url.replace("sqlite:///", "")
DB_PATH = ROOT / db_path_str

YEAR_COLUMNS = [str(y) for y in range(2009, 2024)]  # 2009–2023

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_int(val: str) -> int | None:
    """Return int or None for blank/non-numeric values."""
    v = val.strip()
    if v == "" or v is None:
        return None
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


def normalize(text: str) -> str:
    """Strip and normalize whitespace."""
    return " ".join(text.strip().split())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found at {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Apply schema
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    cursor.executescript(schema_sql)
    conn.commit()

    # Clear existing data (idempotent re-run)
    cursor.execute("DELETE FROM enrollments")
    conn.commit()

    insert_sql = """
        INSERT INTO enrollments
            (year, state, city, institution_name, institution_acronym,
             organization_type, administrative_category,
             course_name, course_detail, degree_type, modality, students_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    rows_inserted = 0
    rows_skipped = 0

    with open(CSV_PATH, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=";")
        batch = []

        for raw_row in reader:
            state        = normalize(raw_row.get("Estado", ""))
            city         = normalize(raw_row.get("Cidade", ""))
            ies          = normalize(raw_row.get("IES", ""))
            sigla        = normalize(raw_row.get("Sigla", ""))
            org_type     = normalize(raw_row.get("Organização", ""))
            adm_cat      = normalize(raw_row.get("Categoria Administrativa", ""))
            course       = normalize(raw_row.get("Nome do Curso", ""))
            course_det   = normalize(raw_row.get("Nome Detalhado do Curso", ""))
            degree       = normalize(raw_row.get("Grau", ""))
            modality     = normalize(raw_row.get("Modalidade", ""))

            for year_str in YEAR_COLUMNS:
                raw_val = raw_row.get(year_str, "")
                count = parse_int(raw_val)
                if count is None:
                    rows_skipped += 1
                    continue

                batch.append((
                    int(year_str), state, city, ies, sigla,
                    org_type, adm_cat, course, course_det,
                    degree, modality, count
                ))

                if len(batch) >= 500:
                    cursor.executemany(insert_sql, batch)
                    rows_inserted += len(batch)
                    batch.clear()

        if batch:
            cursor.executemany(insert_sql, batch)
            rows_inserted += len(batch)

    conn.commit()
    conn.close()

    print(f"Import complete.")
    print(f"  Rows inserted : {rows_inserted}")
    print(f"  Cells skipped : {rows_skipped} (blank/null year values)")
    print(f"  Database      : {DB_PATH}")

    # Sanity checks
    conn2 = sqlite3.connect(DB_PATH)
    c2 = conn2.cursor()
    c2.execute("SELECT COUNT(*) FROM enrollments")
    total = c2.fetchone()[0]
    c2.execute("SELECT MIN(year), MAX(year) FROM enrollments")
    yr_min, yr_max = c2.fetchone()
    c2.execute("SELECT COUNT(DISTINCT course_name) FROM enrollments")
    courses = c2.fetchone()[0]
    c2.execute("SELECT COUNT(DISTINCT institution_name) FROM enrollments")
    ies_count = c2.fetchone()[0]
    conn2.close()

    print(f"\nSanity check:")
    print(f"  Total rows    : {total}")
    print(f"  Year range    : {yr_min} – {yr_max}")
    print(f"  Distinct courses: {courses}")
    print(f"  Distinct IES    : {ies_count}")


if __name__ == "__main__":
    main()
