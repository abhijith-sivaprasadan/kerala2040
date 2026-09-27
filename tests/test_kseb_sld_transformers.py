"""Regression tests for KSEBL public SLD transformer text parsing."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/promote_kseb_sld_transformers.py"
SPEC = importlib.util.spec_from_file_location("kseb_sld_transformers", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _first_levels(context: str) -> list[int]:
    accepted, _ = MODULE._parse_context(context)
    assert accepted
    return accepted[0]["voltage_levels_kv"]


def test_repeated_kv_three_winding_notation() -> None:
    context = "BHEL 220KV/110KV/11KV 160MVA TR BANK I & II"
    accepted, _ = MODULE._parse_context(context)
    assert accepted[0]["voltage_levels_kv"] == [220, 110, 11]
    assert accepted[0]["voltage_notation_normalized"] is False


def test_compact_110_66_voltage_notation() -> None:
    context = "40 MVA 11066 KV TRANSFORMER No. I"
    accepted, _ = MODULE._parse_context(context)
    assert accepted[0]["voltage_levels_kv"] == [110, 66]
    assert accepted[0]["voltage_notation_normalized"] is True


def test_compact_66_11_voltage_notation() -> None:
    context = "10 MVA 6611 KV TRANSFORMER II"
    assert _first_levels(context) == [66, 11]


def test_unrelated_numeric_token_is_not_rewritten_as_voltage() -> None:
    normalized, changed = MODULE._normalize_voltage_notation(
        "CT 400200100/1A TRANSFORMER 40 MVA"
    )
    assert normalized == "CT 400200100/1A TRANSFORMER 40 MVA"
    assert changed is False
