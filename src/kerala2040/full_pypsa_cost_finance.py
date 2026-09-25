"""Cost/finance harmonisation for the bounded Full-PyPSA v0.5 research package."""
from __future__ import annotations

from math import isclose, sqrt
from pathlib import Path
from typing import Any

import yaml

SUITE_CLASS = "full_pypsa_cost_finance_research_assumption_v0_5_not_validated_kerala_costs"


def annuity(rate: float, lifetime_years: int) -> float:
    """Return the standard capital-recovery factor."""
    if rate < 0:
        raise ValueError("discount rate must be non-negative")
    if lifetime_years <= 0:
        raise ValueError("lifetime must be positive")
    if rate == 0:
        return 1.0 / lifetime_years
    return rate / (1.0 - (1.0 + rate) ** (-lifetime_years))


def annualised_cost_inr_per_kw_year(
    capex_inr_per_kw: float,
    *,
    discount_rate: float,
    lifetime_years: int,
    fixed_om_fraction_capex_per_year: float,
) -> float:
    """Annualise capex and add fixed O&M on the same real-price basis."""
    if capex_inr_per_kw <= 0:
        raise ValueError("capex must be positive")
    if fixed_om_fraction_capex_per_year < 0:
        raise ValueError("fixed O&M fraction must be non-negative")
    return capex_inr_per_kw * (
        annuity(discount_rate, lifetime_years) + fixed_om_fraction_capex_per_year
    )


def load_cost_finance_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("cost/finance suite classification mismatch")

    basis = data["price_basis"]
    if basis["currency"] != "INR" or basis["basis"] != "real_2021_22_INR":
        raise ValueError("v0.5 must stay on the declared real 2021-22 INR basis")
    if basis.get("inflation_applied") is not False:
        raise ValueError("v0.5 must not silently inflate the CEA cost basis")

    finance = data["finance"]
    if not isclose(float(finance["discount_rate_real_fraction"]), 0.0908, abs_tol=1e-12):
        raise ValueError("unexpected v0.5 research discount-rate benchmark")
    if not isclose(
        float(finance["normative_debt_fraction"]) + float(finance["normative_equity_fraction"]),
        1.0,
        abs_tol=1e-12,
    ):
        raise ValueError("normative debt/equity shares must sum to one")

    tech = data["research_2030"]
    if float(tech["solar_pv"]["capex_inr_per_kw"]) != 41000:
        raise ValueError("solar 2030 benchmark changed")
    if float(tech["wind_onshore"]["capex_inr_per_kw"]) != 60000:
        raise ValueError("wind benchmark changed")

    bess = tech["bess_4h"]
    if [float(x) for x in bess["capex_inr_per_kw_bracket"]] != [47200.0, 82200.0]:
        raise ValueError("BESS published cost bracket changed")
    rte = float(bess["round_trip_efficiency"])
    charge = float(bess["charge_efficiency_symmetric"])
    discharge = float(bess["discharge_efficiency_symmetric"])
    if not isclose(charge, sqrt(rte), rel_tol=0, abs_tol=1e-12):
        raise ValueError("BESS charge efficiency is not the symmetric sqrt(RTE) split")
    if not isclose(charge * discharge, rte, rel_tol=0, abs_tol=1e-12):
        raise ValueError("BESS charge/discharge efficiencies do not reproduce RTE")

    psp = tech["pumped_storage"]
    if psp["capex_inr_per_kw"] is not None or psp["expansion_cost_admitted_for_research"] is not False:
        raise ValueError("site-specific PSP expansion must remain blocked")

    admission = data["model_year_admission"]
    if admission[2030]["cost_finance_harmonised_for_research"] is not True:
        raise ValueError("2030 research cost package not admitted")
    for year in (2035, 2040):
        if admission[year]["cost_finance_harmonised_for_research"] is not False:
            raise ValueError("post-2030 cost extrapolation must remain blocked")

    release = data["release"]
    if release["capacity_expansion_research_2030_ready"] is not False:
        raise ValueError("v0.5 must not release capacity expansion by itself")
    if release["validated_costs"] is not False:
        raise ValueError("research benchmarks must not be labelled validated Kerala costs")
    return data


def build_cost_finance_summary(data: dict[str, Any]) -> dict[str, Any]:
    rate = float(data["finance"]["discount_rate_real_fraction"])
    tech = data["research_2030"]

    def annualised(item: dict[str, Any], capex: float | None = None) -> float:
        selected_capex = float(item["capex_inr_per_kw"] if capex is None else capex)
        return annualised_cost_inr_per_kw_year(
            selected_capex,
            discount_rate=rate,
            lifetime_years=int(item["lifetime_years"]),
            fixed_om_fraction_capex_per_year=float(
                item["fixed_om_fraction_capex_per_year"]
            ),
        )

    bess = tech["bess_4h"]
    low, high = [float(x) for x in bess["capex_inr_per_kw_bracket"]]
    return {
        "classification": SUITE_CLASS,
        "price_basis": data["price_basis"]["basis"],
        "discount_rate_real_fraction": rate,
        "annualised_2030_inr_per_kw_year": {
            "solar_pv": annualised(tech["solar_pv"]),
            "wind_onshore": annualised(tech["wind_onshore"]),
            "bess_4h_low": annualised(bess, low),
            "bess_4h_high": annualised(bess, high),
        },
        "bess_4h": {
            "duration_hours": int(bess["duration_hours"]),
            "round_trip_efficiency": float(bess["round_trip_efficiency"]),
            "charge_efficiency_symmetric": float(bess["charge_efficiency_symmetric"]),
            "discharge_efficiency_symmetric": float(bess["discharge_efficiency_symmetric"]),
        },
        "pumped_storage_expansion_ready": False,
        "capacity_expansion_research_2030_ready": False,
        "validated_costs": False,
    }
