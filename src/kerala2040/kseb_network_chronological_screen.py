"""Full-year KSEBL public-network chronological screening v1.0.

This module intentionally implements a linear/DC *screening* calculation, not a
calibrated load flow. Source-backed topology is combined with assumption-tier
line/transformer parameters, an ERA5-sensitive reconstructed load chronology,
daily-average SLDC generation accounting and explicitly proxy-labelled spatial
allocation rules.
"""
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from kerala2040.chronological_screen import prepare_inputs
from kerala2040.weather_load_proxy import load_hourly_proxy

CLASSIFICATION = (
    "KSEBL_NETWORK_CHRONOLOGICAL_SCREENING_V1_0_"
    "DC_PROXY_NOT_CALIBRATED_POWER_FLOW"
)


def _as_bool(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def _as_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_suite(path: Path) -> dict[str, Any]:
    suite = yaml.safe_load(path.read_text(encoding="utf-8"))
    expected = (
        "ksebl_network_chronological_screening_v1_0_"
        "dc_proxy_not_calibrated_power_flow"
    )
    if suite.get("classification") != expected:
        raise ValueError("network chronological screening classification mismatch")
    release = suite["release"]
    for key in (
        "calibrated_dc_power_flow",
        "ac_power_flow",
        "measured_bus_load_telemetry",
        "measured_generator_dispatch",
        "measured_interface_dispatch",
        "n_minus_1_reliability",
        "validated_operational_security",
    ):
        if release.get(key) is not False:
            raise ValueError(f"network screening must keep {key}=false")
    return suite


def connected_components(
    bus_ids: set[str],
    lines: list[dict[str, Any]],
    transformers: list[dict[str, Any]],
) -> tuple[list[list[str]], dict[str, int]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for row in [*lines, *transformers]:
        a = str(row["bus0"])
        b = str(row["bus1"])
        if a not in bus_ids or b not in bus_ids:
            raise ValueError("branch references a missing bus")
        adjacency[a].add(b)
        adjacency[b].add(a)

    seen: set[str] = set()
    components: list[list[str]] = []
    for bus in sorted(bus_ids):
        if bus in seen:
            continue
        queue = deque([bus])
        seen.add(bus)
        group: list[str] = []
        while queue:
            current = queue.popleft()
            group.append(current)
            for other in adjacency.get(current, set()):
                if other not in seen:
                    seen.add(other)
                    queue.append(other)
        components.append(sorted(group))
    components.sort(key=lambda group: (-len(group), group[0]))
    lookup = {
        bus: component_id
        for component_id, group in enumerate(components)
        for bus in group
    }
    return components, lookup


def identify_boundary_interfaces(
    buses: list[dict[str, Any]],
    lines: list[dict[str, Any]],
    *,
    minimum_voltage_kv: int,
) -> list[dict[str, Any]]:
    """Find explicit cross-boundary public-grid endpoints without name guessing."""
    bus_by_id = {str(row["bus_id"]): row for row in buses}
    support: dict[str, dict[str, Any]] = {}
    for line in lines:
        a = str(line["bus0"])
        b = str(line["bus1"])
        for outside, inside in ((a, b), (b, a)):
            external = bus_by_id[outside]
            internal = bus_by_id[inside]
            external_district = str(external.get("district") or "").strip()
            internal_district = str(internal.get("district") or "").strip()
            voltage = int(float(external["voltage_kv"]))
            if (
                external_district
                or not internal_district
                or voltage < minimum_voltage_kv
                or _as_bool(external.get("synthetic_junction"))
            ):
                continue
            rating = _as_float(line.get("screening_s_nom_mva"))
            if rating is None or rating <= 0:
                continue
            item = support.setdefault(
                outside,
                {
                    "bus_id": outside,
                    "node_id": external.get("node_id", ""),
                    "location": external.get("location", ""),
                    "code": external.get("code", ""),
                    "voltage_kv": voltage,
                    "cross_boundary_line_count": 0,
                    "cross_boundary_screening_mva": 0.0,
                    "line_ids": [],
                    "basis": (
                        "NO_KERALA_DISTRICT_PUBLIC_NODE_CONNECTED_BY_"
                        "ADMITTED_LINE_TO_KERALA_DISTRICT_BUS"
                    ),
                },
            )
            item["cross_boundary_line_count"] += 1
            item["cross_boundary_screening_mva"] += rating
            item["line_ids"].append(str(line["line_id"]))

    output = list(support.values())
    for row in output:
        row["cross_boundary_screening_mva"] = round(
            float(row["cross_boundary_screening_mva"]), 6
        )
        row["line_ids"] = ";".join(sorted(set(row["line_ids"])))
    output.sort(
        key=lambda row: (
            -float(row["cross_boundary_screening_mva"]),
            str(row["bus_id"]),
        )
    )
    total = sum(float(row["cross_boundary_screening_mva"]) for row in output)
    if total <= 0:
        raise ValueError(
            "No explicit cross-boundary 220-kV+ interface buses were identified"
        )
    for row in output:
        row["allocation_weight"] = (
            float(row["cross_boundary_screening_mva"]) / total
        )
    return output


def transformer_capacity_for_dc_base(
    row: dict[str, Any],
    incident_line_mva: dict[str, list[float]],
    *,
    floor_mva: float,
) -> tuple[float, str, bool]:
    source = _as_float(row.get("screening_s_nom_mva"))
    if source is not None and source > 0:
        return source, str(row.get("screening_capacity_basis") or ""), True
    candidates = [
        *incident_line_mva.get(str(row["bus0"]), []),
        *incident_line_mva.get(str(row["bus1"]), []),
    ]
    fallback = max(candidates, default=float(floor_mva))
    fallback = max(float(floor_mva), float(fallback))
    return (
        fallback,
        "DC_REACTANCE_BASE_PROXY_MAX_INCIDENT_LINE_MVA_NOT_OPERATOR_RATING",
        False,
    )


def spatialize_generation(
    hourly: pd.DataFrame,
    generators: list[dict[str, Any]],
    *,
    official_hydro_mw: float,
    official_nonhydro_mw: float,
) -> tuple[dict[str, np.ndarray], np.ndarray, dict[str, Any]]:
    """Allocate only mapped capacity shares; keep the unmapped share unlocated."""
    if official_hydro_mw <= 0 or official_nonhydro_mw <= 0:
        raise ValueError("official technology capacities must be positive")

    mapped = [
        row
        for row in generators
        if str(row.get("bus_id") or "").strip()
        and (_as_float(row.get("p_nom_mw")) or 0) > 0
    ]
    hydro = [row for row in mapped if str(row.get("technology") or "").lower() == "hydro"]
    nonhydro = [row for row in mapped if row not in hydro]
    hydro_cap = sum(float(row["p_nom_mw"]) for row in hydro)
    nonhydro_cap = sum(float(row["p_nom_mw"]) for row in nonhydro)

    if hydro_cap > official_hydro_mw + 1e-6:
        raise ValueError("mapped hydro capacity exceeds official hydro fleet")
    if nonhydro_cap > official_nonhydro_mw + 1e-6:
        raise ValueError("mapped nonhydro capacity exceeds official nonhydro fleet")

    hydro_state = hourly["hydro_fixed_mw"].to_numpy(dtype=float)
    nonhydro_state = hourly["nonhydro_fixed_mw"].to_numpy(dtype=float)
    if float(hydro_state.max()) > official_hydro_mw + 1e-6:
        raise ValueError("statewide daily-average hydro exceeds installed hydro")
    if float(nonhydro_state.max()) > official_nonhydro_mw + 1e-6:
        raise ValueError("statewide daily-average nonhydro exceeds installed nonhydro")

    dispatch: dict[str, np.ndarray] = {}
    for row in hydro:
        dispatch[str(row["asset_id"])] = (
            hydro_state * float(row["p_nom_mw"]) / official_hydro_mw
        )
    for row in nonhydro:
        dispatch[str(row["asset_id"])] = (
            nonhydro_state * float(row["p_nom_mw"]) / official_nonhydro_mw
        )

    mapped_hydro = hydro_state * hydro_cap / official_hydro_mw
    mapped_nonhydro = nonhydro_state * nonhydro_cap / official_nonhydro_mw
    unlocated = (
        hydro_state
        - mapped_hydro
        + nonhydro_state
        - mapped_nonhydro
    )
    if (unlocated < -1e-8).any():
        raise RuntimeError("unlocated generation proxy became negative")

    stats = {
        "mapped_hydro_capacity_mw": hydro_cap,
        "official_hydro_capacity_mw": official_hydro_mw,
        "mapped_hydro_capacity_fraction": hydro_cap / official_hydro_mw,
        "mapped_nonhydro_capacity_mw": nonhydro_cap,
        "official_nonhydro_capacity_mw": official_nonhydro_mw,
        "mapped_nonhydro_capacity_fraction": nonhydro_cap / official_nonhydro_mw,
        "mapped_generator_rows": len(mapped),
        "mapped_hydro_rows": len(hydro),
        "mapped_nonhydro_rows": len(nonhydro),
        "unlocated_generation_mwh": float(unlocated.sum()),
        "unlocated_generation_peak_mw": float(unlocated.max()),
        "allocation_rule": (
            "STATEWIDE_DAILY_AVERAGE_TECHNOLOGY_OUTPUT_TIMES_"
            "MAPPED_ASSET_SHARE_OF_OFFICIAL_INSTALLED_TECHNOLOGY_MW"
        ),
    }
    return dispatch, unlocated, stats


def _line_metrics(
    flows: pd.DataFrame,
    rows: list[dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    ratings = pd.Series(
        {
            str(row["line_id"]): float(row["screening_s_nom_mva"])
            for row in rows
        }
    )
    loading = flows.abs().divide(ratings, axis=1)
    metrics = []
    row_by_id = {str(row["line_id"]): row for row in rows}
    for line_id in loading.columns:
        x = loading[line_id]
        source = row_by_id[str(line_id)]
        metrics.append(
            {
                "line_id": line_id,
                "name": source.get("name", ""),
                "feeder_code": source.get("feeder_code", ""),
                "voltage_kv": int(float(source["voltage_kv"])),
                "bus0": source["bus0"],
                "bus1": source["bus1"],
                "screening_s_nom_mva": float(source["screening_s_nom_mva"]),
                "rating_basis": source.get("screening_rating_basis", ""),
                "rating_uses_ksebl_conductor_current_reference": _as_bool(
                    source.get("rating_uses_ksebl_conductor_current_reference")
                ),
                "max_abs_flow_mw": float(flows[line_id].abs().max()),
                "max_loading_pu": float(x.max()),
                "p95_loading_pu": float(x.quantile(0.95)),
                "hours_ge_80pct": int((x >= 0.8).sum()),
                "hours_over_100pct": int((x > 1.0 + 1e-9).sum()),
            }
        )
    return pd.DataFrame(metrics), loading


def _transformer_metrics(
    flows: pd.DataFrame,
    rows: list[dict[str, Any]],
    capacities: dict[str, tuple[float, str, bool]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    ratings = pd.Series(
        {
            key: value[0]
            for key, value in capacities.items()
        }
    )
    loading = flows.abs().divide(ratings, axis=1)
    row_by_id = {str(row["transformer_link_id"]): row for row in rows}
    metrics = []
    for tx_id in loading.columns:
        source = row_by_id[str(tx_id)]
        cap, basis, source_backed = capacities[str(tx_id)]
        x = loading[tx_id]
        metrics.append(
            {
                "transformer_link_id": tx_id,
                "location": source.get("location", ""),
                "bus0": source["bus0"],
                "bus1": source["bus1"],
                "v0_kv": int(float(source["v0_kv"])),
                "v1_kv": int(float(source["v1_kv"])),
                "dc_base_s_nom_mva": cap,
                "capacity_basis": basis,
                "capacity_source_backed": source_backed,
                "max_abs_flow_mw": float(flows[tx_id].abs().max()),
                "max_loading_pu": float(x.max()),
                "p95_loading_pu": float(x.quantile(0.95)),
                "hours_ge_80pct": int((x >= 0.8).sum()),
                "hours_over_100pct": (
                    int((x > 1.0 + 1e-9).sum())
                    if source_backed
                    else None
                ),
            }
        )
    return pd.DataFrame(metrics), loading


def run_screening(
    root: Path,
    *,
    suite_path: Path,
    buses_path: Path,
    lines_path: Path,
    transformers_path: Path,
    generators_path: Path,
    spatial_load_path: Path,
    load_weights_path: Path,
    load_manifest_path: Path,
    daily_path: Path,
    daily_qa_path: Path,
    out_dir: Path,
    hours: int = 8760,
) -> dict[str, Any]:
    if not 24 <= hours <= 8760 or hours % 24:
        raise ValueError("hours must be whole days from 24 through 8760")
    suite = load_suite(suite_path)
    buses = _read_csv(buses_path)
    lines = _read_csv(lines_path)
    transformers = _read_csv(transformers_path)
    generators = _read_csv(generators_path)
    weights = _read_csv(load_weights_path)

    if not buses or not lines or not transformers:
        raise ValueError("network screening inputs are empty")
    bus_ids = {str(row["bus_id"]) for row in buses}
    components, component_lookup = connected_components(
        bus_ids, lines, transformers
    )
    detected_interfaces = identify_boundary_interfaces(
        buses,
        lines,
        minimum_voltage_kv=int(
            suite["boundary_injection"]["minimum_voltage_kv"]
        ),
    )

    proxy = load_hourly_proxy(load_manifest_path)
    daily = pd.read_csv(daily_path)
    daily_qa = json.loads(daily_qa_path.read_text(encoding="utf-8"))
    hourly, chronology_meta = prepare_inputs(
        proxy,
        daily,
        expected_missing_dates=daily_qa["missing_dates"],
    )
    hourly = hourly.iloc[:hours].copy()
    snapshots = pd.DatetimeIndex(hourly["snapshot_ist_naive"])

    gross_load = pd.read_parquet(spatial_load_path).iloc[:hours].copy()
    source_times = (
        pd.to_datetime(gross_load.index, utc=True)
        .tz_convert("Asia/Kolkata")
        .tz_localize(None)
    )
    if not source_times.equals(snapshots):
        raise ValueError("spatial load timestamps disagree with canonical chronology")
    if set(gross_load.columns) != {str(row["bus_id"]) for row in weights}:
        raise ValueError("spatial load columns disagree with load-weight buses")

    load_bus_ids = set(map(str, gross_load.columns))
    load_components = {component_lookup[bus] for bus in load_bus_ids}
    interfaces: list[dict[str, Any]] = []
    for row in detected_interfaces:
        enriched = dict(row)
        cid = component_lookup[str(row["bus_id"])]
        enriched["component_id"] = cid
        enriched["load_serving_component"] = cid in load_components
        enriched["admitted_for_boundary_allocation"] = cid in load_components
        enriched["exclusion_reason"] = (
            ""
            if cid in load_components
            else "TOPOLOGY_COMPONENT_HAS_NO_SPATIAL_LOAD"
        )
        interfaces.append(enriched)

    admitted_interfaces = [
        row for row in interfaces if row["admitted_for_boundary_allocation"]
    ]
    admitted_interface_mva = sum(
        float(row["cross_boundary_screening_mva"])
        for row in admitted_interfaces
    )
    if admitted_interface_mva <= 0:
        raise ValueError(
            "No detected external interface belongs to a load-serving component"
        )
    for row in interfaces:
        row["allocation_weight"] = (
            float(row["cross_boundary_screening_mva"]) / admitted_interface_mva
            if row["admitted_for_boundary_allocation"]
            else 0.0
        )
    if float(
        np.abs(
            gross_load.sum(axis=1).to_numpy()
            - hourly["load_mw"].to_numpy(dtype=float)
        ).max(initial=0)
    ) > 1e-6:
        raise ValueError("spatial load does not reproduce statewide chronology")

    official = suite["official_installed_capacity_mw"]
    generation_dispatch, unlocated_generation, gen_stats = spatialize_generation(
        hourly,
        generators,
        official_hydro_mw=float(official["hydro"]),
        official_nonhydro_mw=float(official["nonhydro"]),
    )
    weight_lookup = {
        str(row["bus_id"]): float(row["load_weight"])
        for row in weights
    }
    if abs(sum(weight_lookup.values()) - 1.0) > 1e-9:
        raise ValueError("load weights do not sum to one")
    net_load = gross_load.copy()
    for bus_id in net_load.columns:
        net_load[bus_id] = (
            net_load[bus_id].to_numpy(dtype=float)
            - unlocated_generation * weight_lookup[bus_id]
        )
    if (net_load.to_numpy() < -1e-6).any():
        raise ValueError("local net-load proxy became negative")

    total_internal = (
        hourly["hydro_fixed_mw"].to_numpy(dtype=float)
        + hourly["nonhydro_fixed_mw"].to_numpy(dtype=float)
    )
    boundary_total = hourly["load_mw"].to_numpy(dtype=float) - total_internal
    if (boundary_total < -1e-6).any():
        raise ValueError("boundary accounting residual became negative")

    generator_by_asset = {
        str(row["asset_id"]): row
        for row in generators
        if str(row.get("asset_id") or "") in generation_dispatch
    }
    injections_by_bus: dict[str, np.ndarray] = defaultdict(
        lambda: np.zeros(hours, dtype=float)
    )
    for asset_id, values in generation_dispatch.items():
        bus_id = str(generator_by_asset[asset_id]["bus_id"])
        injections_by_bus[bus_id] = injections_by_bus[bus_id] + values

    component_tolerance = float(
        suite["component_balance"]["tolerance_mw"]
    )
    load_by_component = {
        cid: np.zeros(hours, dtype=float)
        for cid in range(len(components))
    }
    mapped_injection_by_component = {
        cid: np.zeros(hours, dtype=float)
        for cid in range(len(components))
    }
    for bus_id in net_load.columns:
        cid = component_lookup[str(bus_id)]
        load_by_component[cid] += net_load[bus_id].to_numpy(dtype=float)
    for bus_id, values in injections_by_bus.items():
        cid = component_lookup[bus_id]
        mapped_injection_by_component[cid] += values

    interfaces_by_component: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for interface in admitted_interfaces:
        interfaces_by_component[int(interface["component_id"])].append(interface)
    for cid, rows in interfaces_by_component.items():
        total_mva = sum(
            float(row["cross_boundary_screening_mva"]) for row in rows
        )
        for row in rows:
            row["component_allocation_weight"] = (
                float(row["cross_boundary_screening_mva"]) / total_mva
            )

    component_supply: dict[int, np.ndarray] = {}
    component_sink: dict[int, np.ndarray] = {}
    interface_injection: dict[str, np.ndarray] = {}
    explicit_boundary_total = np.zeros(hours, dtype=float)
    total_component_supply = np.zeros(hours, dtype=float)
    total_component_sink = np.zeros(hours, dtype=float)
    component_rows: list[dict[str, Any]] = []

    for cid, group in enumerate(components):
        pre_boundary_net = (
            load_by_component[cid] - mapped_injection_by_component[cid]
        )
        deficit = np.maximum(pre_boundary_net, 0.0)
        surplus = np.maximum(-pre_boundary_net, 0.0)
        component_interfaces = interfaces_by_component.get(cid, [])

        if component_interfaces:
            for interface in component_interfaces:
                bus_id = str(interface["bus_id"])
                values = (
                    deficit
                    * float(interface["component_allocation_weight"])
                )
                interface_injection[bus_id] = values
                injections_by_bus[bus_id] = (
                    injections_by_bus[bus_id] + values
                )
                explicit_boundary_total += values
            supply = np.zeros(hours, dtype=float)
        else:
            supply = deficit

        # A disconnected component with local generation surplus cannot export
        # through the admitted topology. Preserve the accounting as an explicit
        # diagnostic sink rather than inventing a tie-line.
        sink = surplus

        if float(supply.max()) <= component_tolerance:
            supply[:] = 0.0
        if float(sink.max()) <= component_tolerance:
            sink[:] = 0.0
        component_supply[cid] = supply
        component_sink[cid] = sink
        total_component_supply += supply
        total_component_sink += sink

        component_rows.append(
            {
                "component_id": cid,
                "bus_count": len(group),
                "load_bus_count": sum(bus in net_load.columns for bus in group),
                "generator_bus_count": sum(
                    bus in injections_by_bus for bus in group
                ),
                "boundary_interface_count": len(component_interfaces),
                "detected_boundary_interface_count": sum(
                    str(row["bus_id"]) in group for row in interfaces
                ),
                "net_load_peak_mw": float(load_by_component[cid].max()),
                "mapped_generation_peak_mw": float(
                    mapped_injection_by_component[cid].max()
                ),
                "explicit_boundary_injection_peak_mw": float(
                    sum(
                        (
                            interface_injection[str(row["bus_id"])]
                            for row in component_interfaces
                        ),
                        np.zeros(hours, dtype=float),
                    ).max()
                )
                if component_interfaces
                else 0.0,
                "diagnostic_balance_supply_peak_mw": float(supply.max()),
                "diagnostic_balance_sink_peak_mw": float(sink.max()),
                "diagnostic_balance_absolute_mwh": float(
                    supply.sum() + sink.sum()
                ),
            }
        )

    accounting_residual = (
        explicit_boundary_total
        + total_component_supply
        - total_component_sink
        - boundary_total
    )
    if float(np.abs(accounting_residual).max()) > 1e-6:
        raise RuntimeError(
            "component-aware boundary accounting does not reproduce "
            "the statewide residual"
        )

    balanced_injection_by_component = {
        cid: np.zeros(hours, dtype=float)
        for cid in range(len(components))
    }
    for bus_id, values in injections_by_bus.items():
        balanced_injection_by_component[component_lookup[bus_id]] += values
    for cid in range(len(components)):
        residual = (
            balanced_injection_by_component[cid]
            + component_supply[cid]
            - load_by_component[cid]
            - component_sink[cid]
        )
        if float(np.abs(residual).max()) > component_tolerance:
            raise RuntimeError(
                f"component {cid} remains unbalanced after explicit diagnostics"
            )

    incident_line_mva: dict[str, list[float]] = defaultdict(list)
    for row in lines:
        rating = _as_float(row.get("screening_s_nom_mva"))
        x = _as_float(row.get("screening_x_ohm"))
        if rating is None or rating <= 0 or x is None or x <= 0:
            raise ValueError("all screening lines require positive rating and reactance")
        incident_line_mva[str(row["bus0"])].append(rating)
        incident_line_mva[str(row["bus1"])].append(rating)

    tx_capacities = {
        str(row["transformer_link_id"]): transformer_capacity_for_dc_base(
            row,
            incident_line_mva,
            floor_mva=float(
                suite["transformer_missing_capacity"]["floor_mva"]
            ),
        )
        for row in transformers
    }

    import pypsa

    network = pypsa.Network()
    network.set_snapshots(snapshots)
    network.snapshot_weightings.loc[:, :] = 1.0
    for row in buses:
        lon = _as_float(row.get("lon"))
        lat = _as_float(row.get("lat"))
        network.add(
            "Bus",
            str(row["bus_id"]),
            v_nom=float(row["voltage_kv"]),
            x=lon if lon is not None else 0.0,
            y=lat if lat is not None else 0.0,
        )
    for row in lines:
        network.add(
            "Line",
            str(row["line_id"]),
            bus0=str(row["bus0"]),
            bus1=str(row["bus1"]),
            r=float(row["screening_r_ohm_20c"]),
            x=float(row["screening_x_ohm"]),
            s_nom=float(row["screening_s_nom_mva"]),
        )
    for row in transformers:
        tx_id = str(row["transformer_link_id"])
        cap, _, _ = tx_capacities[tx_id]
        x_pu = _as_float(row.get("screening_x_pu"))
        if x_pu is None or x_pu <= 0:
            raise ValueError(f"transformer {tx_id} lacks positive screening x")
        network.add(
            "Transformer",
            tx_id,
            bus0=str(row["bus0"]),
            bus1=str(row["bus1"]),
            s_nom=cap,
            x=x_pu,
            r=0.0,
        )

    for bus_id in net_load.columns:
        network.add(
            "Load",
            f"NETLOAD:{bus_id}",
            bus=str(bus_id),
            p_set=pd.Series(
                net_load[bus_id].to_numpy(dtype=float),
                index=snapshots,
            ),
        )
    for asset_id, values in generation_dispatch.items():
        row = generator_by_asset[asset_id]
        network.add(
            "Generator",
            f"GEN:{asset_id}",
            bus=str(row["bus_id"]),
            p_nom=float(row["p_nom_mw"]),
            p_set=pd.Series(values, index=snapshots),
        )
    for interface in admitted_interfaces:
        bus_id = str(interface["bus_id"])
        values = interface_injection[bus_id]
        network.add(
            "Generator",
            f"BOUNDARY:{bus_id}",
            bus=bus_id,
            p_nom=float(values.max()),
            p_set=pd.Series(values, index=snapshots),
        )
    for cid, group in enumerate(components):
        if float(component_supply[cid].max()) > component_tolerance:
            network.add(
                "Generator",
                f"COMPONENT_BALANCE_SUPPLY:{cid}",
                bus=group[0],
                p_nom=float(component_supply[cid].max()),
                p_set=pd.Series(component_supply[cid], index=snapshots),
            )
        if float(component_sink[cid].max()) > component_tolerance:
            network.add(
                "Load",
                f"COMPONENT_BALANCE_SINK:{cid}",
                bus=group[0],
                p_set=pd.Series(component_sink[cid], index=snapshots),
            )

    network.lpf()

    line_metrics, line_loading = _line_metrics(
        network.lines_t.p0,
        lines,
    )
    tx_metrics, tx_loading = _transformer_metrics(
        network.transformers_t.p0,
        transformers,
        tx_capacities,
    )

    interface_component_ids = {
        int(row["component_id"]) for row in admitted_interfaces
    }
    line_metrics["component_id"] = line_metrics["bus0"].map(
        component_lookup
    )
    line_metrics["interface_served_component"] = (
        line_metrics["component_id"].isin(interface_component_ids)
    )
    line_metrics["primary_congestion_claim_eligible"] = (
        line_metrics["interface_served_component"]
    )
    primary_lines = line_metrics[
        line_metrics["primary_congestion_claim_eligible"]
    ]
    primary_source_lines = primary_lines[
        primary_lines["rating_uses_ksebl_conductor_current_reference"]
    ]
    primary_fallback_lines = primary_lines[
        ~primary_lines["rating_uses_ksebl_conductor_current_reference"]
    ]

    tx_metrics["component_id"] = tx_metrics["bus0"].map(component_lookup)
    tx_metrics["interface_served_component"] = (
        tx_metrics["component_id"].isin(interface_component_ids)
    )
    tx_metrics["used_for_spatial_load_allocation"] = (
        tx_metrics["bus1"].isin(load_bus_ids)
    )
    tx_metrics["independent_capacity_bottleneck_claim_eligible"] = (
        tx_metrics["capacity_source_backed"]
        & tx_metrics["interface_served_component"]
        & ~tx_metrics["used_for_spatial_load_allocation"]
    )
    source_tx = tx_metrics[tx_metrics["capacity_source_backed"]]
    independent_source_tx = tx_metrics[
        tx_metrics["independent_capacity_bottleneck_claim_eligible"]
    ]

    hourly_metrics = pd.DataFrame(
        {
            "timestamp_ist": snapshots,
            "statewide_gross_load_mw": hourly["load_mw"].to_numpy(dtype=float),
            "unlocated_generation_netted_locally_mw": unlocated_generation,
            "network_net_load_mw": net_load.sum(axis=1).to_numpy(dtype=float),
            "statewide_accounting_residual_mw": boundary_total,
            "explicit_boundary_injection_mw": explicit_boundary_total,
            "component_balance_supply_mw": total_component_supply,
            "component_balance_sink_mw": total_component_sink,
            "max_line_loading_pu": line_loading.max(axis=1).to_numpy(dtype=float),
            "overloaded_line_count": (line_loading > 1.0 + 1e-9).sum(axis=1).to_numpy(dtype=int),
            "max_independent_source_backed_transformer_loading_pu": (
                tx_loading[
                    independent_source_tx["transformer_link_id"]
                ].max(axis=1).to_numpy(dtype=float)
                if not independent_source_tx.empty
                else np.zeros(hours)
            ),
        }
    )

    summary = {
        "classification": CLASSIFICATION,
        "period": (
            f"{snapshots[0].isoformat()} to {snapshots[-1].isoformat()}"
        ),
        "hours": hours,
        "full_financial_year": hours == 8760,
        "network": {
            "buses": len(buses),
            "lines": len(lines),
            "transformers": len(transformers),
            "connected_components": len(components),
            "largest_component_buses": len(components[0]) if components else 0,
            "load_buses": len(net_load.columns),
            "boundary_interfaces_detected": len(interfaces),
            "boundary_interfaces": len(admitted_interfaces),
            "boundary_interfaces_excluded_topology_isolated": (
                len(interfaces) - len(admitted_interfaces)
            ),
            "source_backed_transformer_capacities": int(
                sum(value[2] for value in tx_capacities.values())
            ),
            "transformer_dc_base_capacity_proxies": int(
                sum(not value[2] for value in tx_capacities.values())
            ),
        },
        "chronology": {
            "load_proxy_classification": proxy["classification"],
            "statewide_peak_mw": float(hourly["load_mw"].max()),
            "statewide_accounting_residual_peak_mw": float(boundary_total.max()),
            "statewide_accounting_residual_mwh": float(boundary_total.sum()),
            "explicit_boundary_injection_peak_mw": float(
                explicit_boundary_total.max()
            ),
            "explicit_boundary_injection_mwh": float(
                explicit_boundary_total.sum()
            ),
            "topology_gap_supply_mwh": float(total_component_supply.sum()),
            "topology_gap_sink_mwh": float(total_component_sink.sum()),
            "observed_days": chronology_meta["observed_days"],
            "imputed_days": chronology_meta["imputed_days"],
            "hourly_import_telemetry_measured": False,
        },
        "generation_spatialization": gen_stats,
        "component_balance_diagnostic": {
            "components_requiring_supply_proxy": int(
                sum(row["diagnostic_balance_supply_peak_mw"] > component_tolerance for row in component_rows)
            ),
            "components_requiring_sink_proxy": int(
                sum(row["diagnostic_balance_sink_peak_mw"] > component_tolerance for row in component_rows)
            ),
            "peak_supply_proxy_mw": float(total_component_supply.max()),
            "peak_sink_proxy_mw": float(total_component_sink.max()),
            "absolute_energy_mwh": float(
                total_component_supply.sum() + total_component_sink.sum()
            ),
            "topology_closed_without_component_balance_proxy": bool(
                float(total_component_supply.max()) <= component_tolerance
                and float(total_component_sink.max()) <= component_tolerance
            ),
            "accounting_identity_max_residual_mw": float(
                np.abs(accounting_residual).max()
            ),
        },
        "line_screening": {
            "raw_all_components_lines_over_100pct_any_hour": int(
                (line_metrics["hours_over_100pct"] > 0).sum()
            ),
            "primary_interface_served_lines": int(len(primary_lines)),
            "primary_lines_over_100pct_any_hour": int(
                (primary_lines["hours_over_100pct"] > 0).sum()
            ),
            "primary_lines_ge_80pct_any_hour": int(
                (primary_lines["hours_ge_80pct"] > 0).sum()
            ),
            "primary_source_backed_rating_lines_over_100pct_any_hour": int(
                (primary_source_lines["hours_over_100pct"] > 0).sum()
            ),
            "primary_fallback_rating_lines_over_100pct_any_hour": int(
                (primary_fallback_lines["hours_over_100pct"] > 0).sum()
            ),
            "max_primary_loading_pu": (
                float(primary_lines["max_loading_pu"].max())
                if not primary_lines.empty
                else None
            ),
            "max_primary_source_backed_loading_pu": (
                float(primary_source_lines["max_loading_pu"].max())
                if not primary_source_lines.empty
                else None
            ),
            "max_overloaded_lines_in_one_hour_raw_all_components": int(
                hourly_metrics["overloaded_line_count"].max()
            ),
            "excluded_topology_gap_component_lines": int(
                (~line_metrics["primary_congestion_claim_eligible"]).sum()
            ),
            "line_rating_interpretation": (
                "screening MVA, not operator emergency/seasonal rating; "
                "primary counts exclude components supplied only by topology-gap diagnostics"
            ),
        },
        "transformer_screening": {
            "raw_source_backed_transformers_over_100pct_any_hour": int(
                (source_tx["hours_over_100pct"].fillna(0) > 0).sum()
            ),
            "independent_source_backed_transformers": int(
                len(independent_source_tx)
            ),
            "independent_source_backed_transformers_over_100pct_any_hour": int(
                (
                    independent_source_tx["hours_over_100pct"].fillna(0)
                    > 0
                ).sum()
            ),
            "max_independent_source_backed_loading_pu": (
                float(independent_source_tx["max_loading_pu"].max())
                if not independent_source_tx.empty
                else None
            ),
            "load_allocation_transformers_excluded_from_independent_claims": int(
                (
                    tx_metrics["capacity_source_backed"]
                    & tx_metrics["used_for_spatial_load_allocation"]
                ).sum()
            ),
            "fallback_capacity_transformers_not_used_for_overload_claims": int(
                (~tx_metrics["capacity_source_backed"]).sum()
            ),
            "interpretation": (
                "Transformers whose PSS MVA directly defines the spatial load weight "
                "are non-independent and excluded from bottleneck claims."
            ),
        },
        "release": {
            "full_year_network_screening_executed": hours == 8760,
            "thermal_congestion_screening": True,
            "dc_flow_sensitivity": True,
            "calibrated_dc_power_flow": False,
            "ac_power_flow": False,
            "measured_bus_load_telemetry": False,
            "measured_generator_dispatch": False,
            "measured_interface_dispatch": False,
            "n_minus_1_reliability": False,
            "validated_operational_security": False,
        },
        "interpretation": [
            (
                "This is a linear/DC screening over public topology and explicit "
                "screening parameters; it is not a calibrated KSEBL load flow."
            ),
            (
                "Mapped physical generators receive capacity-share proxies of "
                "statewide daily-average technology output, not measured plant dispatch."
            ),
            (
                "Unmapped internal generation is netted proportionally at load buses "
                "rather than assigned to invented plant locations."
            ),
            (
                "Boundary injection preserves the statewide hourly accounting residual "
                "and observed daily import energy, but is not measured interface dispatch. "
                "Detected external interfaces in components with no spatial load are "
                "reported but excluded from the allocation. Each connected component "
                "is balanced separately; load-serving components without an admitted "
                "external interface receive an explicit topology-gap supply diagnostic."
            ),
            (
                "Line loading compares DC MW flow with screening MVA and is therefore a "
                "congestion indicator, not an operational security-limit assessment. "
                "Primary line counts exclude topology-gap-only components."
            ),
            (
                "Distribution-interface transformer MVA used to weight spatial load is "
                "not independent validation of transformer loading and is excluded from "
                "primary transformer bottleneck claims."
            ),
        ],
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(interfaces).to_csv(
        out_dir / "boundary_interfaces.csv", index=False
    )
    pd.DataFrame(component_rows).to_csv(
        out_dir / "component_balance_diagnostic.csv", index=False
    )
    line_metrics.sort_values(
        ["max_loading_pu", "line_id"], ascending=[False, True]
    ).to_csv(out_dir / "line_loading_summary.csv", index=False)
    tx_metrics.sort_values(
        ["max_loading_pu", "transformer_link_id"], ascending=[False, True]
    ).to_csv(out_dir / "transformer_loading_summary.csv", index=False)
    hourly_metrics.to_parquet(
        out_dir / "hourly_network_metrics.parquet",
        compression="zstd",
        index=False,
    )
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary
