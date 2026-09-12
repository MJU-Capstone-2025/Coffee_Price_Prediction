"""Read-only legacy inventory; no imports or execution of notebook code."""

import csv
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "google_colab": r"google\.colab",
    "drive_mount": r"drive\.mount\s*\(",
    "content_path": r"/content(?:/|\b)",
    "cuda": r"cuda|CUDA",
    "shell_pip": r"(?m)^\s*[!%]pip\s+install\b",
    "bare_pip": r"(?m)^\s*pip\s+install\b",
}


def notebook_inventory(path):
    notebook = json.loads(path.read_text())
    findings = {}
    for name, pattern in PATTERNS.items():
        findings[name] = {
            "source_cells": [
                i for i, cell in enumerate(notebook["cells"], 1)
                if cell["cell_type"] == "code"
                and re.search(pattern, "".join(cell.get("source", [])))
            ],
            "output_cells": [
                i for i, cell in enumerate(notebook["cells"], 1)
                if re.search(pattern, json.dumps(cell.get("outputs", [])))
            ],
        }
    return {"cell_numbering": "1-based, including markdown", "findings": findings}


def csv_inventory(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        fields = reader.fieldnames
    dates = [date.fromisoformat(row["Date"]) for row in rows]
    key_fields = ["Date", "locationName"] if "locationName" in fields else ["Date"]
    keys = [tuple(row[field] for field in key_fields) for row in rows]
    grouped_dates = {}
    for row, day in zip(rows, dates):
        grouped_dates.setdefault(row.get("locationName", "all"), []).append(day)
    return {
        "rows": len(rows),
        "columns": len(fields),
        "fields": fields,
        "date_min": min(dates).isoformat(),
        "date_max": max(dates).isoformat(),
        "empty_cells": sum(value in ("", None) for row in rows for value in row.values()),
        "duplicate_rows": len(rows) - len({tuple(row.values()) for row in rows}),
        "inspection_key_only": key_fields,
        "duplicate_keys": len(keys) - len(set(keys)),
        "date_sorted_global": dates == sorted(dates),
        "date_sorted_per_location": all(value == sorted(value) for value in grouped_dates.values()),
        "location_count": len(grouped_dates) if "locationName" in fields else None,
        "time_metadata_present": [
            field for field in fields
            if field in {"published_at", "ingested_at", "available_at", "availability_basis", "vintage"}
        ],
    }


def main():
    paths = sorted(
        path for folder in ("data", "data_code", "model_code", "old_code", "docs/old_docs")
        for path in (ROOT / folder).rglob("*") if path.is_file()
    )
    output = {
        "baseline_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "scope": "read-only file integrity and mechanical quality; no relationship EDA or model execution",
        "sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths
        },
        "notebooks": {
            str(path.relative_to(ROOT)): notebook_inventory(path)
            for path in paths if path.suffix == ".ipynb"
        },
        "csv": {
            str(path.relative_to(ROOT)): csv_inventory(path)
            for path in paths if path.suffix == ".csv"
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
