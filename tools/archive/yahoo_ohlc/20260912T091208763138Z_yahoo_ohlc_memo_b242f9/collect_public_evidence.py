"""Bounded public-document retrieval plus two eligible BRL hourly probes; no auth."""
import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

DOCUMENTS = [
    ("ice_coffee_spec", "https://www.ice.com/products/15/Coffee-C-Futures", "html"),
    ("ice_trading_rules", "https://www.ice.com/publicdocs/rulebooks/futures_us/4_Trading.pdf", "pdf"),
    ("ice_settlement_window_2018", "https://www.ice.com/publicdocs/futures_us/exchange_notices/ICE_Futures_US_KC_ArbBlocks20181207.pdf", "pdf"),
    ("ice_report_center", "https://www.ice.com/report-center", "html"),
    ("ice_expiry_calendar", "https://www.ice.com/expiry-calendar", "html"),
    ("yfinance_history_docs", "https://ranaroussi.github.io/yfinance/reference/yfinance.price_history.html", "html"),
    ("yfinance_repair_docs", "https://ranaroussi.github.io/yfinance/advanced/price_repair.html", "html"),
]


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    records = []
    session = requests.Session()
    # No .env, cookie export, authentication or redirect chasing in this diagnostic.
    for name, url, extension in DOCUMENTS:
        retrieve(session, records, output, name, url, {}, extension)
    blocked = False
    for day in ["2024-11-06", "2024-12-27"]:
        if blocked:
            records.append({"dataset_id": day, "request_status": "not_requested_after_access_limit"})
            continue
        start = datetime.fromisoformat(day).replace(tzinfo=timezone.utc)
        parameters = {"period1": int(start.timestamp()), "period2": int((start + timedelta(days=1)).timestamp()),
                      "interval": "60m", "includePrePost": "false"}
        rec = retrieve(session, records, output, "BRL_X_60m_" + day,
                       "https://query2.finance.yahoo.com/v8/finance/chart/BRL=X", parameters, "json")
        blocked = rec.get("http_status") in [401, 403, 429]
    (output / "requests.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps([{k: r.get(k) for k in ["dataset_id", "request_status", "http_status", "bytes"]} for r in records], indent=2))


def retrieve(session, records, output, name, url, parameters, extension):
    record = {"dataset_id": name, "method": "GET", "endpoint": url, "parameters": parameters,
              "requested_at": datetime.now(timezone.utc).isoformat(), "timeout_seconds": 25,
              "max_attempts": 2, "redirects_followed": False, "authentication": "none"}
    for attempt in range(1, 3):
        try:
            response = session.get(url, params=parameters, timeout=25, allow_redirects=False)
            content = response.content
            actual_extension = extension
            if extension == "json" and "json" not in response.headers.get("Content-Type", "").lower():
                actual_extension = "txt"
            target = output / f"{name}.{actual_extension}"
            target.write_bytes(content)
            record.update({"attempts": attempt, "retrieved_at": datetime.now(timezone.utc).isoformat(),
                           "request_status": "success" if response.status_code == 200 else "http_failure",
                           "http_status": response.status_code, "content_type": response.headers.get("Content-Type"),
                           "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest(), "artifact_path": target.name})
            break
        except requests.exceptions.Timeout:
            record.update({"attempts": attempt, "request_status": "timeout", "error_type": "Timeout"})
        except requests.exceptions.RequestException as exc:
            # Never emit an exception message containing a prepared URL or headers.
            record.update({"attempts": attempt, "request_status": "network_failure", "error_type": type(exc).__name__})
            break
    records.append(record)
    (output / "requests.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    main(parser.parse_args().output.resolve())
