"""Provenance-gated hourly PyPSA *screening*, not measured hourly calibration.

Uses an explicitly labelled FY2024-25 hourly demand reconstruction, *observed*
daily SLDC source-energy constraints, and optional fixed solar/storage additions.
No assumed price, transfer limit or unverified reservoir relationship is silently
promoted to an observed fact or a validated Kerala 2040 investment result.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd

START = "2024-04-01"
END = "2025-03-31"
PROXY_CLASS = "proxy_reconstruction_not_measured_telemetry"
OBSERVED_CLASS = "official_observed_reference"
SOURCE_URL = "https://sldckerala.com/index.php?id=1"


@dataclass(frozen=True)
class ScreeningAssumptions:
    """Explicit *sensitivity*, not historical rating or validated project costing."""

    import_limit_mw: float
    additional_solar_mw: float = 0.0
    battery_power_mw: float = 0.0
    battery_duration_h: float = 4.0
    battery_round_trip_efficiency: float = 0.88
    objective_import_per_mwh: float = 1.0
    objective_unserved_per_mwh: float = 10000.0

    def validate(self) -> None:
        values = asdict(self)
        if any(not np.isfinite(v) for v in values.values()):
            raise ValueError("All screening parameters must be finite")
        if self.import_limit_mw <= 0:
            raise ValueError("Specify a positive *assumed*, not observed, import limit MW")
        if self.additional_solar_mw < 0 or self.battery_power_mw < 0:
            raise ValueError("Added capacities cannot be negative")
        if self.battery_duration_h <= 0 or not 0 < self.battery_round_trip_efficiency <= 1:
            raise ValueError("Invalid battery duration or round-trip efficiency")
        if self.objective_import_per_mwh <= 0:
            raise ValueError("Import penalty must be positive")
        if self.objective_unserved_per_mwh <= self.objective_import_per_mwh:
            raise ValueError("Unserved-load penalty must exceed import penalty")


def prepare_inputs(
    load_proxy: dict[str, Any],
    daily: pd.DataFrame,
    *,
    expected_missing_dates: list[str],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Validate entire fiscal year *before* taking a shorter smoke-test slice.

    Daily hydro/non-hydro energy is linearly interpolated only on the 11 dates
    without source reports, and is flagged on every derived hourly row.
    Generation for each observed date is held at its reported daily average MW;
    this does not assert measured intra-day plant operation or reservoir dispatch.
    """
    if load_proxy.get("classification") != PROXY_CLASS:
        raise ValueError("Hourly input must retain explicit not-measured classification")
    if load_proxy.get("timezone") != "Asia/Kolkata" or load_proxy.get("interval") != "1h":
        raise ValueError("Expected hourly Asia/Kolkata proxy timestamps")
    hourly = pd.DataFrame(load_proxy["records"])
    required_hourly = {"timestamp", "load_mw", "daily_energy_imputed", "classification"}
    if not required_hourly.issubset(hourly):
        raise ValueError(f"Hourly proxy missing {sorted(required_hourly - set(hourly))}")
    times = pd.to_datetime(hourly["timestamp"], utc=True)
    local = times.dt.tz_convert("Asia/Kolkata")
    if not local.is_monotonic_increasing or local.duplicated().any():
        raise ValueError("Hourly proxy must be sorted with unique timestamps")
    if len(hourly) != 8760 or not (times.diff().iloc[1:] == pd.Timedelta(hours=1)).all():
        raise ValueError("Hourly proxy must contain 8760 consecutive hours")
    if local.iloc[0].strftime("%Y-%m-%d %H") != START + " 00":
        raise ValueError("Incorrect financial-year start")
    if local.iloc[-1].strftime("%Y-%m-%d %H") != END + " 23":
        raise ValueError("Incorrect financial-year end")
    if set(hourly["classification"].unique()) != {"proxy_reconstruction"}:
        raise ValueError("Hourly record classification cannot be measured")
    hourly["load_mw"] = pd.to_numeric(hourly["load_mw"], errors="coerce")
    if not np.isfinite(hourly["load_mw"]).all() or (hourly["load_mw"] <= 0).any():
        raise ValueError("Hourly load must be finite and positive")
    hourly["date"] = local.dt.strftime("%Y-%m-%d")
    hourly["snapshot_ist_naive"] = local.dt.tz_localize(None)

    columns = {"date", "status", "hydro_mu", "internal_generation_mu", "net_import_mu", "consumption_mu"}
    if not columns.issubset(daily):
        raise ValueError(f"Daily SLDC table missing {sorted(columns - set(daily))}")
    work = daily[list(columns)].copy()
    work["date"] = pd.to_datetime(work["date"]).dt.strftime("%Y-%m-%d")
    if work.date.duplicated().any() or len(work) != 365:
        raise ValueError("Expected exactly one record per 365 fiscal-year dates")
    work = work.sort_values("date").set_index("date")
    if work.index.tolist() != pd.date_range(START, END, freq="D").strftime("%Y-%m-%d").tolist():
        raise ValueError("Daily dates do not cover the full financial year")
    missing = work.index[work.status != "observed"].tolist()
    if missing != sorted(expected_missing_dates) or len(missing) != 11:
        raise ValueError("Missing-day mask disagrees with SLDC QA report")
    fields = ["hydro_mu", "internal_generation_mu", "net_import_mu", "consumption_mu"]
    work[fields] = work[fields].apply(pd.to_numeric, errors="coerce")
    observed = work.loc[work.status == "observed", fields]
    if not np.isfinite(observed).all().all() or work.loc[missing, fields].notna().any().any():
        raise ValueError("Observed values must be finite; unreported dates must remain null")
    if (observed[fields] < 0).any().any() or (observed.consumption_mu <= 0).any():
        raise ValueError("Negative reported energy is outside this model's import-only scope")
    if ((observed.internal_generation_mu - observed.hydro_mu) < -1e-5).any():
        raise ValueError("Hydro is greater than total internal generation")
    if (observed.internal_generation_mu + observed.net_import_mu - observed.consumption_mu).abs().max() > 0.001:
        raise ValueError("Observed daily electricity accounting does not close")
    hourly_daily_mu = hourly.groupby("date").load_mw.sum() / 1000
    observed_proxy_residual = (
        hourly_daily_mu.loc[observed.index] - observed.consumption_mu
    ).abs().max()
    if observed_proxy_residual > 1e-4:
        raise ValueError("Proxy does not conserve measured daily energy")
    imputed_dates = hourly.groupby("date").daily_energy_imputed.first()
    if imputed_dates[imputed_dates].index.tolist() != missing:
        raise ValueError("Hourly proxy missing-date flags differ from SLDC QA")
    if not hourly.groupby("date").daily_energy_imputed.nunique().eq(1).all():
        raise ValueError("Hourly imputation flags vary within a date")

    filled = work[fields].interpolate(method="linear", limit_area="inside")
    if filled.isna().any().any():
        raise ValueError("Cannot interpolate leading/trailing missing daily energies")
    filled["nonhydro_mu"] = filled.internal_generation_mu - filled.hydro_mu
    if (filled.nonhydro_mu < -1e-5).any():
        raise ValueError("Interpolated hydro exceeds total internal generation")
    # Explicitly do not overwrite the source daily CSV: interpolation is model-only.
    hourly["hydro_fixed_mw"] = hourly.date.map(filled.hydro_mu).astype(float) * 1000 / 24
    hourly["nonhydro_fixed_mw"] = hourly.date.map(filled.nonhydro_mu).astype(float) * 1000 / 24
    hourly["generation_daily_imputed"] = hourly.date.isin(missing)
    hourly["observed_import_mu"] = hourly.date.map(work.net_import_mu)
    if ((hourly.hydro_fixed_mw + hourly.nonhydro_fixed_mw) > hourly.load_mw + 1e-6).any():
        raise ValueError("Fixed daily-average generation exceeds proxy load in at least one hour")
    meta = {
        "classification": "scenario_screening_using_proxy_not_measured_hourly_dispatch",
        "load_classification": PROXY_CLASS,
        "source_url": SOURCE_URL,
        "period": f"{START} to {END}",
        "timezone": "Asia/Kolkata; snapshots stored as local naive for PyPSA",
        "observed_days": 354,
        "imputed_days": 11,
        "missing_dates": missing,
        "observed_days_energy_mu": {key: float(observed[key].sum()) for key in fields},
        "hourly_proxy_energy_mu": float(hourly.load_mw.sum() / 1000),
        "observed_proxy_max_daily_residual_mu": float(observed_proxy_residual),
        "generation_profile": "daily reported hydro and residual nonhydro as fixed 24-hour averages; NOT hourly observed",
        "imputation": "model-only linear interpolation on 11 days with no SLDC report",
        "import_bound": "explicit screening assumption, NOT observed interface transfer capability",
        "reservoir_model": "none; source hydro fixed to reported daily energy; NO cascade, inflow or rule curves imposed",
        "objective_units": "abstract screening weights, NOT INR or audited historical price",
        "interpretation": "model prototyping/sensitivity only; not measured hourly validation or a 2040 optimisation",
    }
    return hourly, meta


