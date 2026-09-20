"""Hydro topology must never turn observed reservoir indicators into independent stores."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from kerala2040.hydro_operations import audit_hydro_evidence

ROOT = Path(__file__).resolve().parents[1]
INPUTS = (
    "data/external/sldc_fy2024_25/qa_report.json",
    "data/external/sldc_fy2024_25/daily_balance.csv",
    "data/external/sldc_fy2024_25/reservoir_daily.csv",
    "data/external/sldc_fy2024_25/hydro_station_daily.csv",
    "configs/hydro_topology_evidence_2024_25.yaml",
)


def _copy(tmp_path: Path) -> Path:
    for path in INPUTS:
        dest = tmp_path / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, dest)
    return tmp_path


def test_hydro_evidence_is_a_partial_qualitative_network():
    report = audit_hydro_evidence(ROOT)
    assert report["observed_dates"] == 354
    assert report["expected_dates"] == 365
    assert len(report["missing_dates"]) == 11
    assert report["reservoir_rows"] == 5664
    assert report["reservoir_rows_per_observed_date"] == 16
    assert report["unique_reservoir_names"] == 16
    assert report["hydro_station_rows"] == 5779
    assert report["qualitative_topology"]["mapped_reservoir_labels"] == 6
    assert report["qualitative_topology"]["documented_qualitative_links"] == 9
    assert report["qualitative_topology"]["documented_shared_waterbody_complexes"] == 3
    assert report["positive_effective_storage_with_zero_reported_pct"] > 0
    assert not report["water_balance_reconciled"]
    assert not report["cascade_energy_allocation_allowed"]
    assert not report["pypsa_connected_hydro_stores_allowed"]
    assert not report["audit_gate_closed"]


def test_cyclic_tailrace_mapping_must_fail(tmp_path):
    root = _copy(tmp_path)
    path = root / "configs/hydro_topology_evidence_2024_25.yaml"
    topo = yaml.safe_load(path.read_text(encoding="utf-8"))
    topo["documented_links"].append({
        "from": "Poringalkuthu, PLBE", "to": "SHOLAYAR",
        "relation": "invented_loop", "source_ids": ["kseb_poringal"],
    })
    path.write_text(yaml.safe_dump(topo), encoding="utf-8")
    with pytest.raises(ValueError, match="cycle"):
        audit_hydro_evidence(root)


def test_wrong_station_and_missing_url_fail_closed(tmp_path):
    root = _copy(tmp_path)
    path = root / "configs/hydro_topology_evidence_2024_25.yaml"
    topo = yaml.safe_load(path.read_text(encoding="utf-8"))
    topo["observed_reservoirs"]["IDUKKI"]["source_station_labels"] = ["invented"]
    path.write_text(yaml.safe_dump(topo), encoding="utf-8")
    with pytest.raises(ValueError, match="Unmatched observed station"):
        audit_hydro_evidence(root)
    topo["observed_reservoirs"]["IDUKKI"]["source_station_labels"] = ["Idukki"]
    topo["sources"]["kseb_idukki"]["url"] = ""
    path.write_text(yaml.safe_dump(topo), encoding="utf-8")
    with pytest.raises(ValueError, match="source URL missing"):
        audit_hydro_evidence(root)


def test_reservoir_rows_cannot_be_silently_lost(tmp_path):
    root = _copy(tmp_path)
    path = root / "data/external/sldc_fy2024_25/reservoir_daily.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="row count"):
        audit_hydro_evidence(root)
