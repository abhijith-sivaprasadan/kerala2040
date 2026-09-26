"""Tests for fail-closed Kerala SLDC Storage gap recovery."""
from kerala2040.sldc_storage_gap_recovery import (
    _parse_storage_candidate,
    _payload,
)


def test_storage_payload():
    assert _payload("2024-11-30") == {
        "date1_day": "30",
        "date1_month": "11",
        "date1_year": "2024",
        "sbtstat": "SHOW",
    }


def test_parse_exact_storage_candidate():
    html = """
    <html><body>
      <h3>SYSTEM STATISTICS: STORAGE AS ON 30.11.2024</h3>
      <table>
        <tr><td>694.944</td><td>732.43</td><td>1460</td><td>2190</td>
            <td>IDUKKI</td><td>720</td><td>900</td><td>62</td>
            <td>1350</td><td>1320</td><td></td><td></td>
            <td>2.5</td><td>127.0</td><td>61</td><td></td></tr>
      </table>
    </body></html>
    """
    parsed = _parse_storage_candidate(html, "2024-11-30")
    assert parsed["accepted"] is True
    assert parsed["idukki_inflow_cell"] == "2.5"
    assert parsed["idukki_cumulative_inflow_cell"] == "127.0"


def test_parse_rejects_wrong_date():
    html = """
    <h3>SYSTEM STATISTICS: STORAGE AS ON 29.11.2024</h3>
    <table><tr><td>IDUKKI</td></tr></table>
    """
    parsed = _parse_storage_candidate(html, "2024-11-30")
    assert parsed["accepted"] is False
    assert parsed["reason"] == "requested_storage_heading_not_unique_or_exact"
