"""Validation and annualisation for the v0.5 research cost/finance benchmark."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

CLASSIFICATION = "research_cost_finance_selection_not_validated_kerala_tariff"


def annuity(rate: float, lifetime_years: int) -> float:
    """Return the standard annual capital-recovery factor."""
    if not 0 < rate < 1:
        raise ValueError("discount rate must be between zero and one")
    if lifetime_years <= 0:
        raise ValueError("lifetime must be positive")
    return rate / (1 - (1 + rate) ** (-lifetime_years))


def load_cost_finance(path: Path) -> dict[str, Any]:
    """Load and fail closed on the deliberately narrow v0.5 admission boundary."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != CLASSIFICATION:
        raise ValueError("cost/finance classification mismatch")

    selection = data["selection"]
    if selection["model_year"] != 2030:
        raise ValueError("v0.5 only admits a 2030 research benchmark")
    if selection["price_basis"] != "real_2021_22_INR":
        raise ValueError("v0.5 price basis must remain real 2021-22 INR")
    if selection["inflation_escalation_applied"] is not False:
        raise ValueError("CEA capex must not be silently inflated")

    rate = float(selection["discount_rate"]["pct"]) / 100.0
    if abs(rate - 0.0908) > 1e-12:
        raise ValueError("CERC research discount rate changed")

    expected = {
        "solar_pv": (41000.0, 0.01, 25),
        "wind_onshore": (60000.0, 0.01, 25),
        "bess_4h": (47200.0, 0.01, 14),
    }
    technologies = selection["technologies"]
    derived = data["derived"]["annualized_cost_inr_per_kw_year"]
    for tech, (capex, fixed_om, life) in expected.items():
        row = technologies[tech]
        capex_key = (
            "capex_inr_per_kw_power_at_4h"
            if tech == "bess_4h"
            else "capex_inr_per_kw"
        )
        if float(row[capex_key]) != capex:
            raise ValueError(f"{tech} capex changed")
        if float(row["fixed_om_pct_capex_per_year"]) / 100.0 != fixed_om:
            raise ValueError(f"{tech} fixed O&M changed")
        if int(row["lifetime_years"]) != life:
            raise ValueError(f"{tech} lifetime changed")
        calculated = capex * (annuity(rate, life) + fixed_om)
        if abs(float(derived[tech]) - calculated) > 1e-8:
            raise ValueError(f"{tech} annualized cost is inconsistent")

    bess = technologies["bess_4h"]
    if bess["max_hours"] != 4 or float(bess["round_trip_efficiency"]) != 0.88:
        raise ValueError("BESS duration/efficiency changed")
    if bess["split_power_energy_capex_available"] is not False:
        raise ValueError("v0.5 must not fabricate a BESS power/energy capex split")
    if technologies["pumped_storage"]["admitted_for_generic_expansion"] is not False:
        raise ValueError("generic pumped-storage expansion must remain blocked")

    release = data["release"]
    if release["research_2030_cost_finance_benchmark"] is not True:
        raise ValueError("research cost benchmark is not released")
    for key in (
        "economic_dispatch_with_import_prices",
        "capacity_expansion_2030",
        "capacity_expansion_2035_2040",
        "validated_cost_case",
    ):
        if release[key] is not False:
            raise ValueError(f"v0.5 incorrectly enables {key}")

    return data
