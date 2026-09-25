"""Build a non-optimising PyPSA skeleton from the reconciled March-2026 base.

This deliberately creates no load chronology and disables dispatch on every resource
whose temporal/operational evidence is unresolved. It is a structural smoke test only.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_selection(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != "research_input_selection_partial_not_run_ready":
        raise ValueError("research input selection classification mismatch")
    if data.get("base_date") != "2026-03-31":
        raise ValueError("full PyPSA skeleton must use the canonical March-2026 base")
    if data.get("release", {}).get("network_skeleton_smoke_ready") is not True:
        raise ValueError("input selection does not permit a network-skeleton smoke test")
    if data.get("release", {}).get("chronological_dispatch_ready") is not False:
        raise ValueError("skeleton input selection incorrectly claims dispatch readiness")
    return data


def build_full_pypsa_skeleton(selection: dict[str, Any]):
    import pandas as pd
    import pypsa

    if selection["release"]["capacity_expansion_ready"] is not False:
        raise ValueError("capacity expansion must remain disabled in the skeleton")

    network = pypsa.Network()
    network.set_snapshots(pd.DatetimeIndex(["2026-03-31 00:00:00"]))

    network.add("Carrier", "hydro_existing")
    network.add("Carrier", "thermal_existing")
    network.add("Carrier", "solar_existing")
    network.add("Carrier", "renewable_unresolved")
    network.add("Carrier", "external_grid")

    network.add("Bus", "kerala_system")
    network.add("Bus", "external_grid")

    gen = selection["selected"]["existing_generation"]

    # These components carry reconciled nameplate/accounting capacity only.
    # p_max_pu=0 prevents accidental dispatch before chronology/operations are admitted.
    components = [
        ("ksebl_hydro", "hydro_existing", gen["ksebl_hydro"]["capacity_mw"]),
        ("non_state_hydro", "hydro_existing", gen["non_state_hydro"]["capacity_mw"]),
        (
            "brahmapuram",
            "thermal_existing",
            gen["ksebl_thermal"]["brahmapuram_mw"],
        ),
        (
            "kozhikode",
            "thermal_existing",
            gen["ksebl_thermal"]["kozhikode_mw"],
        ),
        (
            "ntpc_kayamkulam",
            "thermal_existing",
            gen["ntpc_kayamkulam"]["capacity_mw"],
        ),
        (
            "private_thermal_residual",
            "thermal_existing",
            gen["private_thermal"]["capacity_mw"],
        ),
        (
            "kayamkulam_floating_solar",
            "solar_existing",
            gen["central_floating_solar"]["capacity_mw"],
        ),
        (
            "renewable_ge_1mw_residual",
            "renewable_unresolved",
            gen["renewable_ge_1mw_residual"]["capacity_mw"],
        ),
    ]
    for name, carrier, p_nom in components:
        network.add(
            "Generator",
            name,
            bus="kerala_system",
            carrier=carrier,
            p_nom=float(p_nom),
            p_nom_extendable=False,
            p_min_pu=0.0,
            p_max_pu=0.0,
        )

    # The ATC snapshot is represented only as disabled structural metadata.
    # It is not admitted as an annual/future flow limit.
    network.add(
        "Link",
        "interstate_import_boundary_snapshot",
        bus0="external_grid",
        bus1="kerala_system",
        carrier="external_grid",
        p_nom=float(selection["selected"]["network"]["current_import_ATC_crosscheck_mw"]),
        p_nom_extendable=False,
        p_min_pu=0.0,
        p_max_pu=0.0,
        efficiency=1.0,
    )

    network.meta = {
        "classification": "structural_network_skeleton_not_dispatch_not_optimised",
        "base_date": selection["base_date"],
        "load_added": False,
        "distributed_solar_explicit_generator": False,
        "distributed_solar_treatment": gen["distributed_solar_lt_1mw"]["mode"],
        "operational_bess_admitted": False,
        "operational_psp_admitted": False,
        "import_ATC_role": "dated_crosscheck_only_not_annual_or_future_limit",
        "all_resource_dispatch_disabled": True,
        "capacity_expansion_enabled": False,
    }
    return network


def skeleton_summary(network) -> dict[str, Any]:
    return {
        "classification": network.meta["classification"],
        "base_date": network.meta["base_date"],
        "buses": len(network.buses),
        "generators": len(network.generators),
        "links": len(network.links),
        "generator_capacity_mw": float(network.generators["p_nom"].sum()),
        "import_boundary_snapshot_mw": float(
            network.links.at["interstate_import_boundary_snapshot", "p_nom"]
        ),
        "all_generator_dispatch_disabled": bool(
            (network.generators["p_max_pu"] == 0.0).all()
        ),
        "all_link_dispatch_disabled": bool((network.links["p_max_pu"] == 0.0).all()),
        "load_count": len(network.loads),
        "storage_units": len(network.storage_units),
        "stores": len(network.stores),
        "meta": dict(network.meta),
    }
