"""Local dependency smoke tests. All observations here are synthetic fixtures.

No source adoption, production schema, availability policy, or live API claim.
"""

from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import import_module
from importlib.metadata import distribution
from io import BytesIO, StringIO
import json
import platform
import sys
from threading import Thread
from zipfile import ZipFile

import pytest


@pytest.mark.parametrize("package,module", [
    ("numpy", "numpy"), ("pandas", "pandas"), ("requests", "requests"),
    ("duckdb", "duckdb"), ("pyarrow", "pyarrow"), ("PyYAML", "yaml"),
    ("openpyxl", "openpyxl"), ("yfinance", "yfinance"), ("pytest", "pytest"),
    ("curl_cffi", "curl_cffi"), ("cffi", "cffi"), ("lxml", "lxml.etree"),
    ("protobuf", "google.protobuf"),
])
def test_import_and_compatible_wheel(package, module):
    from packaging.tags import parse_tag, sys_tags

    import_module(module)
    wheel = distribution(package).read_text("WHEEL")
    assert wheel is not None
    wheel_tags = set()
    for line in wheel.splitlines():
        if line.startswith("Tag: "):
            wheel_tags.update(parse_tag(line.removeprefix("Tag: ")))
    assert wheel_tags.intersection(sys_tags()), package


def test_approved_runtime():
    assert sys.implementation.name == "cpython"
    assert sys.version_info[:2] == (3, 14)
    assert sys.prefix != sys.base_prefix
    assert platform.system() == "Darwin"
    assert platform.machine() == "arm64"


def test_parquet_duckdb_roundtrip(tmp_path):
    import duckdb
    import numpy as np
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq

    # Distinct times only test preservation, not a production availability rule.
    frame = pd.DataFrame({
        "code": pd.Series(["083731", "083731"], dtype="string"),
        "observation_date": [date(2020, 1, 1), date(2020, 1, 2)],
        "published_at": pd.to_datetime([None, None], utc=True),
        "ingested_at": pd.to_datetime(["2026-09-12T00:00:00Z"] * 2, utc=True),
        "available_at": pd.to_datetime(["2020-01-03T00:00:00Z", None], utc=True),
        "value": pd.Series([1.25, None], dtype="Float64"),
    })
    path = tmp_path / "synthetic.parquet"
    table = pa.Table.from_pandas(frame, preserve_index=False)
    pq.write_table(table, path)
    assert pq.read_table(path).equals(table)
    restored = pd.read_parquet(path)
    pd.testing.assert_frame_equal(restored, frame)
    np.testing.assert_allclose(restored["value"].dropna().to_numpy(dtype=float), [1.25])
    with duckdb.connect(":memory:") as connection:
        connection.execute("SET TimeZone = 'UTC'")
        rows = connection.execute(
            "SELECT code, value, published_at, available_at FROM read_parquet(?) ORDER BY observation_date",
            [str(path)],
        ).fetchall()
    assert rows[0] == ("083731", 1.25, None, datetime(2020, 1, 3, tzinfo=timezone.utc))
    assert rows[1] == ("083731", None, None, None)


def test_yaml_zip_csv_and_xlsx_parsers():
    import pandas as pd
    import yaml
    from openpyxl import Workbook

    config = yaml.safe_load('code: "083731"\nkind: fixture\n')
    assert config["code"] == "083731"
    payload = "code,date,value\n083731,2020-01-01,1.25\n083731,2020-01-02,.\n"
    archive_bytes = BytesIO()
    with ZipFile(archive_bytes, "w") as archive:
        archive.writestr("synthetic.csv", payload)
    archive_bytes.seek(0)
    with ZipFile(archive_bytes) as archive:
        frame = pd.read_csv(
            StringIO(archive.read("synthetic.csv").decode()),
            dtype={"code": "string"}, na_values=["."],
        )
    assert frame["code"].tolist() == ["083731", "083731"]
    assert pd.isna(frame.loc[1, "value"])
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["code", "value"])
    sheet.append(["083731", 1.25])
    excel_bytes = BytesIO()
    workbook.save(excel_bytes)
    workbook.close()
    excel_bytes.seek(0)
    excel = pd.read_excel(excel_bytes, engine="openpyxl", dtype={"code": "string"})
    assert excel.loc[0, "code"] == "083731"
    assert excel.loc[0, "value"] == 1.25


def test_yfinance_quote_parser_fixture():
    import pandas as pd
    from yfinance.utils import parse_quotes

    # Tests installed parser interoperability, not Yahoo's actual response contract.
    quotes = parse_quotes({
        "timestamp": [1577923200, 1577836800],
        "indicators": {"quote": [{
            "open": [2.0, 1.0], "high": [2.5, 1.5], "low": [1.5, 0.5],
            "close": [2.25, 1.25], "volume": [20, 10],
        }]},
    })
    assert quotes.index.is_monotonic_increasing
    assert quotes["Close"].tolist() == [1.25, 2.25]
    assert isinstance(quotes, pd.DataFrame)


@pytest.fixture
def local_json_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = json.dumps({"fixture": True, "value": 1.25}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            pass

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}/fixture"
        finally:
            server.shutdown()
            thread.join(timeout=5)


@pytest.mark.parametrize("client", ["requests", "curl_cffi.requests"])
def test_http_transport_loopback_only(client, local_json_server):
    module = import_module(client)
    with module.Session(trust_env=False) if client != "requests" else module.Session() as session:
        session.trust_env = False
        response = session.get(local_json_server, timeout=5)
        response.raise_for_status()
        assert response.json() == {"fixture": True, "value": 1.25}
