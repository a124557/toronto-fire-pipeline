# Toronto Fire Incidents Pipeline (v0)

Small public data-engineering sample: ingest City of Toronto Open Data into DuckDB, then run one SQL transform.

## What it does

```text
Toronto CKAN DataStore  ->  raw_fire_incidents (DuckDB)  ->  ward/month + top types
```

- Source: [Fire Incidents](https://open.toronto.ca/dataset/fire-incidents/) via the CKAN DataStore API (no API key).
- Warehouse: local DuckDB file at `data/pipeline.duckdb`.
- Transform: `sql/transform.sql` builds monthly counts by ward and a top incident-type table.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/ingest.py
python src/transform.py
```
