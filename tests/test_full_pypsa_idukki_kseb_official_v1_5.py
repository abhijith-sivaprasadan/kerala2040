from pathlib import Path

import yaml

from kerala2040.full_pypsa_idukki_kseb_official_v1_5 import (
    SUITE_CLASS,
    assess_kseb_official_gate,
    load_kseb_official_v15_suite,
)


def test_v15_config_contract():
    root = Path(__file__).resolve().parents[1]
    suite = load_kseb_official_v15_suite(
        root / "configs/full_pypsa_idukki_kseb_official_v1_5.yaml"
    )
    assert suite["classification"] == SUITE_CLASS
    assert suite["official_source"]["required_months"] == 12
    assert suite["pilot_period"]["required_calendar_days"] == 365
    assert suite["pilot_period"]["required_dispatch_inflow_days"] == 364
    assert suite["official_source"]["missing_value_policy"] == (
        "fail_closed_no_interpolation"
    )


def test_v15_missing_bundle_blocks():
    root = Path(__file__).resolve().parents[1]
    suite = load_kseb_official_v15_suite(
        root / "configs/full_pypsa_idukki_kseb_official_v1_5.yaml"
    )
    gate = assess_kseb_official_gate(root, None, suite)
    assert gate["physical_run_ready"] is False
    assert gate["status"] == "blocked_official_monthly_bundle_missing"


def test_v15_rejects_changed_calendar_requirement(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    source = yaml.safe_load(
        (root / "configs/full_pypsa_idukki_kseb_official_v1_5.yaml").read_text(
            encoding="utf-8"
        )
    )
    source["pilot_period"]["required_calendar_days"] = 364
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(source), encoding="utf-8")

    try:
        load_kseb_official_v15_suite(path)
    except ValueError as exc:
        assert "calendar-day requirement" in str(exc)
    else:
        raise AssertionError("changed v1.5 calendar requirement was accepted")
