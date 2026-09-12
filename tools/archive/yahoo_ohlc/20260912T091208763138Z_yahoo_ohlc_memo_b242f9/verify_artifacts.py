"""Verify memo tables, local links, preserved inputs, manifest and private-secret absence."""
import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

import pandas as pd
from dotenv import dotenv_values

RUN = Path(__file__).resolve().parent
ROOT = next(p for p in RUN.parents if (p / "Context.md").exists())
MEMO = ROOT / "docs/reports/yahoo-ohlc-technical-memo.md"
STATUS = ROOT / "docs/STATUS.md"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(report):
    memo = MEMO.read_text()
    cases = pd.read_csv(RUN / "analysis_final/selected_cases.csv", float_precision="round_trip")
    checked_cells = 0
    checked_rows = 0
    for line in memo.splitlines():
        if line.startswith("| 날짜 | Open |"):
            headers = [x.strip() for x in line.strip("|").split("|")]
        elif re.match(r"\| 20\d\d-\d\d-\d\d \| [-\d.]+ \|", line):
            values = [x.strip() for x in line.strip("|").split("|")]
            symbol = "KC=F" if "Volume" in headers else "BRL=X"
            row = cases[(cases.symbol == symbol) & (cases.observation_date == values[0])].iloc[0]
            for header, value in zip(headers[1:], values[1:]):
                column = {"Close signed gap": "close_signed_gap", "Open signed gap": "open_signed_gap"}.get(header, header)
                assert abs(float(value) - float(row[column])) <= 0.00000051, (symbol, values[0], column)
                checked_cells += 1
            checked_rows += 1
    assert checked_rows == 10
    summary = json.loads((RUN / "analysis_final/summary.json").read_text())
    fields = {
        "HTTP 원문 전체 행": lambda r: r["response_rows"],
        "승인 구간 내 행": lambda r: r["rows"],
        "실제 기간 시작": lambda r: r["observed_start"],
        "실제 기간 끝": lambda r: r["observed_end"],
        "유효 OHLC 행": lambda r: r["valid_ohlc"],
        "OHLC 결측 행": lambda r: r["missing_ohlc_rows"],
        "날짜 중복": lambda r: r["duplicates"],
        "High < Low": lambda r: r["high_below_low"],
        "Open 하방 / 상방 이탈": lambda r: f'{r["open_below"]} / {r["open_above"]}',
        "Close 하방 / 상방 이탈": lambda r: f'{r["close_below"]} / {r["close_above"]}',
        "이상 행 합집합": lambda r: r["anomalies"],
        "원문 Volume null: 전체 / 구간 내": lambda r: f'{r["response_volume_null"]} / {r["raw_volume_null"]}',
        "구간 내 원문 Volume 0": lambda r: r["raw_volume_zero"],
        "library Volume null / 0": lambda r: f'{r["library_volume_null"]} / {r["library_volume_zero"]}',
        "이상 행 Volume null / 0": lambda r: f'{r["bad_volume_null"]} / {r["bad_volume_zero"]}',
    }
    aggregate_cells = 0
    for line in memo.splitlines():
        values = [x.strip() for x in line.strip("|").split("|")]
        if values[0] in fields:
            assert values[1:] == [str(fields[values[0]](r)) for r in summary], values[0]
            aggregate_cells += 2
    assert aggregate_cells == 30
    contexts = pd.read_csv(RUN / "analysis_final/neighbor_context.csv", float_precision="round_trip")
    context_cells = 0
    for day in ["2024-09-18", "2025-03-19", "2025-05-19"]:
        rows = contexts[(contexts.symbol == "KC=F") & (contexts.case_date == day)]
        before, current, after = [r for _, r in rows.iterrows()]
        prefix = f'| {day} | {before.observation_date[5:]}: {int(before.Volume)} | {int(current.Volume)} | {after.observation_date[5:]}: {int(after.Volume)} | '
        matching = [line for line in memo.splitlines() if line.startswith(prefix)]
        assert len(matching) == 1, day
        value = float(matching[0].split('|')[-2].strip())
        assert abs(value - (current.High-current.Low)) < 0.00000051
        context_cells += 4
    links = []
    own_status = STATUS.read_text().split("## 문서 정리 — ADR과 작업 기록 분리")[0]
    for document, content in [(MEMO, memo), (STATUS, own_status)]:
        assert all(line == line.rstrip() for line in content.splitlines()), f"Trailing space: {document.name}"
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if target.startswith(("https://", "http://", "#")):
                continue
            path = (document.parent / unquote(target.split('#')[0])).resolve()
            assert path.exists(), f"Missing link: {target}"
            links.append({"document": str(document.relative_to(ROOT)), "target": target})
    manifest = json.loads((RUN / "manifest.json").read_text())
    for item in manifest["artifacts"]:
        path = ROOT / item["path"]
        assert path.stat().st_size == item["bytes"] and sha(path) == item["sha256"], item["path"]
    inputs = json.loads((RUN / "analysis_final/input_integrity.json").read_text())
    for item in inputs["artifacts"]:
        assert sha(ROOT / item["path"]) == item["sha256"], item["path"]
    baseline = json.loads((RUN / "preservation_before.json").read_text())
    unchanged, moved, other = [], [], []
    for rel, expected in baseline.items():
        path = ROOT / rel
        if path.exists() and sha(path) == expected:
            unchanged.append(rel)
        elif rel == "docs/STATUS.md":
            continue
        else:
            destination = ROOT / "data/old_data" / path.name
            if rel.startswith("data/") and destination.exists() and sha(destination) == expected:
                moved.append({"from": rel, "to": str(destination.relative_to(ROOT))})
            else:
                other.append(rel)
    # Known independent edit is reported, never silently accepted as unchanged.
    assert other == ["requirements.txt"], f"Additional concurrent changes: {other}"
    assert len(moved) == 8
    existing_report = "docs/reports/yahoo-ohlc-investigation-2026-09-12.md"
    assert sha(ROOT / existing_report) == baseline[existing_report]
    private_values = [v.encode() for k, v in dotenv_values(ROOT / ".env").items()
                      if v and len(v) >= 8 and re.search(r"KEY|TOKEN|SECRET|PASSWORD", k, re.I)]
    scanned = [p for p in RUN.rglob('*') if p.is_file()] + [MEMO, STATUS]
    for path in scanned:
        data = path.read_bytes()
        assert not any(value in data for value in private_values), f"Private secret found in {path.name}"
        assert not re.search(rb"https?://[^\s\"<>]+[?&](?:api_key|apikey|access_token|crumb)=[^\s\"<>]+", data, re.I), f"Sensitive query URL: {path.name}"
    diff = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, "git diff --check failed"
    result = {"verified_at": datetime.now(timezone.utc).isoformat(), "status": "passed_with_reported_independent_changes",
              "table_rows_checked": checked_rows, "numeric_case_cells_checked": checked_cells,
              "aggregate_cells_checked": aggregate_cells, "context_numeric_cells_checked": context_cells,
              "local_links_checked": len(links), "links": links,
              "manifest_artifacts_checked": len(manifest["artifacts"]), "input_artifacts_checked": len(inputs["artifacts"]),
              "preservation": {"unchanged_paths": len(unchanged), "independently_moved_identical_files": moved,
                               "independent_modified_paths": other, "own_modified_baseline_paths": ["docs/STATUS.md"],
                               "prior_report_unchanged": True, "git_notebook_changes": "See concurrent_changes.json; not changed by this task"},
              "secret_scan": {"files_checked": len(scanned), "private_value_matches": 0, "sensitive_query_urls": 0},
              "git_diff_check_exit_code": diff.returncode,
              "documents": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in [MEMO, STATUS]]}
    if report:
        with report.open("x") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ["links", "documents"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    main(parser.parse_args().report)
