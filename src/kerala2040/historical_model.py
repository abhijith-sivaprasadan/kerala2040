"""Observed FY2024-25 Kerala daily replay model.

This is deliberately not an hourly dispatch model. It replays measured daily
system energy as average MW over 24-hour weighted snapshots.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

_REQUIRED = {
    "date",
    "consumption_mu",
    "internal_generation_mu",
    "net_import_interface_mu",
    "hydel_total_mu",
}


def build_daily_observed_replay(
    daily: pd.DataFrame,
    observed: dict[str, object],
):
    """Build a fixed-profile PyPSA network from observed SLDC daily energy."""
    import pypsa

    missing = sorted(_REQUIRED - set(daily.columns))
    if missing:
        raise ValueError(f"daily data missing required columns: {missing}")

    work = daily.copy()
    work["date"] = pd.to_datetime(work["date"]).dt.normalize()
    work = work.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    if work.empty:
        raise ValueError("daily data are empty")

    numeric_columns = [
        "consumption_mu",
        "internal_generation_mu",
        "net_import_interface_mu",
        "hydel_total_mu",
    ]
    numeric = work[numeric_columns].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(numeric).all().all():
        raise ValueError("daily replay requires finite observed energy values")
    if (numeric["consumption_mu"] <= 0).any():
        raise ValueError("daily consumption must be positive")
    if (numeric["net_import_interface_mu"] < 0).any():
        raise ValueError("negative net-import days require explicit export representation")

    non_hydro_mu = numeric["internal_generation_mu"] - numeric["hydel_total_mu"]
    if (non_hydro_mu < -1e-6).any():
        raise ValueError("hydro generation exceeds internal generation on at least one day")
    non_hydro_mu = non_hydro_mu.clip(lower=0.0)

    capacity = observed["electricity"]["capacity_mix_mw"]
    hydro_capacity_mw = float(capacity["hydel"])
    installed_total_mw = float(observed["electricity"]["installed_capacity_mw"])
    non_hydro_capacity_mw = installed_total_mw - hydro_capacity_mw
    if hydro_capacity_mw <= 0 or non_hydro_capacity_mw <= 0:
        raise ValueError("observed installed capacities must be positive")

    load_mw = numeric["consumption_mu"].to_numpy() * 1000.0 / 24.0
    hydro_mw = numeric["hydel_total_mu"].to_numpy() * 1000.0 / 24.0
    non_hydro_mw = non_hydro_mu.to_numpy() * 1000.0 / 24.0
    import_mw = numeric["net_import_interface_mu"].to_numpy() * 1000.0 / 24.0

    if (hydro_mw > hydro_capacity_mw + 1e-6).any():
        raise ValueError("observed daily-average hydro exceeds installed hydro capacity")
    if (non_hydro_mw > non_hydro_capacity_mw + 1e-6).any():
        raise ValueError("observed daily-average non-hydro exceeds installed non-hydro capacity")

    import_normalisation_mw = max(float(import_mw.max()), 1.0)

    network = pypsa.Network()
    network.set_snapshots(pd.DatetimeIndex(work["date"]))
    network.snapshot_weightings.loc[:, :] = 24.0
    network.add("Bus", "kerala")
    network.add("Carrier", "hydro")
    network.add("Carrier", "non_hydro_internal")
    network.add("Carrier", "interstate_net_import")

    network.add("Load", "observed_system_consumption", bus="kerala", p_set=load_mw)

    hydro_pu = hydro_mw / hydro_capacity_mw
    network.add(
        "Generator",
        "observed_hydro",
        bus="kerala",
        carrier="hydro",
        p_nom=hydro_capacity_mw,
        p_min_pu=hydro_pu,
        p_max_pu=hydro_pu,
    )
    non_hydro_pu = non_hydro_mw / non_hydro_capacity_mw
    network.add(
        "Generator",
        "observed_non_hydro_internal",
        bus="kerala",
        carrier="non_hydro_internal",
        p_nom=non_hydro_capacity_mw,
        p_min_pu=non_hydro_pu,
        p_max_pu=non_hydro_pu,
    )
    import_pu = import_mw / import_normalisation_mw
    network.add(
        "Generator",
        "observed_net_import",
        bus="kerala",
        carrier="interstate_net_import",
        p_nom=import_normalisation_mw,
        p_min_pu=import_pu,
        p_max_pu=import_pu,
    )

    network.meta = {
        "classification": "derived_from_measured",
        "source_type": "observed_daily_replay",
        "source": "Kerala SLDC system statistics + Kerala State Planning Board/KSEBL Economic Review 2025",
        "source_urls": [
            "https://sldckerala.com/index.php?id=1",
            "https://spb.kerala.gov.in/economic-review/ER2025/index.php",
        ],
        "period": observed.get("period", "FY2024-25"),
        "observed_days": len(work),
        "snapshot_duration_hours": 24,
        "import_p_nom_role": "normalisation_only_not_transfer_capability",
        "hourly_telemetry_used": False,
        "synthetic_hourly_load_used": False,
        "installed_capacity_source": "Kerala Economic Review 2025 / KSEBL",
        "daily_energy_source": "Kerala SLDC system statistics",
    }
    return network


def replay_energy_summary(network) -> dict[str, object]:
    """Report energy represented by fixed profiles before/after optimisation."""
    weights = network.snapshot_weightings["generators"]
    load_weights = network.snapshot_weightings["objective"]
    load_mwh = float(
        (network.loads_t.p_set["observed_system_consumption"] * load_weights).sum()
    )

    generators: dict[str, float] = {}
    for name in network.generators.index:
        p_nom = float(network.generators.at[name, "p_nom"])
        profile = network.generators_t.p_max_pu[name]
        generators[name] = float((profile * p_nom * weights).sum())

    return {
        "classification": "derived_from_measured",
        "source_type": "model_energy_check",
        "source": "Kerala SLDC system statistics + Kerala State Planning Board/KSEBL Economic Review 2025",
        "source_urls": [
            "https://sldckerala.com/index.php?id=1",
            "https://spb.kerala.gov.in/economic-review/ER2025/index.php",
        ],
        "load_mwh": load_mwh,
        "generator_energy_mwh": generators,
        "supply_mwh": float(sum(generators.values())),
        "balance_error_mwh": float(sum(generators.values()) - load_mwh),
    }
