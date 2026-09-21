"""Source QA and scientific non-admission invariants for Kerala renewables."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/evidence/solar"


def read(name: str):
    return json.loads((EVIDENCE / name).read_text(encoding="utf8"))


def test_nwic_boundary_clip_is_not_siting_capacity() -> None:
    d = read("kerala_boundary_resource_clips_2026_09_22.json")
    assert d["NIWE"]["inside_Kerala_points"] == 200692
    assert d["GSA"]["native_grid_PVOUT_cells"] == 46241
    assert d["GSA"]["all_46241_annual_daily_ratio_365_25_checked"] is True
    assert d["model_ready"] is False
    assert d["capacity_MW"] is None
    assert d["offshore_assessed"] is False
    assert "NOT_committed" in d["derived_binary_storage"]


def test_all_five_tech_capacities_stay_null_without_constraints() -> None:
    d = read("solar_wind_feasible_capacity_gates_2026_09_22.json")
    for tech in ("rooftop_pv", "ground_mounted_pv", "floating_pv",
                 "onshore_wind", "offshore_wind"):
        row = d["technologies"][tech]
        assert row.get("feasible_GWp_range", row.get("feasible_MW_range")) is None
        assert row["missing"]
    assert d["technologies"]["floating_pv"][
        "publisher_NISE_2026_scenarios_GWp_DC"
    ] == {"20percent_surface": 2.22, "broader_feasible_area": 5.73}
    assert d["model_admitted"] is False


def test_renewable_admission_gate_fails_on_actual_missing_evidence() -> None:
    p = subprocess.run(
        [sys.executable, str(ROOT / "scripts/gate_kerala_solar_wind_model_admission.py")],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert p.returncode == 2, p.stdout + p.stderr
    d = json.loads(p.stdout)
    assert d["model_admitted"] is False
    assert d["proxies_allowed_as_verified_generation"] is False
    assert not d["all_checks_pass"]
    assert not d["checks"]["independently_measured_solar_generation_or_irradiance_validation"]


def test_source_binary_release_does_not_exist_by_manifest_declaration() -> None:
    d = read("solar_batch_2026_09_21_originals_manifest.json")
    assert d["release_uploaded"] is False
    assert d["release_url"] is None
    assert len(d["assets"]) == 17
