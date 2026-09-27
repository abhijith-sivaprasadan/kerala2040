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
