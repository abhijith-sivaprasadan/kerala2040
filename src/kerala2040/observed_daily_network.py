"""Observed-detail FY2024-25 Kerala PyPSA network from public SLDC daily reports.

This network is an evidence replay, not a chronological dispatch reconstruction.
Each snapshot represents one observed reporting day and carries 24 h of weight.
Station and interface rows are replayed at their daily-average MW values. Missing
station rows are *not* interpreted as observed zero energy: their unallocated
share remains in an explicit residual-hydro generator tied to the published
aggregate hydro total.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

import numpy as np
import pandas as pd

_REQUIRED_DAILY = {
    "date",
    "status",
    "hydro_mu",
    "internal_generation_mu",
    "net_import_mu",
    "consumption_mu",
}
_REQUIRED_HYDRO = {"date", "station_name_as_reported", "generation_mu"}
_REQUIRED_IMPORT = {"date", "interface_name_as_reported", "import_mu"}


def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{label} missing required columns: {missing}")


def _slug(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip()).strip("_").lower()
    return text or "unnamed"


def _prepare_daily(daily: pd.DataFrame) -> pd.DataFrame:
    _require_columns(daily, _REQUIRED_DAILY, "daily")
    work = daily.copy()
    work["date"] = pd.to_datetime(work["date"], errors="raise").dt.normalize()
    work = work.loc[work["status"].eq("observed")].copy()
    work = work.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    if work.empty:
        raise ValueError("no observed daily rows")

    numeric = ["hydro_mu", "internal_generation_mu", "net_import_mu", "consumption_mu"]
    work[numeric] = work[numeric].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(work[numeric]).all().all():
        raise ValueError("observed daily rows must have finite system-energy values")
    if (work["consumption_mu"] <= 0).any():
        raise ValueError("observed daily consumption must be positive")
    if (work["net_import_mu"] < -1e-9).any():
        raise ValueError("negative aggregate net-import days require explicit export modelling")
    if (work["internal_generation_mu"] + work["net_import_mu"] - work["consumption_mu"]).abs().max() > 0.001:
        raise ValueError("daily system balance exceeds 0.001 MU")
    if (work["hydro_mu"] - work["internal_generation_mu"] > 0.001).any():
        raise ValueError("aggregate hydro exceeds aggregate internal generation")
    return work


def _normalised_profile(values_mw: pd.Series) -> tuple[float, np.ndarray]:
    p_nom = max(float(values_mw.max()), 1e-9)
    return p_nom, values_mw.to_numpy(dtype=float) / p_nom


def _normalised_signed_profile(values_mw: pd.Series) -> tuple[float, np.ndarray]:
    p_nom = max(float(values_mw.abs().max()), 1e-9)
    return p_nom, values_mw.to_numpy(dtype=float) / p_nom


def build_observed_detail_network(
    daily: pd.DataFrame,
    hydro: pd.DataFrame,
    imports: pd.DataFrame,
    *,
    qa: Mapping[str, object] | None = None,
):
    """Build a 354-day observed-detail PyPSA replay.

    The model uses one Kerala bus. It is intentionally not a transmission-flow
    model because interface transfer limits and internal topology are not yet
    verified. Individual hydro stations and import interfaces are represented as
    fixed-profile generators solely to preserve observed source attribution.
    """

    import pypsa

    days = _prepare_daily(daily)
    _require_columns(hydro, _REQUIRED_HYDRO, "hydro")
    _require_columns(imports, _REQUIRED_IMPORT, "imports")

    hydro_work = hydro.copy()
    import_work = imports.copy()
    for frame in (hydro_work, import_work):
        frame["date"] = pd.to_datetime(frame["date"], errors="raise").dt.normalize()

    hydro_work["generation_mu"] = pd.to_numeric(hydro_work["generation_mu"], errors="coerce")
    import_work["import_mu"] = pd.to_numeric(import_work["import_mu"], errors="coerce")
    if (hydro_work["generation_mu"].dropna() < -1e-9).any():
        raise ValueError("negative station hydro generation is not supported")
    if (import_work["import_mu"].dropna() < -1e-9).any():
        raise ValueError("negative interface import energy requires explicit export modelling")

    snapshots = pd.DatetimeIndex(days["date"])
    day_index = pd.Index(snapshots, name="date")

    hydro_pivot = hydro_work.pivot_table(
        index="date",
        columns="station_name_as_reported",
        values="generation_mu",
        aggfunc="sum",
    ).reindex(day_index)
    import_pivot = import_work.pivot_table(
        index="date",
        columns="interface_name_as_reported",
        values="import_mu",
        aggfunc="sum",
    ).reindex(day_index)

    # Interface coverage is expected to be complete for each observed day in the
    # v1.0.1 evidence archive. Missing values are rejected rather than imputed.
    if import_pivot.isna().any().any():
        missing = int(import_pivot.isna().sum().sum())
        raise ValueError(f"import interface table has {missing} missing observed-day cells")

    reported_hydro_mu = hydro_pivot.sum(axis=1, skipna=True)
    aggregate_hydro_mu = days.set_index("date")["hydro_mu"].reindex(day_index)
    residual_hydro_mu = aggregate_hydro_mu - reported_hydro_mu
    if (residual_hydro_mu < -0.001).any():
        raise ValueError("station hydro rows exceed published aggregate hydro")
    residual_hydro_mu = residual_hydro_mu.clip(lower=0.0)

    interface_total_mu = import_pivot.sum(axis=1)
    aggregate_import_mu = days.set_index("date")["net_import_mu"].reindex(day_index)
    interface_error_mu = interface_total_mu - aggregate_import_mu
    if interface_error_mu.abs().max() > 0.001:
        raise ValueError("interface import rows do not reconcile to published net import")

    nonhydro_mu = (
        days.set_index("date")["internal_generation_mu"].reindex(day_index)
        - aggregate_hydro_mu
    ).clip(lower=0.0)

    network = pypsa.Network()
    network.set_snapshots(snapshots)
    network.snapshot_weightings.loc[:, :] = 24.0
    network.add("Bus", "kerala")

    carriers = [
        "hydro_station",
        "hydro_unallocated",
        "nonhydro_internal",
        "interstate_import",
        "accounting_rounding",
    ]
    for carrier in carriers:
        network.add("Carrier", carrier)

    load_mw = days.set_index("date")["consumption_mu"].reindex(day_index) * 1000.0 / 24.0
    network.add("Load", "observed_system_consumption", bus="kerala", p_set=load_mw.to_numpy())

    station_missing_cells: dict[str, int] = {}
    for station in hydro_pivot.columns:
        observed = hydro_pivot[station]
        station_missing_cells[str(station)] = int(observed.isna().sum())
        # A missing station value is not declared zero in provenance. The zero
        # profile here only prevents assigning unknown energy to that named unit;
        # the day's difference is retained by hydro_unallocated.
        mw = observed.fillna(0.0) * 1000.0 / 24.0
        p_nom, pu = _normalised_profile(mw)
        network.add(
            "Generator",
            f"hydro_station__{_slug(str(station))}",
            bus="kerala",
            carrier="hydro_station",
            p_nom=p_nom,
            p_min_pu=pu,
            p_max_pu=pu,
        )

    residual_mw = residual_hydro_mu * 1000.0 / 24.0
    p_nom, pu = _normalised_profile(residual_mw)
    network.add(
        "Generator",
        "hydro_unallocated",
        bus="kerala",
        carrier="hydro_unallocated",
        p_nom=p_nom,
        p_min_pu=pu,
        p_max_pu=pu,
    )

    nonhydro_mw = nonhydro_mu * 1000.0 / 24.0
    p_nom, pu = _normalised_profile(nonhydro_mw)
    network.add(
        "Generator",
        "observed_nonhydro_internal",
        bus="kerala",
        carrier="nonhydro_internal",
        p_nom=p_nom,
        p_min_pu=pu,
        p_max_pu=pu,
    )

    for interface in import_pivot.columns:
        mw = import_pivot[interface] * 1000.0 / 24.0
        p_nom, pu = _normalised_profile(mw)
        network.add(
            "Generator",
            f"import_interface__{_slug(str(interface))}",
            bus="kerala",
            carrier="interstate_import",
            p_nom=p_nom,
            p_min_pu=pu,
            p_max_pu=pu,
        )

    # SLDC values are published to finite decimal precision. The interface sum can
    # differ from aggregate net import by 0.0001 MU, and the published statewide
    # energy balance can differ by the same order. Preserve every reported value
    # and expose the tiny signed closure term rather than silently altering a row.
    internal_mu = days.set_index("date")["internal_generation_mu"].reindex(day_index)
    consumption_mu = days.set_index("date")["consumption_mu"].reindex(day_index)
    accounting_rounding_mu = consumption_mu - internal_mu - interface_total_mu
    if accounting_rounding_mu.abs().max() > 0.001:
        raise ValueError("accounting closure term exceeds 0.001 MU")
    rounding_mw = accounting_rounding_mu * 1000.0 / 24.0
    p_nom, pu = _normalised_signed_profile(rounding_mw)
    network.add(
        "Generator",
        "accounting_rounding_residual",
        bus="kerala",
        carrier="accounting_rounding",
        p_nom=p_nom,
        p_min_pu=pu,
        p_max_pu=pu,
    )

    qa_meta = dict(qa or {})
    expected_missing = qa_meta.get("missing_dates")
    network.meta = {
        "classification": "derived_from_measured",
        "model_role": "observed_daily_source_attribution_replay",
        "period": "FY2024-25",
        "observed_days": len(days),
        "snapshot_duration_hours": 24,
        "hourly_telemetry_used": False,
        "missing_day_interpolation_used": False,
        "network_topology_role": "single_bus_energy_accounting_not_power_flow",
        "hydro_station_missing_cells": station_missing_cells,
        "hydro_unallocated_reason": (
            "difference between published aggregate hydro and named station rows; "
            "includes unreported/aggregated hydro and preserves missing station cells"
        ),
        "import_p_nom_role": "daily-profile normalisation only; not ATC or transfer capability",
        "accounting_rounding_role": (
            "explicit signed closure of published finite-precision interface/system values; "
            "never a physical source"
        ),
        "accounting_rounding_max_abs_mu": float(accounting_rounding_mu.abs().max()),
        "hydro_p_nom_role": "daily-profile normalisation only; not nameplate capacity",
        "reservoir_constraints_used": False,
        "reservoir_constraint_reason": (
            "reservoir-powerhouse cascade topology and operating rules are not yet verified"
        ),
        "qa_source_archive_sha256": qa_meta.get("source_archive_sha256"),
        "qa_missing_dates": expected_missing,
    }
    return network


def observed_detail_summary(network) -> dict[str, object]:
    """Return energy and provenance checks for the observed-detail replay."""

    gen_weights = network.snapshot_weightings["generators"]
    load_weights = network.snapshot_weightings["objective"]
    load_mwh = float(
        (network.loads_t.p_set["observed_system_consumption"] * load_weights).sum()
    )

    generator_energy: dict[str, float] = {}
    carrier_energy: dict[str, float] = {}
    for name, row in network.generators.iterrows():
        energy = float(
            (network.generators_t.p_max_pu[name] * float(row.p_nom) * gen_weights).sum()
        )
        generator_energy[name] = energy
        carrier = str(row.carrier)
        carrier_energy[carrier] = carrier_energy.get(carrier, 0.0) + energy

    supply_mwh = float(sum(generator_energy.values()))
    return {
        "classification": "derived_from_measured",
        "model_role": "observed_daily_source_attribution_replay",
        "observed_days": len(network.snapshots),
        "load_mwh": load_mwh,
        "supply_mwh": supply_mwh,
        "balance_error_mwh": supply_mwh - load_mwh,
        "carrier_energy_mwh": carrier_energy,
        "generator_energy_mwh": generator_energy,
        "network_meta": dict(network.meta),
    }
