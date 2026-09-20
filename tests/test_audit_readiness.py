"""Verify that scientific gates cannot be inferred from code or source catalogues."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from kerala2040.audit_readiness import (
    STATUS_BLOCKED,
    STATUS_PARTIAL,
    STATUS_PASS,
    build_audit,
    markdown_report,
)

ROOT = Path(__file__).resolve().parents[1]


def test_readiness_preserves_historical_evidence_and_blocks_2040_claims():
    report = build_audit(ROOT)
    assert report["classification"] == (
        "repository_evidence_audit_not_external_source_validation"
    )
    assert report["finding_count"] == 17
    assert report["closed_findings"] == 0
    assert report["open_findings"] == 17
    assert report["checks"]["sldc_accounting_integrity"]["status"] == STATUS_PASS
    assert report["checks"]["sldc_daily_coverage"]["status"] == STATUS_PARTIAL
    assert "2024-08-12" in report["checks"]["sldc_daily_coverage"]["detail"]
    assert report["checks"]["measured_interval"]["status"] == STATUS_BLOCKED
    assert report["checks"]["era5_complete"]["status"] == STATUS_PARTIAL
    assert "4 NRSC LULC product routes" in report["checks"]["gis_model_ready"]["detail"]
    assert report["checks"]["gis_model_ready"]["status"] == STATUS_BLOCKED
    assert "three forest/DEM/hazard" in report["checks"]["gis_model_ready"]["detail"]
    assert "39 EPSG:32643 MultiPolygons" in report["checks"]["gis_model_ready"]["detail"]
    assert "ring self-intersection" in report["checks"]["gis_model_ready"]["detail"]
    assert "14 original Copernicus GLO90" in report["checks"]["gis_model_ready"]["detail"]
    assert report["checks"]["grid_transfer"]["status"] == STATUS_BLOCKED
    assert "6500 MW" in report["checks"]["grid_transfer"]["detail"]
    assert report["checks"]["hydro_physics"]["status"] == STATUS_BLOCKED
    assert "9 qualitative links" in report["checks"]["hydro_physics"]["detail"]
    assert report["checks"]["generator_assets"]["status"] == STATUS_PARTIAL
    assert "100 MW" in report["checks"]["generator_assets"]["detail"]
    assert report["checks"]["technology_costs"]["status"] == STATUS_BLOCKED
    assert report["release_gates"]["daily_accounting"]["passed"]
    assert not report["release_gates"]["observed_full_year"]["passed"]
    assert not report["release_gates"]["ecological_capacity_ceiling"]["passed"]
    assert not report["release_gates"]["techno_economic_2040"]["passed"]
    assert not report["release_gates"]["kmml_case"]["passed"]


def test_report_does_not_present_daily_checks_as_hourly_validation():
    report = build_audit(ROOT)
    document = markdown_report(report)
    assert "Daily accounting passing does not demonstrate" in document
    assert "BLOCKED" in document
    assert "17 acquisition findings" in document
    assert "measured_interval" in document


def test_source_qa_tampering_fails_closed(tmp_path):
    for file in (
        "data/external/sldc_fy2024_25/qa_report.json",
        "public/era5-daily-manifest.json",
        "configs/techno_economics.yaml",
        "configs/gis_inputs.yaml",
        "configs/lulc_native_acquisition_2024_25.yaml",
        "configs/gis_forest_dem_wetlands_hazards_2026.yaml",
        "data/evidence/gis/official_gis_public_acquisition_2026_09_20.json",
        "data/evidence/gis/gsi_2022_geometry_validation_2026_09_20.json",
        "data/evidence/gis/copernicus_glo90_envelope_2026_09_20.json",
        "configs/audit_findings.yaml",
        "configs/observed_2024_25.yaml",
        "configs/generator_reconciliation_2024_25.yaml",
        "configs/hydro_topology_evidence_2024_25.yaml",
        "configs/grid_transfer_contract_evidence_2024_25.yaml",
        "public/kseb-projects.json",
    ):
        target = tmp_path / file
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / file, target)
    qa_path = tmp_path / "data/external/sldc_fy2024_25/qa_report.json"
    qa = json.loads(qa_path.read_text())
    qa["observed_days"] = 365
    qa_path.write_text(json.dumps(qa))
    with pytest.raises(ValueError, match="coverage inconsistent"):
        build_audit(tmp_path)
    qa["observed_days"] = 354
    qa["bad_raw_sha256_count"] = 1
    qa_path.write_text(json.dumps(qa))
    with pytest.raises(ValueError, match="hash"):
        build_audit(tmp_path)


def test_unknown_gate_is_rejected_instead_of_counted_ready(tmp_path):
    import yaml

    for file in (
        "data/external/sldc_fy2024_25/qa_report.json",
        "public/era5-daily-manifest.json",
        "configs/techno_economics.yaml",
        "configs/gis_inputs.yaml",
        "configs/lulc_native_acquisition_2024_25.yaml",
        "configs/gis_forest_dem_wetlands_hazards_2026.yaml",
        "data/evidence/gis/official_gis_public_acquisition_2026_09_20.json",
        "data/evidence/gis/gsi_2022_geometry_validation_2026_09_20.json",
        "data/evidence/gis/copernicus_glo90_envelope_2026_09_20.json",
        "configs/audit_findings.yaml",
        "configs/observed_2024_25.yaml",
        "configs/generator_reconciliation_2024_25.yaml",
        "configs/hydro_topology_evidence_2024_25.yaml",
        "configs/grid_transfer_contract_evidence_2024_25.yaml",
        "public/kseb-projects.json",
    ):
        target = tmp_path / file
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / file, target)
    path = tmp_path / "configs/audit_findings.yaml"
    config = yaml.safe_load(path.read_text())
    config["release_gates"]["techno_economic_2040"]["required"].append("imaginary_ready")
    path.write_text(yaml.safe_dump(config))
    with pytest.raises(ValueError, match="Unknown"):
        build_audit(tmp_path)


def test_generator_register_official_source_crosscheck_fails_closed(tmp_path):
    import yaml

    inputs = (
        "data/external/sldc_fy2024_25/qa_report.json",
        "public/era5-daily-manifest.json",
        "configs/techno_economics.yaml",
        "configs/gis_inputs.yaml",
        "configs/lulc_native_acquisition_2024_25.yaml",
        "configs/gis_forest_dem_wetlands_hazards_2026.yaml",
        "data/evidence/gis/official_gis_public_acquisition_2026_09_20.json",
        "data/evidence/gis/gsi_2022_geometry_validation_2026_09_20.json",
        "data/evidence/gis/copernicus_glo90_envelope_2026_09_20.json",
        "configs/audit_findings.yaml",
        "configs/observed_2024_25.yaml",
        "configs/generator_reconciliation_2024_25.yaml",
        "configs/hydro_topology_evidence_2024_25.yaml",
        "configs/grid_transfer_contract_evidence_2024_25.yaml",
        "public/kseb-projects.json",
    )
    for file in inputs:
        target = tmp_path / file
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / file, target)
    path = tmp_path / "configs/generator_reconciliation_2024_25.yaml"
    source = yaml.safe_load(path.read_text())
    source["official_commissioned_during_fy"][0]["units"][0]["capacity_mw"] = 15
    path.write_text(yaml.safe_dump(source))
    with pytest.raises(ValueError, match="unit MW differ"):
        build_audit(tmp_path)


def test_transfer_gate_rejects_import_limit_promotion(tmp_path):
    import yaml

    inputs = (
        "data/external/sldc_fy2024_25/qa_report.json",
        "public/era5-daily-manifest.json",
        "configs/techno_economics.yaml",
        "configs/gis_inputs.yaml",
        "configs/lulc_native_acquisition_2024_25.yaml",
        "configs/gis_forest_dem_wetlands_hazards_2026.yaml",
        "data/evidence/gis/official_gis_public_acquisition_2026_09_20.json",
        "data/evidence/gis/gsi_2022_geometry_validation_2026_09_20.json",
        "data/evidence/gis/copernicus_glo90_envelope_2026_09_20.json",
        "configs/audit_findings.yaml",
        "configs/observed_2024_25.yaml",
        "configs/generator_reconciliation_2024_25.yaml",
        "configs/hydro_topology_evidence_2024_25.yaml",
        "configs/grid_transfer_contract_evidence_2024_25.yaml",
        "public/kseb-projects.json",
    )
    for file in inputs:
        target = tmp_path / file
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / file, target)
    path = tmp_path / "configs/grid_transfer_contract_evidence_2024_25.yaml"
    evidence = yaml.safe_load(path.read_text())
    evidence["model_use"]["can_apply_snapshot_as_full_year_import_limit"] = True
    path.write_text(yaml.safe_dump(evidence))
    with pytest.raises(ValueError, match="cannot certify model constraints"):
        build_audit(tmp_path)


def test_lulc_register_cannot_self_certify_ecological_capacity(tmp_path):
    import yaml

    inputs = (
        "data/external/sldc_fy2024_25/qa_report.json",
        "public/era5-daily-manifest.json",
        "configs/techno_economics.yaml",
        "configs/gis_inputs.yaml",
        "configs/lulc_native_acquisition_2024_25.yaml",
        "configs/gis_forest_dem_wetlands_hazards_2026.yaml",
        "data/evidence/gis/official_gis_public_acquisition_2026_09_20.json",
        "data/evidence/gis/gsi_2022_geometry_validation_2026_09_20.json",
        "data/evidence/gis/copernicus_glo90_envelope_2026_09_20.json",
        "configs/audit_findings.yaml",
        "configs/observed_2024_25.yaml",
        "configs/generator_reconciliation_2024_25.yaml",
        "configs/hydro_topology_evidence_2024_25.yaml",
        "configs/grid_transfer_contract_evidence_2024_25.yaml",
        "public/kseb-projects.json",
    )
    for file in inputs:
        target = tmp_path / file
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / file, target)
    path = tmp_path / "configs/lulc_native_acquisition_2024_25.yaml"
    data = yaml.safe_load(path.read_text())
    data["model_use"]["generation_capacity_ceiling_mw"] = 100000
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ValueError, match="unsupported capacity"):
        build_audit(tmp_path)


def test_three_gis_workstreams_cannot_invent_a_ceiling(tmp_path):
    import yaml

    inputs = (
        "data/external/sldc_fy2024_25/qa_report.json",
        "public/era5-daily-manifest.json",
        "configs/techno_economics.yaml",
        "configs/gis_inputs.yaml",
        "configs/lulc_native_acquisition_2024_25.yaml",
        "configs/gis_forest_dem_wetlands_hazards_2026.yaml",
        "data/evidence/gis/official_gis_public_acquisition_2026_09_20.json",
        "data/evidence/gis/gsi_2022_geometry_validation_2026_09_20.json",
        "data/evidence/gis/copernicus_glo90_envelope_2026_09_20.json",
        "configs/audit_findings.yaml",
        "configs/observed_2024_25.yaml",
        "configs/generator_reconciliation_2024_25.yaml",
        "configs/hydro_topology_evidence_2024_25.yaml",
        "configs/grid_transfer_contract_evidence_2024_25.yaml",
        "public/kseb-projects.json",
    )
    for file in inputs:
        target = tmp_path / file
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / file, target)
    path = tmp_path / "configs/gis_forest_dem_wetlands_hazards_2026.yaml"
    data = yaml.safe_load(path.read_text())
    data["model_use"]["potential_mw"] = 12500
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ValueError, match="cannot invent eligibility"):
        build_audit(tmp_path)
