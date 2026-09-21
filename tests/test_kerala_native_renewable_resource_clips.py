"""Protect exact-boundary solar/wind clipping evidence and archival truth."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "data/evidence/solar/kerala_native_resource_clips_2026_09_22.json"
BATCH = ROOT / "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json"


def test_kerala_native_source_clip_evidence_is_not_model_admission() -> None:
    qa = json.loads(QA.read_text(encoding="utf-8"))
    batch = json.loads(BATCH.read_text(encoding="utf-8"))
    assert qa["NWIC_original_zip_sha256"] == (
        "a932ea29e7afd0fea1e1068f3beeeadb760e6b2baae9783f5822bbefd4224ebd"
    )
    assert qa["NIWE_inside_exact_Kerala_polygon_point_centres"] == 200692
    assert qa["GSA_onshore_PVOUT_30arcsec_valid_pixel_centres"] == 46241
    assert qa["GSA_onshore_GHI_9arcsec_valid_pixel_centres"] == 513823
    assert qa["PVOUT_annual_over_daily_full_kerala_clipped_cells"]["count"] == 46241
    assert qa["PVOUT_annual_over_daily_full_kerala_clipped_cells"]["pct_within_0_02"] == 100
    assert qa["science_model_admitted"] is False
    assert qa["all_17_original_solar_binaries_archived_in_GitHub"] is False
    assert qa["NIWE_original_binary_archived_in_GitHub"] is False
    assert batch["release_uploaded"] is False
    assert qa["output_derived_zip_size_bytes"] > 0
    assert len(qa["output_derived_zip_sha256"]) == 64
