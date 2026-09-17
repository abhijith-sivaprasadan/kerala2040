from __future__ import annotations

import numpy as np
import pandas as pd


def build_smoke_network(hours: int = 24):
    """Build a tiny deterministic PyPSA network used only for CI/smoke tests."""
    import pypsa

    snapshots = pd.date_range("2024-01-01", periods=hours, freq="h")
    network = pypsa.Network()
    network.set_snapshots(snapshots)
    network.add("Bus", "kerala")

    load = 5000 + 500 * np.sin(np.linspace(0, 2 * np.pi, hours, endpoint=False))
    network.add("Load", "load", bus="kerala", p_set=load)

    network.add(
        "Generator",
        "internal_supply",
        bus="kerala",
        p_nom=3500,
        marginal_cost=1200,
    )
    network.add(
        "Generator",
        "imports",
        bus="kerala",
        p_nom=4000,
        marginal_cost=3500,
    )
    return network


def solve_smoke_network(hours: int = 24):
    """Solve the tiny network with HiGHS; this is not the Kerala baseline model."""
    network = build_smoke_network(hours=hours)
    status, condition = network.optimize(solver_name="highs")
    return network, str(status), str(condition)
