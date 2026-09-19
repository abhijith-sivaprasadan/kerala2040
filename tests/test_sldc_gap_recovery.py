"""The missing-date fetch must fail closed on wrong day and on false balances."""

from __future__ import annotations

import json
from pathlib import Path

from requests.exceptions import ConnectionError as RequestConnectionError

from kerala2040.sldc_gap_recovery import probe_missing_dates

ROOT = Path(__file__).resolve().parents[1]


def _html(date: str, consumption: float = 90) -> bytes:
    dd, mm, yyyy = date[8:10], date[5:7], date[:4]
    return (
        f"<html><body>SYSTEM STATISTICS - FOR {dd}/{mm}/{yyyy}, Monday"
        "<table><tr><td>Internal Generation</td><td>40</td></tr>"
        "<tr><td>Net Import</td><td>50</td></tr>"
        f"<tr><td>Consumption</td><td>{consumption}</td></tr>"
        "</table></body></html>"
    ).encode()


class Response:
    def __init__(self, html: bytes, url: str = "https://sldckerala.com/index.php?id=1"):
        self.content = html
        self.text = html.decode()
        self.status_code = 200
        self.url = url


class FakeSession:
    def __init__(self, responses: list[Response]):
        self.responses = iter(responses)
        self.calls = []

    def post(self, url, *, data, timeout):
        self.calls.append((url, data, timeout))
        return next(self.responses)


def test_accepts_only_matching_generation_candidate(tmp_path):
    session = FakeSession([Response(_html("2024-08-12"))])
    result = probe_missing_dates(
        ["2024-08-12"], tmp_path, session, pause_seconds=0
    )
    assert result["recovered_generation_candidates"] == 1
    assert result["not_recovered"] == 0
    assert result["official_observed_day_coverage_changed"] is False
    assert result["audit_gate_closed"] is False
    assert session.calls[0][1]["sbtstat"] == "SHOW"
    assert session.calls[0][1]["date1_day"] == "12"
    assert (tmp_path / "verified_generation_candidates/2024-08-12.html").read_bytes() == (
        _html("2024-08-12")
    )


def test_wrong_date_and_false_balance_never_create_observations(tmp_path):
    session = FakeSession([
        Response(_html("2024-08-13")),
        Response(_html("2024-08-12", consumption=95)),
    ])
    report = probe_missing_dates(
        ["2024-08-12"], tmp_path, session, pause_seconds=0
    )
    assert report["not_recovered"] == 1
    assert [x["result"] for x in report["records"][0]["attempts"]] == [
        "wrong_report_date", "balance_failure"
    ]
    assert not list((tmp_path / "verified_generation_candidates").iterdir())


def test_partial_http_failure_does_not_count_as_missing_source(tmp_path):
    class Failed:
        def post(self, *_args, **_kwargs):
            raise RequestConnectionError("transport unavailable")

    report = probe_missing_dates(
        ["2024-08-12"], tmp_path, Failed(), pause_seconds=0
    )
    assert report["not_recovered"] == 1
    assert report["records"][0]["status"] == "not_recovered"
    assert len(report["records"][0]["attempts"]) == 2
    assert all(
        a["result"] == "request_failed" for a in report["records"][0]["attempts"]
    )


def test_uses_exact_committed_qa_dates_not_an_arbitrary_selection(tmp_path):
    qa = json.loads(
        (ROOT / "data/external/sldc_fy2024_25/qa_report.json").read_text()
    )
    assert qa["missing_dates"][0] == "2024-08-12"
    assert len(qa["missing_dates"]) == 11
    assert qa["observed_days"] == 354
    assert qa["expected_days"] == 365
