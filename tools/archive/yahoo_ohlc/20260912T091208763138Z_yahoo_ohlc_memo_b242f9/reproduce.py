"""Offline, read-only reanalysis of preserved Yahoo evidence. No network requests."""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "Context.md").exists())
PROBE = ROOT / "data/raw/probes/20260912T063021795259Z_99d695f0"
DIAG = ROOT / "data/raw/probes/20260912T084033463809Z_yahoo_diagnostic_b09941"
PRICE = ["Open", "High", "Low", "Close", "Adj Close"]
CASES = {
    "KC_F": ["2025-03-06", "2024-05-02", "2024-09-18", "2025-03-19", "2025-05-19", "2025-09-15"],
    "BRL_X": ["2024-01-01", "2024-07-29", "2024-11-06", "2024-12-27"],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def read_csv(path):
    # round_trip avoids introducing a second decimal-to-binary rounding difference.
    return pd.read_csv(path, float_precision="round_trip")


def same_prices(left, right):
    return bool(np.allclose(left[PRICE].to_numpy(float), right[PRICE].to_numpy(float),
                            rtol=0, atol=1e-12, equal_nan=True))


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    checks = []
    inputs = []
    for manifest_path in [PROBE / "system/manifest.json", DIAG / "manifest.json"]:
        manifest = json.loads(manifest_path.read_text())
        for item in manifest["artifacts"]:
            path = ROOT / item["path"]
            actual = sha(path)
            assert actual == item["sha256"], f"Input hash changed: {item['path']}"
            inputs.append({"path": item["path"], "sha256": actual, "bytes": path.stat().st_size,
                           "verified_against": str(manifest_path.relative_to(ROOT))})
        checks.append({"manifest": str(manifest_path.relative_to(ROOT)),
                       "verified_artifacts": len(manifest["artifacts"])})
    dump(output / "input_integrity.json", {"checks": checks, "artifacts": inputs})
    request_log = json.loads((DIAG / "requests.json").read_text())
    summaries, selected, contexts, all_violations, metadata = [], [], [], [], []
    for number, name in enumerate(CASES, 1):
        payload = json.loads((DIAG / f"chart_response_{number}.json").read_text())
        result = payload["chart"]["result"][0]
        meta = result["meta"]
        quote = result["indicators"]["quote"][0]
        raw = pd.DataFrame({col: quote[col.lower()] for col in PRICE[:4]})
        raw["Adj Close"] = result["indicators"]["adjclose"][0]["adjclose"]
        raw["Volume"] = quote["volume"]
        utc = pd.to_datetime(result["timestamp"], unit="s", utc=True)
        local = utc.tz_convert(meta["exchangeTimezoneName"])
        dates = local.strftime("%Y-%m-%d").tolist()
        raw.insert(0, "observation_date", dates)
        raw["timestamp"] = result["timestamp"]
        raw["timestamp_utc"] = utc.astype(str)
        raw["timestamp_exchange_local"] = local.astype(str)
        raw["source"] = "Yahoo chart preserved HTTP response"
        raw["source_path"] = str((DIAG / f"chart_response_{number}.json").relative_to(ROOT))
        raw["source_retrieved_at"] = request_log[number - 1]["retrieved_at"]
        raw["symbol"] = meta["symbol"]
        raw["unit"] = "US cents/lb" if name == "KC_F" else "BRL per USD"
        response_row_count = len(raw)
        response_volume_null = int(raw.Volume.isna().sum())
        in_scope = raw.observation_date.between("2023-12-31", "2025-12-31")
        raw.loc[~in_scope].to_csv(output / f"{name}_outside_approved_period.csv", index=False)
        raw = raw.loc[in_scope].reset_index(drop=True)
        local = local[in_scope.to_numpy()]
        dates = raw.observation_date.tolist()
        assert len(set(dates)) == len(dates)
        representations = {
            "diagnostic_library_csv": read_csv(DIAG / f"{name}_library_return.csv"),
            "probe_library_csv": read_csv(PROBE / f"library_return/yahoo/{name}.csv"),
            "probe_validation_csv": read_csv(PROBE / f"validation/market_{name}.csv"),
            # Local provenance and manifest checked before loading this trusted pickle.
            "probe_library_pickle": pd.read_pickle(PROBE / f"library_return/yahoo/{name}.pkl").reset_index(),
        }
        comparisons = {}
        for label, frame in representations.items():
            date_col = "observation_date" if "observation_date" in frame else "Date"
            actual_dates = frame[date_col].astype(str).str[:10].tolist()
            assert actual_dates == dates, f"Date mismatch: {name}/{label}"
            assert same_prices(raw, frame), f"Price mismatch: {name}/{label}"
            assert np.array_equal(raw["Volume"].fillna(0), frame["Volume"])
            comparisons[label] = {"rows": len(frame), "price_equal": True, "dates_equal": True,
                                  "volume_equals_raw_after_null_to_zero": True}
            if date_col == "Date":
                instants = pd.to_datetime(frame[date_col], format="mixed", utc=True)
                original_instants = pd.to_datetime(raw.timestamp, unit="s", utc=True)
                comparisons[label]["timestamp_instant_changed_rows"] = int((instants != original_instants).sum())
        valid = raw[PRICE[:4]].notna().all(axis=1)
        raw["valid_ohlc"] = valid
        for col in ["Open", "Close"]:
            below, above = valid & (raw[col] < raw.Low), valid & (raw[col] > raw.High)
            raw[f"{col.lower()}_direction"] = np.select([~valid, below, above], ["missing", "below", "above"], default="inside")
            raw[f"{col.lower()}_signed_gap"] = np.where(~valid, np.nan, np.where(below, raw[col]-raw.Low, np.where(above, raw[col]-raw.High, 0)))
        bad = valid & ((raw.open_direction != "inside") | (raw.close_direction != "inside") | (raw.High < raw.Low))
        raw["ohlc_violation"] = bad
        raw["close_gap_pct_of_boundary"] = np.where(valid, 100 * raw.close_signed_gap / np.where(raw.close_signed_gap < 0, raw.Low, raw.High), np.nan)
        prior_bad = read_csv(DIAG / f"{name}_ohlc_violations.csv")
        prior_dates = prior_bad.iloc[:, 0].astype(str).str[:10].tolist()
        assert prior_dates == raw.loc[bad, "observation_date"].tolist()
        assert same_prices(raw.loc[bad], prior_bad)
        volume = raw.loc[bad, "Volume"]
        good_volume = raw.loc[valid & ~bad, "Volume"]
        within_100 = valid & raw.Volume.le(100)
        summaries.append({
            "symbol": meta["symbol"], "response_rows": response_row_count,
            "response_volume_null": response_volume_null, "outside_approved_period": response_row_count-len(raw),
            "rows": len(raw), "valid_ohlc": int(valid.sum()),
            "missing_ohlc_rows": int((~valid).sum()), "duplicates": int(raw.observation_date.duplicated().sum()),
            "observed_start": dates[0], "observed_end": dates[-1], "anomalies": int(bad.sum()),
            "high_below_low": int((valid & (raw.High < raw.Low)).sum()),
            "open_below": int((raw.open_direction == "below").sum()), "open_above": int((raw.open_direction == "above").sum()),
            "close_below": int((raw.close_direction == "below").sum()), "close_above": int((raw.close_direction == "above").sum()),
            "raw_volume_null": int(raw.Volume.isna().sum()), "raw_volume_zero": int(raw.Volume.eq(0).sum()),
            "library_volume_null": int(representations["probe_library_csv"].Volume.isna().sum()),
            "library_volume_zero": int(representations["probe_library_csv"].Volume.eq(0).sum()),
            "bad_volume_null": int(volume.isna().sum()), "bad_volume_zero": int(volume.eq(0).sum()),
            "bad_volume_min": float(volume.min()), "bad_volume_median": float(volume.median()), "bad_volume_max": float(volume.max()),
            "other_valid_volume_median": float(good_volume.median()),
            "bad_volume_le100": int(volume.le(100).sum()), "bad_volume_le1000": int(volume.le(1000).sum()),
            "valid_volume_le100": int(within_100.sum()), "valid_volume_le100_without_violation": int((within_100 & ~bad).sum()),
            "valid_high_equals_low": int((valid & raw.High.eq(raw.Low)).sum()),
            "bad_high_equals_low": int((bad & raw.High.eq(raw.Low)).sum()),
            "max_close_abs_gap": float(raw.loc[bad, "close_signed_gap"].abs().max()),
            "min_close_abs_gap": float(raw.loc[bad, "close_signed_gap"].abs().min()),
            "valid_open_equals_close": int((valid & raw.Open.eq(raw.Close)).sum()),
            "bad_open_equals_close": int((bad & raw.Open.eq(raw.Close)).sum()),
            "close_equals_adj_close": bool(np.allclose(raw.Close, raw["Adj Close"], rtol=0, atol=0, equal_nan=True)),
            "timestamp_exchange_clock_counts": local.strftime("%H:%M:%S").value_counts().to_dict(),
            "comparisons": comparisons,
        })
        selected.append(raw.set_index("observation_date").loc[CASES[name]].reset_index())
        for day in CASES[name]:
            index = dates.index(day)
            part = raw.iloc[max(0, index-1):index+2].copy()
            part.insert(0, "case_date", day)
            contexts.append(part)
        all_violations.append(raw.loc[bad])
        raw.to_csv(output / f"{name}_diagnostic_rows.csv", index=False)
        old_meta = json.loads((PROBE / f"library_return/yahoo/{name}_metadata.json").read_text())
        metadata.append({"symbol": meta["symbol"], "chart_meta": meta,
                         "original_history_metadata_type": type(old_meta.get("history_metadata")).__name__,
                         "original_quote_metadata_type": type(old_meta.get("quote_metadata")).__name__})
    for name, frames in [("selected_cases", selected), ("neighbor_context", contexts), ("all_violations", all_violations)]:
        pd.concat(frames, ignore_index=True).to_csv(output / f"{name}.csv", index=False)
    dump(output / "summary.json", summaries)
    dump(output / "metadata_review.json", metadata)
    dump(output / "environment.json", {"python": sys.version, "executable": sys.executable,
         "platform": platform.platform(), "machine": platform.machine(),
         "packages": {p: importlib.metadata.version(p) for p in ["pandas", "numpy", "yfinance", "requests", "curl_cffi"]},
         "analyzed_at": datetime.now(timezone.utc).isoformat(), "network_requests": 0})
    print(json.dumps({"output": str(output), "input_hashes_verified": len(inputs),
                      "counts": [{k: r[k] for k in ["symbol", "rows", "anomalies", "open_below", "open_above", "close_below", "close_above"]} for r in summaries]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New directory; existing directories are rejected")
    main(parser.parse_args().output.resolve())
