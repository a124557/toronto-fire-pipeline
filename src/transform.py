#!/usr/bin/env python3
"""Run the SQL transform against the local DuckDB warehouse."""
from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "pipeline.duckdb"
SQL_PATH = ROOT / "sql" / "transform.sql"


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"missing db; run ingest first: {DB_PATH}")
    sql = SQL_PATH.read_text()
    con = duckdb.connect(str(DB_PATH))
    con.execute(sql)
    print("transform tables:")
    for name in ("fire_incidents_by_ward_month", "fire_incidents_top_types"):
        n = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        print(f"  {name}: {n} rows")
        rows = con.execute(f"SELECT * FROM {name} LIMIT 5").fetchall()
        cols = [d[0] for d in con.description]
        print("  columns:", ", ".join(cols))
        for row in rows:
            print("   ", row)
        print()
    con.close()


if __name__ == "__main__":
    main()
