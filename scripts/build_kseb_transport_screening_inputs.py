"""Build provenance-labelled Kerala transport/DC screening inputs.

This layer is distinct from a calibrated power-flow model. It combines the
2026 public graph with historical KSEBL PSS equipment evidence, KSEBL SLD
conductor-current references, published conductor resistance references, and
the existing statewide hourly load reconstruction. Assumptions remain explicit.
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import math
import re
import zlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUSES = (
    ROOT / "results/network/public_multibus_skeleton_v0_1/model_buses.csv"
)
DEFAULT_LINES = (
    ROOT / "results/network/public_multibus_skeleton_v0_1/model_lines.csv"
)
DEFAULT_TX = (
    ROOT
    / "results/network/public_multibus_skeleton_v0_1/"
    "model_transformer_links.csv"
)
DEFAULT_PSS_EDGE = (
    ROOT / "results/network/public_pss_evidence_v0_1/"
    "pss_source_edge_crosswalk.csv"
)
DEFAULT_PSS_TX = (
    ROOT / "results/network/public_pss_evidence_v0_1/"
    "pss_station_transformer_capacity_links.csv"
)
DEFAULT_SLD = (
    ROOT / "results/network/public_sld_mining_v0_1/"
    "sld_equipment_mining.json"
)
DEFAULT_LOAD_MANIFEST = (
    ROOT
    / "data/evidence/demand/"
    "hourly_load_proxy_era5_weather_sensitive_v2/manifest.json"
)
DEFAULT_OUT = ROOT / "results/network/public_transport_screening_v0_1"

CLASSIFICATION = (
    "KSEBL_PUBLIC_TRANSPORT_SCREENING_INPUTS_V0_1_"
    "NOT_CALIBRATED_POWER_FLOW"
)

CONDUCTOR_R20_OHM_PER_KM = {
    "WOLF": 0.1871,
    "PANTHER": 0.1390,
    "KUNDAH": 0.07311,
    "MOOSE": 0.05595,
    "LYNX": 0.1576,
    "TIGER": 0.2202,
}
RESISTANCE_REFERENCE = {
    "WOLF": "KSEBL SCM technical specification / IS 398 reference",
    "MOOSE": "KSEBL SCM technical specification / IS 398 reference",
    "PANTHER": "published ACSR 20 C D.C. resistance reference",
    "KUNDAH": "published ACSR 20 C D.C. resistance reference",
    "LYNX": "published BS 215 ACSR 20 C D.C. resistance reference",
    "TIGER": "published BS 215 ACSR 20 C D.C. resistance reference",
}

# Conductor code alone cannot determine positive-sequence line reactance.
# These are replaceable screening assumptions, not KSEBL measurements.
X_SCREEN_OHM_PER_KM = {110: 0.40, 220: 0.35, 320: 0.32, 400: 0.30}
X_UG_SCREEN_OHM_PER_KM = 0.10
VOLTAGE_FALLBACK_CURRENT_A = {
    110: 296.0,
    220: 726.0,
    320: 726.0,
    400: 1760.0,
}

AMPACITY_PATTERNS = {
    name: re.compile(
        rf"\b(?:ACSR\s+)?{name}(?:\s+CONDUCTOR)?\s*[-,:]?\s*"
        rf"(\d{{2,4}})\s*A\b",
        re.IGNORECASE,
    )
    for name in (
        "WOLF",
        "KUNDAH",
        "PANTHER",
        "LYNX",
        "TIGER",
        "MOOSE",
    )
}


def _as_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _as_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(
    path: Path, rows: list[dict[str, Any]], fields: list[str]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


def _sld_ampacity_reference(
    payload: dict[str, Any],
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    hits: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for station in payload.get("records", []):
        code = str(station.get("code") or "")
        mining = station.get("mining") or {}
        texts = [
            mining.get("text_preview") or "",
            *(mining.get("equipment_contexts") or []),
        ]
        for text in dict.fromkeys(map(str, texts)):
            for conductor, pattern in AMPACITY_PATTERNS.items():
                for match in pattern.finditer(text):
                    value = int(match.group(1))
                    if 100 <= value <= 3000:
                        hits[conductor].append((value, code))
    consensus: dict[str, float] = {}
    evidence_rows: list[dict[str, Any]] = []
    for conductor, values in sorted(hits.items()):
        counts = Counter(value for value, _ in values)
        if not counts:
            continue
        value, count = counts.most_common(1)[0]
        total = sum(counts.values())
        dominance = count / total
        stations = len(
            {
                code
                for hit, code in values
                if hit == value and code
            }
        )
        admitted = count >= 2 and dominance >= 0.80
        if admitted:
            consensus[conductor] = float(value)
        evidence_rows.append(
            {
                "conductor": conductor,
                "consensus_ampacity_a": value,
                "consensus_hit_count": count,
                "all_candidate_hits": total,
                "supporting_station_count": stations,
                "dominance_fraction": round(dominance, 6),
                "admitted_as_screening_reference": admitted,
                "basis": (
                    "REPEATED_KSEBL_PUBLIC_SLD_CONDUCTOR_CURRENT_TEXT"
                ),
            }
        )
    return consensus, evidence_rows


def _conductor_components(
    label: str,
) -> tuple[list[tuple[str, int]], bool]:
    value = str(label or "").upper().strip()
    if not value:
        return [], False
    if value == "QUAD_MOOSE":
        return [("MOOSE", 4)], False
    if value == "TWIN_MOOSE":
        return [("MOOSE", 2)], False
    if value == "TWIN_PANTHER":
        return [("PANTHER", 2)], False
    if value == "ACSR_KUNDAH_TWIN_PANTHER":
        return [("KUNDAH", 1), ("PANTHER", 2)], True
    if value == "ACSR_WOLF_PANTHER":
        return [("WOLF", 1), ("PANTHER", 1)], True
    if value == "ACSR_WOLF_TIGER":
        return [("WOLF", 1), ("TIGER", 1)], True
    for conductor in (
        "WOLF",
        "KUNDAH",
        "PANTHER",
        "LYNX",
        "TIGER",
        "MOOSE",
    ):
        if conductor in value:
            return [(conductor, 1)], False
    return [], False


def _screen_current(
    conductor_label: str,
    voltage_kv: int,
    ampacity: dict[str, float],
) -> tuple[float, str, bool]:
    components, series_mixed = _conductor_components(conductor_label)
    if components and all(name in ampacity for name, _ in components):
        capacities = [
            ampacity[name] * bundle
            for name, bundle in components
        ]
        current = min(capacities) if series_mixed else capacities[0]
        return (
            current,
            "PSS_CONDUCTOR_PLUS_KSEBL_SLD_CURRENT_REFERENCE",
            True,
        )
    current = VOLTAGE_FALLBACK_CURRENT_A.get(voltage_kv)
    if current is None:
        raise ValueError(
            f"No current-screening fallback for {voltage_kv} kV"
        )
    return (
        current,
        "CONSERVATIVE_VOLTAGE_CLASS_CURRENT_ASSUMPTION",
        False,
    )


def _screen_resistance(
    conductor_label: str,
    voltage_kv: int,
    length_km: float,
) -> tuple[float, str, bool]:
    components, series_mixed = _conductor_components(conductor_label)
    if components and not series_mixed and len(components) == 1:
        name, bundle = components[0]
        if name in CONDUCTOR_R20_OHM_PER_KM:
            per_km = CONDUCTOR_R20_OHM_PER_KM[name] / bundle
            return (
                per_km * length_km,
                (
                    f"{RESISTANCE_REFERENCE[name]}; "
                    f"bundle_parallel_divisor={bundle}"
                ),
                True,
            )
    fallback_name = {
        110: "WOLF",
        220: "KUNDAH",
        320: "KUNDAH",
        400: "MOOSE",
    }[voltage_kv]
    bundle = 2 if voltage_kv == 400 else 1
    per_km = CONDUCTOR_R20_OHM_PER_KM[fallback_name] / bundle
    return (
        per_km * length_km,
        (
            f"CONSERVATIVE_{voltage_kv}KV_"
            f"{fallback_name}_R20_ASSUMPTION"
        ),
        False,
    )


def _decode_load_proxy(manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )
    payload = "".join(
        (manifest_path.parent / part["file"])
        .read_text(encoding="utf-8")
        .strip()
        for part in manifest["parts"]
    )
    data = zlib.decompress(base64.b64decode(payload))
    result = json.loads(data)
    if (
        result.get("classification")
        != "proxy_reconstruction_not_measured_telemetry"
    ):
        raise ValueError(
            "Refusing to relabel hourly load input as measured telemetry"
        )
    return result


def _build_screening_buses(
    buses: list[dict[str, Any]],
    pss_tx: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[tuple[str, int], str]]:
    output = [dict(row) for row in buses]
    lookup: dict[tuple[str, int], str] = {}
    node_meta: dict[str, dict[str, Any]] = {}
    for row in output:
        voltage = int(float(row["voltage_kv"]))
        lookup[(row["node_id"], voltage)] = row["bus_id"]
        node_meta.setdefault(row["node_id"], row)
    for row in pss_tx:
        node_id = str(row["node_id"])
        for voltage in (
            int(float(row["high_kv"])),
            int(float(row["low_kv"])),
        ):
            key = (node_id, voltage)
            if key in lookup:
                continue
            meta = node_meta.get(node_id)
            if meta is None:
                continue
            bus_id = f"{node_id}@{voltage}"
            lookup[key] = bus_id
            output.append(
                {
                    **meta,
                    "bus_id": bus_id,
                    "voltage_kv": voltage,
                    "topology_voltage_evidence": False,
                    "station_class_voltage_evidence": False,
                    "sld_transformer_voltage_evidence": False,
                    "pss_2023_transformer_voltage_evidence": True,
                    "screening_added_bus": True,
                }
            )
    for row in output:
        row.setdefault(
            "pss_2023_transformer_voltage_evidence", False
        )
        row.setdefault("screening_added_bus", False)
    return output, lookup


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--buses", type=Path, default=DEFAULT_BUSES)
    parser.add_argument("--lines", type=Path, default=DEFAULT_LINES)
    parser.add_argument(
        "--transformers", type=Path, default=DEFAULT_TX
    )
    parser.add_argument(
        "--pss-edge", type=Path, default=DEFAULT_PSS_EDGE
    )
    parser.add_argument(
        "--pss-transformers", type=Path, default=DEFAULT_PSS_TX
    )
    parser.add_argument(
        "--sld-mining", type=Path, default=DEFAULT_SLD
    )
    parser.add_argument(
        "--load-manifest", type=Path, default=DEFAULT_LOAD_MANIFEST
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    buses = _read_csv(args.buses)
    lines = _read_csv(args.lines)
    existing_tx = _read_csv(args.transformers)
    pss_edges = _read_csv(args.pss_edge)
    pss_tx = _read_csv(args.pss_transformers)
    sld = json.loads(
        args.sld_mining.read_text(encoding="utf-8")
    )
    ampacity, ampacity_rows = _sld_ampacity_reference(sld)

    edge_by_id = {
        row["source_edge_id"]: row for row in pss_edges
    }
    screening_lines: list[dict[str, Any]] = []
    for line in lines:
        voltage = int(float(line["voltage_kv"]))
        length = _as_float(line.get("geometry_length_km"))
        if length is None or length <= 0:
            length = _as_float(
                line.get("source_length_km_allocated")
            )
        if length is None or length <= 0:
            raise ValueError(
                f"Line {line['line_id']} has no positive length"
            )
        pss = edge_by_id.get(line["source_edge_id"], {})
        conductor = str(pss.get("pss_conductor") or "")
        current, current_basis, current_from_source = (
            _screen_current(conductor, voltage, ampacity)
        )
        s_nom = (
            math.sqrt(3.0) * voltage * current / 1000.0
        )
        r_ohm, r_basis, r_from_conductor = _screen_resistance(
            conductor, voltage, length
        )
        is_ug = "UG" in conductor or "CABLE" in conductor
        x_per_km = (
            X_UG_SCREEN_OHM_PER_KM
            if is_ug
            else X_SCREEN_OHM_PER_KM[voltage]
        )
        screening_lines.append(
            {
                **line,
                "pss_2023_conductor": conductor,
                "pss_2023_row_matched": _as_bool(
                    pss.get("pss_row_matched")
                ),
                "screening_current_a": round(current, 6),
                "screening_s_nom_mva": round(s_nom, 6),
                "screening_rating_basis": current_basis,
                "rating_uses_ksebl_conductor_current_reference": (
                    current_from_source
                ),
                "screening_r_ohm_20c": round(r_ohm, 8),
                "screening_r_basis": r_basis,
                "r_uses_conductor_specific_reference": (
                    r_from_conductor
                ),
                "screening_x_ohm": round(
                    x_per_km * length, 8
                ),
                "screening_x_basis": (
                    "ASSUMED_GENERIC_UG_X_PER_KM"
                    if is_ug
                    else (
                        f"ASSUMED_GENERIC_{voltage}KV_"
                        "OVERHEAD_X_PER_KM"
                    )
                ),
                "screening_only_not_operator_rating": True,
            }
        )

    screening_buses, bus_lookup = _build_screening_buses(
        buses, pss_tx
    )
    tx_by_key: dict[tuple[str, int, int], dict[str, Any]] = {}
    for row in existing_tx:
        key = (
            row["node_id"],
            int(float(row["v0_kv"])),
            int(float(row["v1_kv"])),
        )
        tx_by_key[key] = {
            **row,
            "screening_s_nom_mva": "",
            "screening_capacity_basis": (
                "NO_PSS_2023_CAPACITY_MATCH"
            ),
            "screening_x_pu": 0.10,
            "screening_x_basis": (
                "GENERIC_TRANSFORMER_X_PU_ASSUMPTION"
            ),
            "pss_2023_supplemented_link": False,
        }
    for source in pss_tx:
        node_id = source["node_id"]
        high = int(float(source["high_kv"]))
        low = int(float(source["low_kv"]))
        cap = _as_float(source.get("aggregate_total_mva"))
        if cap is None or cap <= 0:
            continue
        key = (node_id, high, low)
        row = tx_by_key.get(key)
        bus0 = bus_lookup.get((node_id, high))
        bus1 = bus_lookup.get((node_id, low))
        if bus0 is None or bus1 is None:
            continue
        if row is None:
            row = {
                "transformer_link_id": (
                    f"PSS23:{node_id}:{high}-{low}"
                ),
                "node_id": node_id,
                "location": source.get("location", ""),
                "code": source.get("code", ""),
                "bus0": bus0,
                "bus1": bus1,
                "v0_kv": high,
                "v1_kv": low,
                "evidence_record_count": 0,
                "labelled_evidence_record_count": 0,
                "evidence_ids": "",
                "rating_expressions": "",
                "rating_values_mva": "",
                "s_nom_mva_admitted": "",
                "impedance_admitted": False,
                "connectivity_only": False,
                "screening_x_pu": 0.10,
                "screening_x_basis": (
                    "GENERIC_TRANSFORMER_X_PU_ASSUMPTION"
                ),
                "pss_2023_supplemented_link": True,
            }
            tx_by_key[key] = row
        row["screening_s_nom_mva"] = round(cap, 6)
        row["screening_capacity_basis"] = (
            "KSEBL_PSS_2022_23_PRINTED_TOTAL_TRANSFORMER_MVA"
        )
        row["pss_2023_supplemented_link"] = True
        row["connectivity_only"] = False
    screening_tx = list(tx_by_key.values())

    load_capacity: dict[str, float] = defaultdict(float)
    load_meta: dict[str, dict[str, Any]] = {}
    for row in screening_tx:
        cap = _as_float(row.get("screening_s_nom_mva"))
        if cap is None or cap <= 0:
            continue
        low = int(float(row["v1_kv"]))
        if low > 33:
            continue
        bus_id = row["bus1"]
        load_capacity[bus_id] += cap
        load_meta[bus_id] = row
    total_capacity = sum(load_capacity.values())
    if total_capacity <= 0:
        raise RuntimeError(
            "No PSS-backed distribution-interface capacity "
            "available for load allocation"
        )
    load_weights: list[dict[str, Any]] = []
    for bus_id, capacity in sorted(load_capacity.items()):
        row = load_meta[bus_id]
        load_weights.append(
            {
                "bus_id": bus_id,
                "node_id": row["node_id"],
                "location": row.get("location", ""),
                "code": row.get("code", ""),
                "voltage_kv": int(float(row["v1_kv"])),
                "pss_2023_distribution_interface_mva": round(
                    capacity, 6
                ),
                "load_weight": capacity / total_capacity,
                "classification": (
                    "CAPACITY_WEIGHTED_SPATIAL_LOAD_PROXY_"
                    "NOT_METERED_BUS_LOAD"
                ),
            }
        )

    load_proxy = _decode_load_proxy(args.load_manifest)
    records = load_proxy.get("records") or []
    if len(records) != 8760:
        raise ValueError(
            "Expected 8760-hour statewide load proxy"
        )
    timestamps = [row["timestamp"] for row in records]
    statewide = pd.Series(
        [float(row["load_mw"]) for row in records],
        index=timestamps,
        name="statewide_load_mw",
    )
    wide = pd.DataFrame(index=timestamps)
    for row in load_weights:
        wide[row["bus_id"]] = (
            statewide.to_numpy() * float(row["load_weight"])
        )
    reconstructed = wide.sum(axis=1)
    max_residual = float(
        (reconstructed - statewide).abs().max()
    )
    if max_residual > 1e-8:
        raise RuntimeError(
            "Spatial load allocation does not conserve "
            f"statewide load: {max_residual} MW"
        )
    wide.index.name = "timestamp"

    bus_ids = {row["bus_id"] for row in screening_buses}
    line_ids = {row["line_id"] for row in screening_lines}
    tx_ids = {
        row["transformer_link_id"] for row in screening_tx
    }
    all_line_refs = all(
        row["bus0"] in bus_ids and row["bus1"] in bus_ids
        for row in screening_lines
    )
    all_tx_refs = all(
        row["bus0"] in bus_ids and row["bus1"] in bus_ids
        for row in screening_tx
    )
    source_rating_lines = sum(
        bool(row["rating_uses_ksebl_conductor_current_reference"])
        for row in screening_lines
    )
    conductor_r_lines = sum(
        bool(row["r_uses_conductor_specific_reference"])
        for row in screening_lines
    )
    pss_capacity_links = sum(
        _as_float(row.get("screening_s_nom_mva")) is not None
        for row in screening_tx
    )
    qa = {
        "classification": CLASSIFICATION + "_QA",
        "screening_buses": len(screening_buses),
        "screening_added_pss_voltage_buses": sum(
            _as_bool(row.get("screening_added_bus"))
            for row in screening_buses
        ),
        "screening_lines": len(screening_lines),
        "lines_with_pss_conductor_identity": sum(
            bool(row["pss_2023_conductor"])
            for row in screening_lines
        ),
        "lines_with_ksebl_sld_conductor_current_reference": (
            source_rating_lines
        ),
        "lines_using_conservative_voltage_current_fallback": (
            len(screening_lines) - source_rating_lines
        ),
        "lines_with_conductor_specific_r20_reference": (
            conductor_r_lines
        ),
        "lines_using_resistance_fallback": (
            len(screening_lines) - conductor_r_lines
        ),
        "lines_with_screening_x": sum(
            _as_float(row.get("screening_x_ohm"))
            not in {None, 0}
            for row in screening_lines
        ),
        "screening_transformer_links": len(screening_tx),
        "transformer_links_with_pss_2023_capacity": (
            pss_capacity_links
        ),
        "pss_2023_supplemented_transformer_links": sum(
            _as_bool(row.get("pss_2023_supplemented_link"))
            for row in screening_tx
        ),
        "load_buses": len(load_weights),
        "load_weight_sum": sum(
            float(row["load_weight"])
            for row in load_weights
        ),
        "load_proxy_hours": len(records),
        "statewide_load_peak_mw": float(statewide.max()),
        "spatial_load_peak_sum_mw": float(
            wide.sum(axis=1).max()
        ),
        "max_hourly_load_conservation_residual_mw": (
            max_residual
        ),
        "bus_ids_unique": len(bus_ids) == len(screening_buses),
        "line_ids_unique": (
            len(line_ids) == len(screening_lines)
        ),
        "transformer_ids_unique": (
            len(tx_ids) == len(screening_tx)
        ),
        "all_line_bus_references_valid": all_line_refs,
        "all_transformer_bus_references_valid": all_tx_refs,
        "thermal_transport_screening_ready": True,
        "dc_screening_inputs_complete": True,
        "calibrated_dc_power_flow_ready": False,
        "ac_power_flow_ready": False,
        "measured_bus_load_telemetry_used": False,
        "interpretation": [
            "Thermal line MVA is a screening derivation from conductor/current references or an explicit conservative fallback; it is not an operator emergency or seasonal rating.",
            "Line X is a generic voltage-class screening assumption because conductor identity alone does not determine tower geometry or positive-sequence reactance.",
            "Transformer MVA from PSS is historical 31 March 2023 equipment evidence and may understate later upgrades.",
            "Spatial bus load is allocated by PSS-backed distribution-interface MVA and exactly conserves the existing statewide 8760-hour proxy; it is not measured substation telemetry.",
            "A constrained transport/DC sensitivity model can now be instantiated, but calibrated DC/AC validation still requires authoritative current network parameters and bus telemetry.",
        ],
    }

    args.out.mkdir(parents=True, exist_ok=True)
    _write_csv(
        args.out / "conductor_ampacity_reference.csv",
        ampacity_rows,
        [
            "conductor",
            "consensus_ampacity_a",
            "consensus_hit_count",
            "all_candidate_hits",
            "supporting_station_count",
            "dominance_fraction",
            "admitted_as_screening_reference",
            "basis",
        ],
    )
    _write_csv(
        args.out / "screening_buses.csv",
        screening_buses,
        sorted(
            {
                key
                for row in screening_buses
                for key in row
            }
        ),
    )
    _write_csv(
        args.out / "screening_lines.csv",
        screening_lines,
        sorted(
            {
                key
                for row in screening_lines
                for key in row
            }
        ),
    )
    _write_csv(
        args.out / "screening_transformer_links.csv",
        screening_tx,
        sorted(
            {
                key
                for row in screening_tx
                for key in row
            }
        ),
    )
    _write_csv(
        args.out / "load_weights.csv",
        load_weights,
        [
            "bus_id",
            "node_id",
            "location",
            "code",
            "voltage_kv",
            "pss_2023_distribution_interface_mva",
            "load_weight",
            "classification",
        ],
    )
    wide.to_parquet(
        args.out / "spatial_load_proxy_wide.parquet",
        compression="zstd",
    )
    (args.out / "transport_screening_qa.json").write_text(
        json.dumps(qa, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(qa, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
