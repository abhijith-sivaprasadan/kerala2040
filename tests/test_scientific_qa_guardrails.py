"""Conference-scientific-QA regression guards.

These tests protect interpretation/provenance corrections discovered during the
28 September 2026 red-team pass. They do not validate physical truth; they prevent
known unsafe wording/source-boundary regressions from silently returning.
"""

from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_shornur_current_capacity_correction_is_preserved() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    synthesis = (
        ROOT / "docs/POWER_SYSTEM_STRESS_SYNTHESIS_2026_09_28.md"
    ).read_text(encoding="utf-8")
    bottlenecks = (
        ROOT / "docs/KSEB_NETWORK_ROBUST_BOTTLENECKS_V1_0.md"
    ).read_text(encoding="utf-8")

    for text in (readme, synthesis, bottlenecks):
        assert "200 MVA + 100 MVA" in text or "200+100 MVA" in text
    assert "not a current whole-station loading estimate" in readme
    assert "not a current whole-station loading estimate" in synthesis
    assert "historical-input screening result" in bottlenecks


def test_era5_load_proxy_is_not_relabelled_forecast_or_telemetry() -> None:
    doc = (
        ROOT / "docs/ERA5_WEATHER_SENSITIVE_HOURLY_LOAD_PROXY_2026_09_27.md"
    ).read_text(encoding="utf-8")
    qa = (ROOT / "docs/qa/REPRODUCIBILITY_AUDIT.md").read_text(
        encoding="utf-8"
    )

    assert "proxy reconstruction, not measured telemetry" in doc.lower()
    assert "5797 MW" in doc
    assert "5904 MW CEA generation-resource-adequacy planning reference" in doc
    assert "not end-to-end reproducible" in qa
    assert "original fitting script" in qa


def test_import_price_524_is_average_not_weighted_mcp() -> None:
    evidence = json.loads(
        (
            ROOT
            / "data/evidence/grid/"
            "kerala_import_economics_forward_transfer_v1_0_2026_09_25.json"
        ).read_text(encoding="utf-8")
    )
    iex = evidence["import_price_benchmarks"]["iex_dam_fy2023_24"]

    assert iex["nominal_inr_per_kwh"] == pytest.approx(5.24)
    assert iex["role"] == "wholesale_average_mcp_proxy"
    assert "weighted MCP" in iex["source_note"]
    assert "not volume-weighted MCP" in iex["boundary_warning"]


def test_idukki_energy_equivalent_reproduces_source_rows() -> None:
    source = ROOT / "data/external/sldc_fy2024_25/reservoir_daily.csv"
    rows = list(csv.DictReader(source.open(encoding="utf-8", newline="")))
    idukki = [row for row in rows if row["reservoir_name_as_reported"] == "IDUKKI"]

    assert len(idukki) == 354
    assert {float(row["full_reservoir_storage_mcm"]) for row in idukki} == {1460.0}
    assert {
        float(row["full_reservoir_storage_reported_mu"]) for row in idukki
    } == {2190.0}

    ratios = [
        float(row["generation_capability_station_mu"])
        * 1000.0
        / float(row["effective_storage_mcm"])
        for row in idukki
        if float(row["effective_storage_mcm"]) > 0
    ]
    assert statistics.median(ratios) == pytest.approx(1470.0, abs=0.01)
    assert 2190.0 * 1000.0 / 1460.0 == pytest.approx(1500.0)


def test_kerala_context_keeps_case_study_and_population_boundaries() -> None:
    context = (
        ROOT / "docs/KERALA_CONTEXT_FOR_SWEDISH_AUDIENCE_2026_09_28.md"
    ).read_text(encoding="utf-8")

    assert "36.207 million" in context
    assert "not** the denominator" in context
    assert "documented project-stage example" in context
    assert "not installed capacity" in context.lower()
    assert "monazite-bearing heavy-mineral black sands" in context


def test_claims_matrix_has_unique_ids_and_explicit_status() -> None:
    path = ROOT / "docs/qa/claims_matrix.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))

    assert len(rows) >= 50
    ids = [row["claim_id"] for row in rows]
    assert len(ids) == len(set(ids))
    assert all(row["status"].strip() for row in rows)
    assert all(row["conference_use"] in {"yes", "no"} for row in rows)

    by_id = {row["claim_id"]: row for row in rows}
    assert by_id["HY03"]["status"] == "RED"
    assert by_id["N05"]["status"] == "RED"
    assert by_id["Q02"]["status"] == "RED"
    assert by_id["X01"]["status"] == "GREEN"
