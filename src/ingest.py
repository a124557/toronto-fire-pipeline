#!/usr/bin/env python3
"""Pull Toronto Fire Incidents from the City Open Data CKAN DataStore into DuckDB."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "pipeline.duckdb"
RESOURCE_ID = "fa5c7de5-10f8-41cf-883a-9b30a67c7b56"
API = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/datastore_search"
PAGE = 1000


def fetch_page(offset: int) -> dict:
    qs = urllib.parse.urlencode(
        {"resource_id": RESOURCE_ID, "limit": PAGE, "offset": offset}
    )
    with urllib.request.urlopen(f"{API}?{qs}", timeout=60) as resp:
        payload = json.load(resp)
    if not payload.get("success"):
        raise RuntimeError(f"CKAN error: {payload}")
    return payload["result"]


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    con = duckdb.connect(str(DB_PATH))
    con.execute(
        """
        CREATE TABLE raw_fire_incidents (
            incident_number VARCHAR,
            initial_cad_event_type VARCHAR,
            final_incident_type VARCHAR,
            incident_station_area VARCHAR,
            incident_ward VARCHAR,
            intersection VARCHAR,
            latitude DOUBLE,
            longitude DOUBLE,
            property_use VARCHAR,
            building_status VARCHAR,
            tfs_alarm_time TIMESTAMP,
            tfs_arrival_time TIMESTAMP,
            last_tfs_unit_clear_time TIMESTAMP,
            persons_rescued INTEGER
        )
        """
    )

    offset = 0
    total = None
    inserted = 0
    while True:
        result = fetch_page(offset)
        if total is None:
            total = result.get("total")
            print(f"CKAN total rows: {total}")
        records = result.get("records") or []
        if not records:
            break
        rows = []
        for r in records:
            rows.append(
                (
                    r.get("Incident_Number"),
                    r.get("Initial_CAD_Event_Type"),
                    r.get("Final_Incident_Type"),
                    r.get("Incident_Station_Area"),
                    r.get("Incident_Ward"),
                    r.get("Intersection"),
                    float(r["Latitude"]) if r.get("Latitude") not in (None, "") else None,
                    float(r["Longitude"]) if r.get("Longitude") not in (None, "") else None,
                    r.get("Property_Use"),
                    r.get("Building_Status"),
                    r.get("TFS_Alarm_Time"),
                    r.get("TFS_Arrival_Time"),
                    r.get("Last_TFS_Unit_Clear_Time"),
                    int(r["Persons_Rescued"])
                    if str(r.get("Persons_Rescued") or "").isdigit()
                    else None,
                )
            )
        con.executemany(
            """
            INSERT INTO raw_fire_incidents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        inserted += len(rows)
        offset += len(records)
        print(f"ingested {inserted}" + (f" / {total}" if total else ""))
        if total is not None and offset >= total:
            break
        if len(records) < PAGE:
            break

    count = con.execute("SELECT COUNT(*) FROM raw_fire_incidents").fetchone()[0]
    print(f"done. rows in raw_fire_incidents: {count}")
    print(f"db: {DB_PATH}")
    con.close()


if __name__ == "__main__":
    main()
