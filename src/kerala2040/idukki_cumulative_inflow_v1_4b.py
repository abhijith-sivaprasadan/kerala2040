"""Source-cumulative Idukki inflow sensitivity builder for v1.4b.

This is deliberately weaker than strict v1.4. It interprets accepted blank
Idukki daily-inflow cells as zero only after an archive-wide convention check,
then derives rejected single-day gaps from adjacent cumulative inflow accounting.
Any date that cannot be source-constrained remains explicit uncertainty.

Detailed daily reconstructed rows are private outputs and must not be committed
until source redistribution/reuse terms are resolved.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

SUITE_CLASS = (
    "full_pypsa_idukki_cumulative_inflow_v1_4b_"
    "source_informed_sensitivity_not_observed_daily_series"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_v14b_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("v1.4b classification mismatch")
    if data["source"]["missing_daily_inflow_policy"] != (
        "no_interpolation_source_convention_and_cumulative_constraints_only"
    ):
        raise ValueError("v1.4b missing-data policy changed")
    if float(data["source"]["blank_cumulative_positive_tolerance_mcm"]) <= 0:
        raise ValueError("v1.4b blank convention tolerance must be positive")
    if int(data["source"]["minimum_archive_blank_pairs_for_convention"]) < 100:
        raise ValueError("v1.4b blank convention evidence floor weakened")
    if data["release"]["strict_v1_4_source_reported_model_ready"] is not False:
        raise ValueError("v1.4b must not promote the strict v1.4 gate")
    if data["release"]["source_informed_sensitivity_ready"] is not True:
        raise ValueError("v1.4b sensitivity release flag is false")
    return data


def _source_frame(
    path: Path,
    *,
    expected_sha256: str,
    required_columns: list[str],
) -> pd.DataFrame:
    actual = sha256(path)
    if actual != expected_sha256:
        raise ValueError(
            "Private reservoir_rows.csv SHA-256 does not match the Phase-4 source"
        )
    frame = pd.read_csv(path, parse_dates=["date"], low_memory=False)
    missing = sorted(set(required_columns) - set(frame.columns))
    if missing:
        raise ValueError(f"Private source missing columns: {missing}")
    idukki = frame.loc[
        frame["reservoir"].astype(str).str.upper().eq("IDUKKI")
    ].copy()
    if idukki["date"].duplicated().any():
        raise ValueError("Duplicate Idukki rows in private source")
    return idukki.sort_values("date").set_index("date")


def audit_blank_zero_convention(
    idukki: pd.DataFrame,
    *,
    tolerance_mcm: float,
    minimum_pairs: int,
) -> dict[str, Any]:
    deltas: list[float] = []
    for date, row in idukki.iterrows():
        if pd.notna(pd.to_numeric(row["inflow_mcm_day"], errors="coerce")):
            continue
        previous = date - pd.Timedelta(days=1)
        if previous not in idukki.index or previous.month != date.month:
            continue
        current_cumulative = pd.to_numeric(
            pd.Series([row["month_inflow_mu"]]),
            errors="coerce",
        ).iloc[0]
        previous_cumulative = pd.to_numeric(
            pd.Series([idukki.loc[previous, "month_inflow_mu"]]),
            errors="coerce",
        ).iloc[0]
        if pd.isna(current_cumulative) or pd.isna(previous_cumulative):
            continue
        deltas.append(float(current_cumulative - previous_cumulative))

    if len(deltas) < minimum_pairs:
        raise ValueError(
            "Too few archive-wide blank inflow pairs to admit blank-zero convention"
        )
    arr = np.asarray(deltas, dtype=float)
    materially_positive = arr > float(tolerance_mcm)
    if materially_positive.any():
        raise ValueError(
            "Blank daily inflow has a materially positive same-month cumulative "
            "increment; do not normalize blanks to zero"
        )

    return {
        "direct_blank_cumulative_pairs": len(arr),
        "maximum_blank_cumulative_increment_mcm": float(arr.max()),
        "minimum_blank_cumulative_increment_mcm": float(arr.min()),
        "zeroish_pairs_within_tolerance": int(
            (np.abs(arr) <= float(tolerance_mcm)).sum()
        ),
        "negative_correction_pairs": int(
            (arr < -float(tolerance_mcm)).sum()
        ),
        "materially_positive_pairs": int(materially_positive.sum()),
        "blank_zero_convention_admitted_for_sensitivity": True,
    }


def build_source_informed_inflow_scenarios(
    private_source: Path,
    suite: dict[str, Any],
    *,
    private_output_dir: Path | None = None,
) -> dict[str, Any]:
    source = suite["source"]
    idukki = _source_frame(
        private_source,
        expected_sha256=source["expected_sha256"],
        required_columns=list(source["required_columns"]),
    )
    tolerance = float(source["blank_cumulative_positive_tolerance_mcm"])
    convention = audit_blank_zero_convention(
        idukki,
        tolerance_mcm=tolerance,
        minimum_pairs=int(source["minimum_archive_blank_pairs_for_convention"]),
    )

    period = suite["pilot_period"]
    days = pd.date_range(period["start"], period["dispatch_end"], freq="D")
    pilot = idukki.reindex(days)
    raw_inflow = pd.to_numeric(pilot["inflow_mcm_day"], errors="coerce")
    valid_observed = raw_inflow.notna() & raw_inflow.ge(0) & raw_inflow.le(300)
    row_present = pilot["reservoir"].notna()
    accepted_blank = row_present & raw_inflow.isna()
    rejected_row = ~row_present

    normalized = raw_inflow.copy()
    input_class = pd.Series("source_reported_daily_inflow", index=days, dtype=object)
    normalized.loc[accepted_blank] = 0.0
    input_class.loc[accepted_blank] = "source_blank_zero_convention_v14b"

    rejected_derived = 0
    rejected_derived_sum_mcm = 0.0
    unresolved: list[pd.Timestamp] = []
    for date in days[rejected_row.to_numpy()]:
        previous = date - pd.Timedelta(days=1)
        following = date + pd.Timedelta(days=1)
        same_month = (
            previous.month == date.month == following.month
            and previous.year == date.year == following.year
        )
        if not same_month or previous not in pilot.index or following not in pilot.index:
            unresolved.append(date)
            continue

        previous_cumulative = pd.to_numeric(
            pd.Series([pilot.loc[previous, "month_inflow_mu"]]),
            errors="coerce",
        ).iloc[0]
        following_cumulative = pd.to_numeric(
            pd.Series([pilot.loc[following, "month_inflow_mu"]]),
            errors="coerce",
        ).iloc[0]
        following_inflow = normalized.loc[following]
        if (
            pd.isna(previous_cumulative)
            or pd.isna(following_cumulative)
            or pd.isna(following_inflow)
        ):
            unresolved.append(date)
            continue

        candidate = float(
            following_cumulative
            - previous_cumulative
            - float(following_inflow)
        )
        if candidate < -tolerance or candidate > 300 + tolerance:
            unresolved.append(date)
            continue
        candidate = max(0.0, candidate)
        normalized.loc[date] = candidate
        input_class.loc[date] = "adjacent_cumulative_derived_rejected_date_v14b"
        rejected_derived += 1
        rejected_derived_sum_mcm += candidate

    if len(unresolved) != 1:
        raise ValueError(
            "v1.4b expected exactly one source-unconstrained pilot date after "
            f"cumulative recovery, got {[d.strftime('%Y-%m-%d') for d in unresolved]}"
        )
    unresolved_date = unresolved[0]

    observed_values = raw_inflow.loc[valid_observed]
    november = observed_values.loc[
        (observed_values.index.year == unresolved_date.year)
        & (observed_values.index.month == unresolved_date.month)
    ]
    if november.empty:
        raise ValueError("No observed same-month inflow values for unresolved-date bracket")

    brackets = {
        "nov30_zero_lower": 0.0,
        "nov30_same_month_median": float(november.median()),
        "nov30_same_month_p95": float(november.quantile(0.95)),
        "nov30_same_month_max": float(november.max()),
        "nov30_pilot_max_stress": float(observed_values.max()),
    }

    base_without_unresolved = float(normalized.dropna().sum())
    scenarios: dict[str, dict[str, float]] = {}
    if private_output_dir is not None:
        private_output_dir.mkdir(parents=True, exist_ok=True)

    for scenario_id, value in brackets.items():
        series = normalized.copy()
        classes = input_class.copy()
        series.loc[unresolved_date] = value
        classes.loc[unresolved_date] = f"unresolved_date_sensitivity_{scenario_id}"
        if series.isna().any():
            raise RuntimeError("v1.4b scenario still contains missing inflow")
        scenarios[scenario_id] = {
            "unresolved_date_assumed_inflow_mcm": value,
            "pilot_inflow_total_mcm": float(series.sum()),
            "unresolved_water_energy_equivalent_gwh_at_1470_mwh_per_mcm": (
                value * 1470.0 / 1000.0
            ),
        }
        if private_output_dir is not None:
            pd.DataFrame({
                "date": days.strftime("%Y-%m-%d"),
                "inflow_mcm_day": series.to_numpy(dtype=float),
                "input_class": classes.to_numpy(dtype=object),
            }).to_csv(
                private_output_dir / f"{scenario_id}.csv",
                index=False,
            )

    return {
        "classification": SUITE_CLASS,
        "private_source_sha256": sha256(private_source),
        "pilot": {
            "days": len(days),
            "source_reported_daily_inflow_days": int(valid_observed.sum()),
            "accepted_blank_zero_convention_days": int(accepted_blank.sum()),
            "rejected_source_rows": int(rejected_row.sum()),
            "rejected_dates_recovered_by_adjacent_cumulative": rejected_derived,
            "rejected_cumulative_derived_sum_mcm": rejected_derived_sum_mcm,
            "source_unconstrained_dates_after_recovery": [
                unresolved_date.strftime("%Y-%m-%d")
            ],
            "base_inflow_total_mcm_excluding_unresolved_date": (
                base_without_unresolved
            ),
        },
        "archive_blank_convention": convention,
        "unresolved_date_bracket": {
            "date": unresolved_date.strftime("%Y-%m-%d"),
            "same_month_observed_days": int(len(november)),
            "same_month_observed_median_mcm_day": float(november.median()),
            "same_month_observed_p95_mcm_day": float(november.quantile(0.95)),
            "same_month_observed_max_mcm_day": float(november.max()),
            "pilot_observed_max_mcm_day": float(observed_values.max()),
        },
        "scenarios": scenarios,
        "interpretation": {
            "strict_v1_4_source_reported_series_complete": False,
            "blank_zero_is_raw_observation": False,
            "cumulative_derived_rejected_dates_are_raw_observations": False,
            "v1_4b_is_sensitivity_only": True,
            "daily_private_scenarios_safe_to_publish": False,
        },
    }


def write_public_qa(result: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
