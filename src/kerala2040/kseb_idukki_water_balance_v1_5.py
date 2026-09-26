"""Water-balance QA for official KSEB Idukki daily workbook records.

The report-date convention is tested as:
    S[t] - S[t-1] = inflow[t] - outflow[t] + residual[t]

When direct daily MCM terms exist they are preferred. Otherwise average/rate
cumecs are converted to daily volume with 0.0864 MCM per (m3/s)-day.

Residuals are diagnostic. They are not automatically named evaporation,
diversion, seepage or measurement error. Published source values are never
silently corrected.
"""
from __future__ import annotations

import math
import statistics
from datetime import date
from itertools import pairwise
from typing import Any

CUMECS_DAY_TO_MCM = 0.0864


class KSEBWaterBalanceError(ValueError):
    """Raised when records cannot support water-balance QA."""


def _flow_mcm(metrics: dict[str, Any]) -> tuple[float | None, float | None, str | None]:
    inflow = metrics.get("inflow_mcm")
    if inflow is not None:
        outflow = metrics.get("total_outflow_mcm")
        if outflow is None:
            power = metrics.get("power_house_discharge_mcm")
            spill = metrics.get("spill_mcm")
            if power is not None and spill is not None:
                outflow = power + spill
        if outflow is not None:
            return float(inflow), float(outflow), "direct_mcm"

    inflow_rate = metrics.get("inflow_cumecs")
    if inflow_rate is None:
        inflow_rate = metrics.get("average_inflow_cumecs")
    outflow_rate = metrics.get("total_outflow_cumecs")
    if outflow_rate is None:
        power = metrics.get("power_house_discharge_cumecs")
        spill = metrics.get("spill_cumecs")
        if power is not None and spill is not None:
            outflow_rate = power + spill
    if inflow_rate is not None and outflow_rate is not None:
        return (
            float(inflow_rate) * CUMECS_DAY_TO_MCM,
            float(outflow_rate) * CUMECS_DAY_TO_MCM,
            "cumecs_daily_volume_assumption",
        )
    return None, None, None


def _median_absolute_deviation(values: list[float]) -> tuple[float, float]:
    median = statistics.median(values)
    mad = statistics.median(abs(value - median) for value in values)
    return median, mad


def water_balance_qa(records: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(records, key=lambda item: item["date"])
    transitions = []
    representation_counts: dict[str, int] = {}
    conversion_checks = []

    for record in ordered:
        metrics = record["metrics"]
        if (
            metrics.get("inflow_mcm") is not None
            and metrics.get("average_inflow_cumecs") is not None
        ):
            converted = (
                float(metrics["average_inflow_cumecs"])
                * CUMECS_DAY_TO_MCM
            )
            conversion_checks.append(
                {
                    "date": record["date"],
                    "source_inflow_mcm": float(metrics["inflow_mcm"]),
                    "average_inflow_cumecs_as_mcm": converted,
                    "difference_mcm": float(metrics["inflow_mcm"]) - converted,
                }
            )

    for previous, current in pairwise(ordered):
        prev_date = previous["date"]
        cur_date = current["date"]
        if (date.fromisoformat(cur_date) - date.fromisoformat(prev_date)).days != 1:
            continue

        prev_storage = previous["metrics"].get("live_storage_mcm")
        cur_storage = current["metrics"].get("live_storage_mcm")
        if prev_storage is None or cur_storage is None:
            continue
        inflow, outflow, representation = _flow_mcm(current["metrics"])
        if inflow is None or outflow is None or representation is None:
            continue

        representation_counts[representation] = (
            representation_counts.get(representation, 0) + 1
        )
        delta_storage = float(cur_storage) - float(prev_storage)
        net_inflow = inflow - outflow
        residual = delta_storage - net_inflow
        transitions.append(
            {
                "date": cur_date,
                "previous_date": prev_date,
                "representation": representation,
                "storage_change_mcm": delta_storage,
                "inflow_mcm_equivalent": inflow,
                "outflow_mcm_equivalent": outflow,
                "net_inflow_mcm": net_inflow,
                "residual_mcm": residual,
            }
        )

    if len(transitions) < 3:
        raise KSEBWaterBalanceError(
            "At least three consecutive water-balance transitions are required"
        )

    residuals = [item["residual_mcm"] for item in transitions]
    median, mad = _median_absolute_deviation(residuals)

    # A robust source-anomaly screen. The absolute 2 MCM floor prevents tiny
    # spreadsheet rounding residuals from generating false flags; 20*MAD
    # adapts to a genuinely wider physical residual distribution.
    anomaly_threshold = max(2.0, 20.0 * mad)
    anomalies = [
        {
            **item,
            "deviation_from_median_mcm": item["residual_mcm"] - median,
        }
        for item in transitions
        if abs(item["residual_mcm"] - median) > anomaly_threshold
    ]

    conversion_abs = [
        abs(item["difference_mcm"]) for item in conversion_checks
    ]
    conversion_summary = {
        "count": len(conversion_checks),
        "median_absolute_difference_mcm": (
            statistics.median(conversion_abs) if conversion_abs else None
        ),
        "maximum_absolute_difference_mcm": (
            max(conversion_abs) if conversion_abs else None
        ),
    }

    finite = all(math.isfinite(value) for value in residuals)
    return {
        "classification": "KSEB_IDUKKI_WATER_BALANCE_QA_V1_5",
        "report_date_convention": (
            "Flow/release values on report date t are applied to the "
            "preceding storage interval S[t-1] -> S[t]."
        ),
        "cumecs_conversion_mcm_per_day": CUMECS_DAY_TO_MCM,
        "transition_count": len(transitions),
        "representation_counts": representation_counts,
        "residual_summary": {
            "median_mcm": median,
            "mad_mcm": mad,
            "mean_mcm": statistics.mean(residuals),
            "mean_absolute_mcm": statistics.mean(abs(x) for x in residuals),
            "minimum_mcm": min(residuals),
            "maximum_mcm": max(residuals),
        },
        "source_anomaly_threshold_mcm_from_median": anomaly_threshold,
        "source_anomaly_candidates": anomalies,
        "source_anomaly_count": len(anomalies),
        "mcm_vs_average_cumecs_crosscheck": conversion_summary,
        "transitions": transitions,
        "finite": finite,
        "automatic_source_corrections_applied": False,
        "residual_physical_label_assigned": False,
        "ready_for_model_input": finite and len(anomalies) == 0,
    }