def align_solar_profile(solar: pd.DataFrame, snapshots: pd.DatetimeIndex) -> np.ndarray:
    """Use existing NASA POWER representative-point availability; reject holes."""
    needed = {"timestamp_ist", "solar_p_max_pu", "classification"}
    if not needed.issubset(solar):
        raise ValueError(f"Solar profile missing {sorted(needed - set(solar))}")
    if set(solar["classification"].dropna().unique()) != {"modelled_resource_profile"}:
        raise ValueError("Solar series must be clearly classified as modelled resource")
    index = pd.to_datetime(solar.timestamp_ist, utc=True).dt.tz_convert("Asia/Kolkata")
    values = pd.to_numeric(solar.solar_p_max_pu, errors="coerce")
    raw = pd.Series(values.to_numpy(dtype=float), index=pd.DatetimeIndex(index).tz_localize(None))
    if raw.index.duplicated().any():
        raise ValueError("Duplicate solar timestamps")
    selected = raw.reindex(snapshots)
    if selected.isna().any() or not selected.between(0, 1).all():
        raise ValueError("Solar resource is missing hours or has values outside [0,1]")
    return selected.to_numpy()


def build_hourly_screening_network(
    hourly: pd.DataFrame,
    metadata: dict[str, Any],
    assumptions: ScreeningAssumptions,
    *,
    installed_hydro_mw: float,
    installed_nonhydro_mw: float,
    solar: pd.DataFrame | None = None,
):
    """Construct hourly PyPSA LP with explicit proxy + input provenance.

    Imported supply and unserved energy are free operational decisions subject
    to *assumed* import bound. Solar and BESS are fixed scenario additions; no
    cost-based capacity expansion occurs in this model.
    """
    assumptions.validate()
    if not metadata.get("classification", "").startswith("scenario_screening_using_proxy"):
        raise ValueError("Cannot relabel a proxy-based screening as observed")
    if hourly.empty or hourly.snapshot_ist_naive.duplicated().any():
        raise ValueError("Nonempty unique hourly timestamps are required")
    if hourly["generation_daily_imputed"].ne(hourly["daily_energy_imputed"]).any():
        raise ValueError("Generation and demand must share the missing-day mask")
    if installed_hydro_mw <= 0 or installed_nonhydro_mw <= 0:
        raise ValueError("Installed capacities must be positive")
    if hourly.hydro_fixed_mw.max() > installed_hydro_mw + 1e-6:
        raise ValueError("Daily-average hydro exceeds official installed hydro capacity")
    if hourly.nonhydro_fixed_mw.max() > installed_nonhydro_mw + 1e-6:
        raise ValueError("Daily-average nonhydro exceeds official installed residual capacity")
    if assumptions.additional_solar_mw and solar is None:
        raise ValueError("Additional solar requires an explicitly modelled weather resource profile")
    import pypsa

    snapshots = pd.DatetimeIndex(hourly.snapshot_ist_naive)
    network = pypsa.Network()
    network.set_snapshots(snapshots)
    network.snapshot_weightings.loc[:, :] = 1.0
    network.add("Bus", "kerala")
    for carrier in ("hydro", "nonhydro", "interstate_import", "unserved", "additional_solar", "bess"):
        network.add("Carrier", carrier)
    network.add("Load", "reconstructed_load", bus="kerala", p_set=hourly.load_mw.to_numpy())
    for name, carrier, fixed_mw, capacity in (
        ("fixed_daily_hydro", "hydro", hourly.hydro_fixed_mw, installed_hydro_mw),
        ("fixed_daily_nonhydro", "nonhydro", hourly.nonhydro_fixed_mw, installed_nonhydro_mw),
    ):
        pu = fixed_mw.to_numpy(dtype=float) / capacity
        network.add(
            "Generator", name, bus="kerala", carrier=carrier, p_nom=capacity,
            p_min_pu=pu, p_max_pu=pu, marginal_cost=0,
        )
    network.add(
        "Generator", "screened_import", bus="kerala", carrier="interstate_import",
        p_nom=assumptions.import_limit_mw, marginal_cost=assumptions.objective_import_per_mwh,
    )
    network.add(
        "Generator", "unserved_load", bus="kerala", carrier="unserved",
        p_nom=max(float(hourly.load_mw.max()), 1.0),
        marginal_cost=assumptions.objective_unserved_per_mwh,
    )
    if assumptions.additional_solar_mw:
        pu = align_solar_profile(solar, snapshots)
        network.add(
            "Generator", "added_solar_sensitivity", bus="kerala", carrier="additional_solar",
            p_nom=assumptions.additional_solar_mw, p_max_pu=pu,
            marginal_cost=0,
        )
    if assumptions.battery_power_mw:
        efficiency = assumptions.battery_round_trip_efficiency**0.5
        network.add(
            "StorageUnit", "added_bess_sensitivity", bus="kerala", carrier="bess",
            p_nom=assumptions.battery_power_mw, max_hours=assumptions.battery_duration_h,
            efficiency_store=efficiency, efficiency_dispatch=efficiency,
            cyclic_state_of_charge=True, marginal_cost=0,
        )
    network.meta = {**metadata, "assumptions": asdict(assumptions), "hours_in_run": len(hourly)}
    return network


