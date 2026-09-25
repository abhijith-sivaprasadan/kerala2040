"""Use SLDC station-reported daily hydro maxima as a dated redispatch envelope.

This v0.4 screen adds an empirical middle case between:
1. flat daily hydro replay (no intraday flexibility), and
2. v0.3 free same-day redispatch up to full installed hydro MW.

For each observed SLDC day, the hourly hydro ceiling is the sum of nonblank
station-level reported maximum outputs. Missing report dates are interpolated
and labelled model-only. Individual station maxima are not simultaneous, so this
is not a measured aggregate capability or a reservoir/cascade model.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from kerala2040.chronological_screen import ScreeningAssumptions
from kerala2040.full_pypsa_hydro_flexibility import (
    HYDRO_NAME,
    _load_inputs,
    _redispatch_case_summary,
    build_daily_hydro_redispatch_network,
    load_hydro_flexibility_config,
    run_hydro_flexibility_bracket,
    solve_daily_hydro_redispatch,
)
from kerala2040.full_pypsa_proxy_adequacy import (
    load_proxy_adequacy_suite,
    load_v02_selection,
)

CLASSIFICATION = "full_pypsa_hydro_reported_peak_envelope_v0_4_not_validated_dispatch"


def load_reported_peak_envelope_config(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != CLASSIFICATION:
        raise ValueError("reported hydro peak envelope classification mismatch")
    release = data.get("release", {})
    if release.get("research_reported_peak_envelope_ready") is not True:
        raise ValueError("reported hydro peak envelope is not released")
    forbidden_true = (
        "measured_simultaneous_hydro_capability",
        "validated_hydro_dispatch_ready",
        "reservoir_model_ready",
        "capacity_expansion_ready",
    )
    if any(release.get(key) is not False for key in forbidden_true):
        raise ValueError("v0.4 promotes a forbidden hydro interpretation")
    return data


def derive_reported_station_peak_envelope(
    station_daily: pd.DataFrame,
    full_dates: pd.DatetimeIndex,
    *,
    expected_missing_dates: list[str],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Derive one aggregate hydro MW ceiling per FY day."""
    required = {
        "date",
        "station_name_as_reported",
        "generation_mu",
        "reported_maximum_output_mw",
    }
    missing_columns = required - set(station_daily.columns)
    if missing_columns:
        raise ValueError(
            f"hydro station source missing columns: {sorted(missing_columns)}"
        )

    data = station_daily.copy()
    data["date"] = pd.to_datetime(data["date"], errors="raise")
    data["generation_mu"] = pd.to_numeric(data["generation_mu"], errors="coerce")
    data["reported_maximum_output_mw"] = pd.to_numeric(
        data["reported_maximum_output_mw"],
        errors="coerce",
    )

    grouped = data.groupby("date", sort=True)
    observed = pd.DataFrame(
        {
            "reported_peak_envelope_mw": grouped[
                "reported_maximum_output_mw"
            ].sum(min_count=1),
            "station_generation_mu": grouped["generation_mu"].sum(min_count=1),
            "station_generation_with_reported_peak_mu": grouped.apply(
                lambda frame: frame.loc[
                    frame["reported_maximum_output_mw"].notna(),
                    "generation_mu",
                ].sum()
            ),
            "station_rows": grouped.size(),
            "rows_with_reported_peak": grouped[
                "reported_maximum_output_mw"
            ].count(),
        }
    )
    observed["reported_peak_row_fraction"] = (
        observed["rows_with_reported_peak"] / observed["station_rows"]
    )
    observed["reported_peak_energy_fraction"] = (
        observed["station_generation_with_reported_peak_mu"]
        / observed["station_generation_mu"]
    )
    observed["classification"] = "official_observed_reference"

    expected_missing = pd.DatetimeIndex(pd.to_datetime(expected_missing_dates))
    observed_dates = pd.DatetimeIndex(observed.index)
    actual_missing = full_dates.difference(observed_dates)
    if set(actual_missing) != set(expected_missing):
        raise ValueError(
            "hydro station missing dates do not match the admitted SLDC QA gap set"
        )

    result = observed.reindex(full_dates)
    result.index.name = "date"
    missing_mask = result["reported_peak_envelope_mw"].isna()
    result["reported_peak_envelope_mw"] = (
        result["reported_peak_envelope_mw"].interpolate(
            method="time",
            limit_area="inside",
        )
    )
    if result["reported_peak_envelope_mw"].isna().any():
        raise ValueError("reported hydro peak envelope has unfillable endpoint gaps")
    result.loc[missing_mask, "classification"] = (
        "model_only_interpolation_not_observation"
    )

    observed_energy_fraction = observed["reported_peak_energy_fraction"].dropna()
    summary = {
        "station_rows": int(len(data)),
        "station_names": int(data["station_name_as_reported"].nunique()),
        "observed_days": int(len(observed)),
        "interpolated_missing_days": int(missing_mask.sum()),
        "reported_peak_rows_fraction": float(
            data["reported_maximum_output_mw"].notna().mean()
        ),
        "reported_peak_energy_fraction_min": float(
            observed_energy_fraction.min()
        ),
        "reported_peak_energy_fraction_median": float(
            observed_energy_fraction.median()
        ),
        "reported_peak_energy_fraction_p90": float(
            observed_energy_fraction.quantile(0.90)
        ),
        "observed_envelope_mw_min": float(
            observed["reported_peak_envelope_mw"].min()
        ),
        "observed_envelope_mw_median": float(
            observed["reported_peak_envelope_mw"].median()
        ),
        "observed_envelope_mw_p90": float(
            observed["reported_peak_envelope_mw"].quantile(0.90)
        ),
        "observed_envelope_mw_max": float(
            observed["reported_peak_envelope_mw"].max()
        ),
        "missing_dates": [d.strftime("%Y-%m-%d") for d in actual_missing],
    }
    return result, summary


