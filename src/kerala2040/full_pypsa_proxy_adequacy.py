"""Full-PyPSA v0.2 chronological proxy adequacy sensitivity suite.

This module deliberately reuses the provenance-gated FY2024-25 chronology engine.
It does not create measured hourly telemetry, economic dispatch, probabilistic LOLP,
or a capacity-expansion result.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from kerala2040.chronological_screen import (
    ScreeningAssumptions,
    build_hourly_screening_network,
    dispatch_summary,
    prepare_inputs,
    solve_hourly_screening,
)

SUITE_CLASS = "full_pypsa_proxy_adequacy_sensitivity_not_validated_dispatch"
SELECTION_CLASS = "research_input_selection_v0_2_proxy_screen_ready_not_validated"


def load_proxy_adequacy_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("proxy adequacy suite classification mismatch")
    cases = data.get("cases", [])
    if [case.get("id") for case in cases] != [
        "replay_control",
        "atc_snapshot_reference",
        "atc_80pct_stress",
        "atc_60pct_stress",
    ]:
        raise ValueError("proxy adequacy cases changed or reordered")
    limits = [float(case["import_limit_mw"]) for case in cases]
    if limits != [6500.0, 4455.0, 3564.0, 2673.0]:
        raise ValueError("proxy adequacy import limits do not match v0.2 selection")
    if any(value != 0 for value in data.get("additions", {}).values()):
        raise ValueError("v0.2 proxy adequacy baseline must not add solar or BESS")
    release = data.get("release", {})
    if release.get("proxy_adequacy_screen") is not True:
        raise ValueError("suite is not released for proxy adequacy screening")
    if any(
        release.get(key) is not False
        for key in ("measured_hourly_telemetry_used", "economic_dispatch", "capacity_expansion")
    ):
        raise ValueError("suite promotes a forbidden interpretation")
    return data


def load_v02_selection(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SELECTION_CLASS:
        raise ValueError("research input selection v0.2 classification mismatch")
    release = data.get("release", {})
    if release.get("chronological_proxy_screen_ready") is not True:
        raise ValueError("v0.2 does not permit proxy chronology")
    if release.get("chronological_validated_dispatch_ready") is not False:
        raise ValueError("v0.2 incorrectly claims validated dispatch")
    if release.get("capacity_expansion_ready") is not False:
        raise ValueError("v0.2 incorrectly permits capacity expansion")
    return data


def _load_inputs(root: Path, suite: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any], dict]:
    proxy = json.loads((root / suite["chronology"]).read_text(encoding="utf-8"))
    qa = json.loads((root / suite["qa"]).read_text(encoding="utf-8"))
    observed = json.loads(
        (root / suite["observed_capacity_reference"]).read_text(encoding="utf-8")
    )
    daily = pd.read_csv(root / suite["daily_source_energy"])
    hourly, metadata = prepare_inputs(
        proxy,
        daily,
        expected_missing_dates=qa["missing_dates"],
    )
    metadata["source_archive_sha256"] = qa["source_archive_sha256"]
    metadata["input_qa"] = "verified daily SLDC accounting plus proxy hourly chronology"
    return hourly, metadata, observed


def run_proxy_adequacy_suite(
    root: Path,
    *,
    hours: int = 8760,
) -> dict[str, Any]:
    """Run deterministic proxy adequacy cases.

    hours must be whole days so daily source-energy provenance remains interpretable.
    """
    if not 24 <= hours <= 8760 or hours % 24:
        raise ValueError("hours must be whole days between 24 and 8760")

    suite = load_proxy_adequacy_suite(root / "configs/full_pypsa_proxy_adequacy_v0_2.yaml")
    selection = load_v02_selection(root / "configs/research_input_selection_v0_2.yaml")
    hourly, metadata, observed = _load_inputs(root, suite)
    hourly = hourly.iloc[:hours].copy()
    metadata["modeled_window_hours"] = hours
    metadata["full_financial_year"] = hours == 8760

    capacities = observed["electricity"]["capacity_mix_mw"]
    installed_hydro_mw = float(capacities["hydel"])
    installed_nonhydro_mw = float(
        observed["electricity"]["installed_capacity_mw"] - installed_hydro_mw
    )
    nens_reference = float(
        suite["reliability_comparison"]["deterministic_nens_reference_pct"]
    )

    case_results = []
    for case in suite["cases"]:
        assumptions = ScreeningAssumptions(
            import_limit_mw=float(case["import_limit_mw"]),
            objective_import_per_mwh=float(suite["objective"]["import_per_mwh"]),
            objective_unserved_per_mwh=float(suite["objective"]["unserved_per_mwh"]),
        )
        network = build_hourly_screening_network(
            hourly,
            metadata,
            assumptions,
            installed_hydro_mw=installed_hydro_mw,
            installed_nonhydro_mw=installed_nonhydro_mw,
        )
        status, condition = solve_hourly_screening(network)
        summary = dispatch_summary(network, hourly, status, condition)
        imports = network.generators_t.p["screened_import"]
        unserved = network.generators_t.p["unserved_load"]

        replay_residual = None
        if case["id"] == "replay_control":
            model_daily = (
                pd.DataFrame(
                    {
                        "date": hourly["date"].to_numpy(),
                        "import_mw": imports.to_numpy(),
                    }
                )
                .groupby("date")
                .import_mw.sum()
                / 1000
            )
            reference_daily = hourly.groupby("date").observed_import_mu.first().dropna()
            replay_residual = float(
                (model_daily.loc[reference_daily.index] - reference_daily).abs().max()
            )
            if replay_residual > 0.001 or float(unserved.sum()) > 1e-5:
                raise RuntimeError("replay control no longer reproduces daily source accounting")

        deterministic_nens_pct = float(summary["unserved_pct_modelled"])
        case_results.append(
            {
                "id": case["id"],
                "role": case["role"],
                "import_limit_mw": float(case["import_limit_mw"]),
                "solver_status": status,
                "solver_condition": condition,
                "load_mwh_proxy": float(summary["load_mwh_proxy"]),
                "imports_mwh_modelled": float(summary["imports_mwh_modelled"]),
                "peak_import_mw_modelled": float(imports.max()),
                "unserved_energy_mwh": float(summary["unserved_mwh_modelled"]),
                "deterministic_nens_pct": deterministic_nens_pct,
                "hours_with_unserved": int((unserved > 1e-6).sum()),
                "max_unserved_mw": float(unserved.max()),
                "numerically_below_cea_state_ra_nens_benchmark": (
                    deterministic_nens_pct <= nens_reference
                ),
                "benchmark_comparison_is_Kerala_compliance_claim": False,
                "observed_daily_import_replay_max_residual_mu": replay_residual,
                "max_abs_hourly_balance_residual_mw": float(
                    summary["max_abs_hourly_balance_residual_mw"]
                ),
            }
        )

    return {
        "classification": SUITE_CLASS,
        "selection_classification": selection["classification"],
        "prepared_date": suite["prepared_date"],
        "period": suite["period"],
        "hours": hours,
        "full_financial_year": hours == 8760,
        "hourly_telemetry_measured": False,
        "economic_dispatch": False,
        "capacity_expansion": False,
        "probabilistic_LOLP_evaluated": False,
        "reliability_benchmark": {
            "metric": "NENS/EENS percentage",
            "numerical_reference_pct": nens_reference,
            "classification": (
                "published_CEA_state_RA_benchmark_not_Kerala_statutory_threshold"
            ),
        },
        "cases": case_results,
        "interpretation": [
            "FY2024-25 hourly load is reconstructed, not measured interval telemetry.",
            "Hydro and other internal generation are fixed daily-average replays of SLDC source energy.",
            "The 4455 MW case is a dated 31-March-2026 ATC snapshot used as a sensitivity bound, not an FY2024-25 historical transfer observation or annual guarantee.",
            "The 80% and 60% cases are synthetic ATC haircuts.",
            "The objective uses abstract priorities; results are adequacy sensitivities, not economic dispatch.",
            "LOLP is not estimated because stochastic forced outages and stochastic demand/renewable draws are not modelled.",
        ],
    }