def solve_hourly_screening(network) -> tuple[str, str]:
    """Solve with HiGHS; never mark infeasible or unbounded as valid results."""
    status, condition = network.optimize(solver_name="highs")
    if status != "ok" or condition != "optimal":
        raise RuntimeError(f"PyPSA HiGHS unsuccessful: {status} / {condition}")
    return status, condition


def dispatch_summary(network, hourly: pd.DataFrame, status: str, condition: str) -> dict[str, Any]:
    """Separate observed SLDC evidence from scenario-derived hourly outcomes."""
    if status != "ok" or condition != "optimal":
        raise ValueError("Cannot report a non-optimal solve as a result")
    dispatch = network.generators_t.p
    load = network.loads_t.p_set["reconstructed_load"].to_numpy(dtype=float)
    known = ["fixed_daily_hydro", "fixed_daily_nonhydro", "screened_import", "unserved_load"]
    solar = dispatch["added_solar_sensitivity"].to_numpy() if "added_solar_sensitivity" in dispatch else np.zeros(len(load))
    storage = (network.storage_units_t.p["added_bess_sensitivity"].to_numpy()
               if "added_bess_sensitivity" in network.storage_units.index else np.zeros(len(load)))
    rhs = sum(dispatch[n].to_numpy() for n in known) + solar + storage
    residual = float(np.max(np.abs(rhs - load)))
    if residual > 1e-3:
        raise RuntimeError(f"Solved hourly power balance residual {residual} MW")
    total = float(load.sum())
    net_import = float(dispatch.screened_import.sum())
    unserved = float(dispatch.unserved_load.sum())
    return {
        **network.meta,
        "solver": "highs",
        "solver_status": status,
        "solver_condition": condition,
        "load_mwh_proxy": total,
        "imports_mwh_modelled": net_import,
        "imports_share_modelled": net_import / total,
        "unserved_mwh_modelled": unserved,
        "unserved_pct_modelled": 100 * unserved / total,
        "added_solar_generation_mwh_modelled": float(solar.sum()),
        "battery_net_discharge_mwh_modelled": float(storage.sum()),
        "max_abs_hourly_balance_residual_mw": residual,
        "measured_hourly_telemetry_used": False,
        "cost_optimal_2040_result": False,
        "notes": [
            "Existing in-state generation is a daily-average replay, not hourly plant telemetry.",
            "Only added solar capacity uses resource availability; observed nonhydro already contains reported solar.",
            "Annual totals include model-only interpolation for 11 unavailable dates; do not compare directly with 354-day observed totals.",
            "No validated reservoir cascade, import transfer capability or harmonised techno-economic costs.",
            "Objective uses arbitrary screening weights and must not be reported in INR.",
        ],
    }