def run_reported_peak_envelope(
    root: Path,
    *,
    hours: int = 8760,
) -> dict[str, Any]:
    """Run the three-way flat / reported-peak / installed-cap hydro bracket."""
    if not 24 <= hours <= 8760 or hours % 24:
        raise ValueError("hours must be whole days between 24 and 8760")

    config = load_reported_peak_envelope_config(
        root / "configs/full_pypsa_hydro_reported_peak_v0_4.yaml"
    )
    load_hydro_flexibility_config(
        root / "configs/full_pypsa_hydro_flexibility_v0_3.yaml"
    )
    suite = load_proxy_adequacy_suite(
        root / "configs/full_pypsa_proxy_adequacy_v0_2.yaml"
    )
    selection = load_v02_selection(
        root / "configs/research_input_selection_v0_2.yaml"
    )
    qa = json.loads((root / config["qa"]).read_text(encoding="utf-8"))

    bracket = run_hydro_flexibility_bracket(root, hours=hours)
    hourly, metadata, observed_capacity = _load_inputs(root, suite)
    hourly = hourly.iloc[:hours].copy()
    metadata["modeled_window_hours"] = hours
    metadata["full_financial_year"] = hours == 8760

    station_daily = pd.read_csv(root / config["station_source"])
    full_dates = pd.DatetimeIndex(pd.to_datetime(hourly["date"].unique()))
    expected_missing_for_window = [
        value
        for value in qa["missing_dates"]
        if pd.Timestamp(value) in set(full_dates)
    ]
    envelope, envelope_summary = derive_reported_station_peak_envelope(
        station_daily,
        full_dates,
        expected_missing_dates=expected_missing_for_window,
    )

    capacities = observed_capacity["electricity"]["capacity_mix_mw"]
    installed_hydro_mw = float(capacities["hydel"])
    installed_nonhydro_mw = float(
        observed_capacity["electricity"]["installed_capacity_mw"]
        - installed_hydro_mw
    )
    if envelope["reported_peak_envelope_mw"].max() > installed_hydro_mw + 1e-6:
        raise ValueError("reported station envelope exceeds installed hydro capacity")

    flat_by_id = {case["id"]: case for case in bracket["flat_daily_average"]}
    upper_by_id = {
        case["id"]: case
        for case in bracket["daily_energy_redispatch_upper_bound"]
    }
    envelope_cases = []

    for case in suite["cases"]:
        assumptions = ScreeningAssumptions(
            import_limit_mw=float(case["import_limit_mw"]),
            objective_import_per_mwh=float(suite["objective"]["import_per_mwh"]),
            objective_unserved_per_mwh=float(
                suite["objective"]["unserved_per_mwh"]
            ),
        )
        network, daily_hydro_mwh = build_daily_hydro_redispatch_network(
            hourly,
            metadata,
            assumptions,
            installed_hydro_mw=installed_hydro_mw,
            installed_nonhydro_mw=installed_nonhydro_mw,
        )

        day_cap = envelope["reported_peak_envelope_mw"]
        energy_required_mwh = daily_hydro_mwh.reindex(day_cap.index.strftime("%Y-%m-%d"))
        energy_ceiling_mwh = day_cap.to_numpy(dtype=float) * 24.0
        if np.any(energy_required_mwh.to_numpy(dtype=float) > energy_ceiling_mwh + 1e-6):
            raise ValueError(
                "daily hydro energy is infeasible under reported station envelope"
            )

        hourly_cap = hourly["date"].map(
            day_cap.rename_axis("date").set_axis(
                day_cap.index.strftime("%Y-%m-%d")
            )
        )
        if hourly_cap.isna().any():
            raise ValueError("hourly hydro envelope mapping failed")
        network.generators_t.p_max_pu[HYDRO_NAME] = (
            hourly_cap.to_numpy(dtype=float) / installed_hydro_mw
        )
        network.meta["hydro_mode"] = "reported_station_peak_envelope"
        network.meta["hydro_envelope_source"] = config["station_source"]
        network.meta["hydro_envelope_interpolated_days"] = int(
            envelope_summary["interpolated_missing_days"]
        )

        status, condition = solve_daily_hydro_redispatch(
            network,
            daily_hydro_mwh,
        )
        summary = _redispatch_case_summary(
            network,
            hourly,
            daily_hydro_mwh,
            status,
            condition,
        )
        summary["id"] = case["id"]
        summary["role"] = case["role"]
        summary["import_limit_mw"] = float(case["import_limit_mw"])
        summary["daily_envelope_mw_min"] = float(day_cap.min())
        summary["daily_envelope_mw_median"] = float(day_cap.median())
        summary["daily_envelope_mw_max"] = float(day_cap.max())

        flat = flat_by_id[case["id"]]
        upper = upper_by_id[case["id"]]
        summary["unserved_change_vs_flat_mwh"] = (
            summary["unserved_energy_mwh"]
            - float(flat["unserved_energy_mwh"])
        )
        summary["unserved_change_vs_installed_upper_mwh"] = (
            summary["unserved_energy_mwh"]
            - float(upper["unserved_energy_mwh"])
        )
        if summary["unserved_energy_mwh"] > float(
            flat["unserved_energy_mwh"]
        ) + 1e-4:
            raise RuntimeError(
                "reported-peak redispatch is worse than feasible flat replay"
            )
        if summary["unserved_energy_mwh"] + 1e-4 < float(
            upper["unserved_energy_mwh"]
        ):
            raise RuntimeError(
                "reported-peak result beats the less-constrained installed upper bound"
            )
        envelope_cases.append(summary)

    return {
        "classification": CLASSIFICATION,
        "selection_classification": selection["classification"],
        "prepared_date": config["prepared_date"],
        "period": suite["period"],
        "hours": hours,
        "full_financial_year": hours == 8760,
        "station_envelope_summary": envelope_summary,
        "flat_daily_average": bracket["flat_daily_average"],
        "reported_station_peak_envelope": envelope_cases,
        "installed_capacity_redispatch_upper_bound": bracket[
            "daily_energy_redispatch_upper_bound"
        ],
        "interpretation": config["interpretation"],
        "release": {
            "validated_hydro_dispatch": False,
            "measured_simultaneous_hydro_capability": False,
            "reservoir_model": False,
            "economic_dispatch": False,
            "probabilistic_LOLP": False,
            "capacity_expansion": False,
        },
    }
