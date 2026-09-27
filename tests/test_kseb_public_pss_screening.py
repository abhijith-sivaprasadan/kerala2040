"""Regression tests for KSEBL PSS and screening-evidence helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PSS = _load("kseb_public_pss", "scripts/build_kseb_public_pss_evidence.py")
SCREEN = _load(
    "kseb_transport_screening",
    "scripts/build_kseb_transport_screening_inputs.py",
)


def test_pss_conductor_parser_handles_known_table34_forms() -> None:
    assert (
        PSS._extract_conductor(
            "1 Adimaly - Aluva 1ADAL ACSR Panther 69 2022"
        )
        == "ACSR_PANTHER"
    )
    assert (
        PSS._extract_conductor(
            "65 Sabarigiri - Ambalamugal 2SBAM ACSR Kundah 123.62"
        )
        == "ACSR_KUNDAH"
    )
    assert (
        PSS._extract_conductor(
            "MADAKKATHARA - KOZHIKKODE 4MDKZI TWIN GREAT HORNBILL"
        )
        == "TWIN_GREAT_HORNBILL"
    )
    assert (
        PSS._extract_conductor(
            "Ambalathara - Cheruvathoor 1ABCV ACSR Wolf/Tiger 19.57"
        )
        == "ACSR_WOLF_TIGER"
    )


def test_screen_current_uses_series_bottleneck() -> None:
    ampacity = {
        "WOLF": 343.0,
        "PANTHER": 427.0,
        "KUNDAH": 726.0,
        "MOOSE": 880.0,
    }
    current, basis, source_backed = SCREEN._screen_current(
        "ACSR_WOLF_PANTHER", 110, ampacity
    )
    assert current == 343.0
    assert "PSS_CONDUCTOR" in basis
    assert source_backed is True


def test_screen_current_bundle_and_fallback() -> None:
    ampacity = {"MOOSE": 880.0}
    current, _, source_backed = SCREEN._screen_current(
        "TWIN_MOOSE", 400, ampacity
    )
    assert current == 1760.0
    assert source_backed is True

    current, basis, source_backed = SCREEN._screen_current(
        "", 110, ampacity
    )
    assert current == 296.0
    assert "ASSUMPTION" in basis
    assert source_backed is False


def test_frozen_pss_snapshot_integrity_and_scope() -> None:
    snapshot = PSS._load_snapshot(PSS.DEFAULT_SNAPSHOT)
    assert snapshot["classification"] == PSS.SNAPSHOT_CLASSIFICATION
    assert snapshot["source"]["source_as_of"] == "2023-03-31"
    assert snapshot["scope"]["network_model_minimum_voltage_kv"] == 110
    assert len(snapshot["table33_primary_station_rows"]) == 134
    assert len(snapshot["table34_graph_crosswalk_rows"]) == 253
    assert (
        snapshot["snapshot_payload_sha256"]
        == PSS.EXPECTED_SNAPSHOT_SHA256
    )


def test_pss_conductor_parser_preserves_mixed_and_fallback_types() -> None:
    assert PSS._extract_conductor("ACSR Wolf+UG") == "MIXED_WOLF_UG"
    assert (
        PSS._extract_conductor("AL59+ACSR Wolf")
        == "MIXED_AL59_WOLF"
    )
    assert (
        PSS._extract_conductor("AAAC+ACSR Wolf")
        == "MIXED_AAAC_WOLF"
    )
    assert PSS._extract_conductor("AAAC") == "AAAC"
    assert PSS._extract_conductor("Zebra") == "ZEBRA"
    assert PSS._extract_conductor("ACSR Dog") == "ACSR_DOG"
    assert PSS._extract_conductor("STACIR") == "STACIR"


def test_mixed_conductor_screening_falls_back() -> None:
    ampacity = {"WOLF": 343.0}
    current, basis, source_backed = SCREEN._screen_current(
        "MIXED_WOLF_UG", 110, ampacity
    )
    assert current == 296.0
    assert "ASSUMPTION" in basis
    assert source_backed is False


def test_transport_screening_uses_canonical_8760_hour_proxy_loader() -> None:
    manifest = (
        ROOT
        / "data/evidence/demand/"
        "hourly_load_proxy_era5_weather_sensitive_v2/manifest.json"
    )
    proxy = SCREEN._decode_load_proxy(manifest)
    assert proxy["classification"] == "proxy_reconstruction_not_measured_telemetry"
    assert len(proxy["records"]) == 8760
    assert proxy["records"][0]["classification"] == "proxy_reconstruction"


def test_pss_station_match_prefers_new_kattakada_over_nested_kattakada() -> None:
    candidates = [
        {
            "node_id": "SS:KKDA:110",
            "location": "Kattakkada",
            "code": "KKDA",
            "kind": "substation",
            "voltage_class_kv": 110,
            "norm_location": PSS._norm_name("Kattakkada"),
        },
        {
            "node_id": "SS:NKDA:220",
            "location": "New Kattakada",
            "code": "NKDA",
            "kind": "substation",
            "voltage_class_kv": 220,
            "norm_location": PSS._norm_name("New Kattakada"),
        },
    ]
    node, basis = PSS._match_station(
        "21 New Kattakkada Thiruvananthapuram ",
        candidates,
    )
    assert node is not None
    assert node["node_id"] == "SS:NKDA:220"
    assert "EXACT_NORMALIZED_LOCATION" in basis
