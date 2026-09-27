"""Crosswalk the FY2024-25 generator census to KSEBL public generating sites and buses.

The mapper is deliberately fail-closed. A census asset may be matched to a public
KSEBL generating-site feature, but it is attached to the 110 kV+ network only
when that public site has an exact/derived KSEBL code relationship to an active
network node or is co-located within 250 m. Distributed/aggregate capacity is
never fabricated onto a bus.
"""
from __future__ import annotations

import argparse
import csv
import difflib
import json
import math
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CENSUS = ROOT / "results/inventory/fy2024_25_generator_census/generator_census.csv"
DEFAULT_ACQ = ROOT / "results/acquisition/network_public_v0_1"
DEFAULT_GRAPH = ROOT / "results/network/public_grid_graph_v0_2/network_graph_110plus.json"
DEFAULT_OUT = ROOT / "results/network/generator_bus_crosswalk_v0_1"

CLASSIFICATION = "FY2024_25_GENERATOR_TO_KSEBL_PUBLIC_BUS_CROSSWALK_V0_1"

PHYSICAL_BASES = {"station", "station_or_farm", "station_precise_unit_sum"}

# Explicit source-name/code aliases are restricted to clearly identifiable public
# map features where spelling, abbreviations or stage numerals defeat generic
# matching. They do not override a public Proposed/In Service conflict.
GENERATOR_CODE_ALIASES = {
    "ksebl-hydro-panniar": "PNYR-H",
    "ksebl-hydro-poringalkuthu-lbe": "PRBE",
    "ksebl-hydro-chembukadavu-1": "CMKV-I",
    "ksebl-hydro-chembukadavu-2": "CMKV-II",
    "ksebl-hydro-urumi-1": "URMI-H-I",
    "ksebl-hydro-urumi-2": "URMI-H-II",
    "ksebl-hydro-kuttiyadi-tailrace": "KUTR",
    "ksebl-hydro-perunthenaruvi": "PMTV-H",
    "ksebl-hydro-peruvannamuzhy": "PVMZ",
    "thermal-cpp-phillips-carbon-black": "PCBL",
    "thermal-central-ntpc-kayamkulam": "KYKM",
    "wind-cpp-malayala-manorama": "MMWM-W",
    "wind-ipp-inox": "INOX-W",
    "solar-other-hindalco": "HDIL",
    "solar-other-cial-prosumer": "CIAL",
    "solar-other-kmrl": "KMRL",
    "solar-other-saint-gobain": "STGB",
    "solar-ipp-anert-kuzhalmandam": "KZMN",
    "solar-ipp-rpckl-ambalathara": "ABTA-S",
    "solar-ipp-thdcil-paivalike": "PVLK",
    "solar-ipp-ntpc-kayamkulam-floating": "KYLM-S",
    "solar-ipp-cial-ettukudikka": "ETKD",
    "ksebl-solar-kollengode-ss": "KEKD-S",
    "ksebl-solar-edayar-ss": "EDYR-S",
    "ksebl-solar-agali": "AGLI-S",
    "ksebl-solar-kanjikode-ss": "KJKD-S",
    "ksebl-solar-kanjikkode-gm": "KJKD-S",
    "ksebl-solar-pothencode": "PCOD-S",
    "ksebl-solar-pezhekkappally": "MVPA-S",
}

# A very small set of assets are not represented as a generation point on the
# public map but are unambiguously named at a public substation site.
DIRECT_SUBSTATION_ALIASES = {
    "ksebl-thermal-bdpp": "BRPM",       # Brahmapuram Diesel Power Plant
    "ksebl-solar-brahmapuram": "BRPM", # Brahmapuram solar at same named site
}

SPELLING = {
    "kuttiady": "kuttiyadi",
    "madupetty": "mattupetty",
    "chembukadave": "chembukadavu",
    "peruvannamozhi": "peruvannamuzhy",
    "irutukanam": "iruttukkanam",
    "meenvallam": "meenvallom",
    "pathamkayam": "pathankayam",
    "kuzhalmannam": "kuzhalmandam",
    "paivalika": "paivalike",
    "ettekudukka": "ettukudikka",
    "perinad": "perunad",
    "kanjikkode": "kanjikode",
    "perumthenaruvi": "perunthenaruvi",
    "panniyar": "panniar",
}
STOP = {
    "hep", "shep", "gs", "ph", "project", "power", "plant", "scheme", "stage",
    "station", "substation", "solar", "prosumer", "gm", "spp", "hydel", "diesel",
    "combined", "cycle", "generation", "generating", "pvt", "ltd", "limited",
    "the", "of", "under", "co", "cogeneration", "rooftop", "floating", "farm",
    "wind", "mill",
}
ROMAN = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5"}


def _norm(value: Any) -> str:
    text = str(value or "").lower().replace("&", " and ")
    for a, b in SPELLING.items():
        text = text.replace(a, b)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    tokens = []
    for token in text.split():
        token = ROMAN.get(token, token)
        if token not in STOP:
            tokens.append(token)
    return " ".join(tokens)


def _name_score(a: str, b: str) -> tuple[float, float, float, bool]:
    aa, bb = _norm(a), _norm(b)
    A, B = set(aa.split()), set(bb.split())
    if not A or not B:
        return 0.0, 0.0, 0.0, False
    jaccard = len(A & B) / len(A | B)
    ratio = difflib.SequenceMatcher(None, aa, bb).ratio()
    containment = bool(aa in bb or bb in aa)
    score = 0.55 * jaccard + 0.35 * ratio + (0.10 if containment else 0.0)
    return score, jaccard, ratio, containment


def _technology_compatible(technology: str, public_type: str) -> bool:
    technology = str(technology or "").lower()
    public_type = str(public_type or "").lower()
    if technology == "hydro":
        return "hydel" in public_type or "ipp" in public_type
    if technology == "thermal":
        return "thermal" in public_type or "ipp" in public_type
    if technology == "solar":
        return "solar" in public_type or "ipp" in public_type
    if technology == "wind":
        return "wind" in public_type or "ipp" in public_type
    return False


def _haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lon1, lat1 = a
    lon2, lat2 = b
    radius = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(h), math.sqrt(1 - h))


def _load_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _as_float(value: Any) -> float:
    return float(str(value or "0").strip())


def _public_points(path: Path) -> list[dict[str, Any]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for feature in obj.get("features", []):
        props = feature.get("properties") or {}
        geom = feature.get("geometry") or {}
        coords = geom.get("coordinates") if geom.get("type") == "Point" else None
        if not coords or len(coords) < 2:
            continue
        rows.append({
            "location": str(props.get("Location") or ""),
            "code": str(props.get("Code") or ""),
            "status": str(props.get("Status") or ""),
            "owner": str(props.get("Owner") or ""),
            "type": str(props.get("Type") or ""),
            "lon": float(coords[0]),
            "lat": float(coords[1]),
        })
    return rows


def _root_code(code: str) -> str:
    code = str(code or "").upper()
    return re.sub(r"-(?:H|S|P)$", "", code)


def _node_for_public_site(site: dict[str, Any], nodes: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str, float | None]:
    code = str(site.get("code") or "").upper()
    root = _root_code(code)
    exact = [n for n in nodes if str(n.get("code") or "").upper() == code]
    if exact:
        node = min(exact, key=lambda n: _haversine_km((site["lon"], site["lat"]), (n["lon"], n["lat"])))
        distance = _haversine_km((site["lon"], site["lat"]), (node["lon"], node["lat"]))
        if distance <= 2.0:
            return node, "EXACT_PUBLIC_CODE_WITHIN_2KM", distance
    root_hits = [n for n in nodes if root and str(n.get("code") or "").upper() == root]
    if root_hits:
        node = min(root_hits, key=lambda n: _haversine_km((site["lon"], site["lat"]), (n["lon"], n["lat"])))
        distance = _haversine_km((site["lon"], site["lat"]), (node["lon"], node["lat"]))
        if distance <= 2.0:
            return node, "DERIVED_PUBLIC_CODE_ROOT_WITHIN_2KM", distance
    if not nodes:
        return None, "NO_ACTIVE_NETWORK_NODE", None
    ranked = sorted(
        ((_haversine_km((site["lon"], site["lat"]), (n["lon"], n["lat"])), n)
         for n in nodes),
        key=lambda item: (item[0], str(item[1].get("node_id") or "")),
    )
    distance, node = ranked[0]
    if distance <= 0.25:
        return node, "COLOCATED_WITHIN_250M", distance
    return None, "PUBLIC_SITE_NOT_ON_110PLUS_GRAPH", distance


def _best_public_match(asset: dict[str, Any], public: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    asset_id = asset["asset_id"]
    alias = GENERATOR_CODE_ALIASES.get(asset_id)
    if alias:
        hits = [row for row in public if row["code"].upper() == alias.upper()]
        if hits:
            chosen = hits[0]
            return chosen, {
                "method": "EXPLICIT_PUBLIC_CODE_ALIAS",
                "score": 1.0,
                "margin": 1.0,
                "candidate_location": chosen["location"],
                "candidate_code": chosen["code"],
            }

    ranked = []
    for row in public:
        base, jac, ratio, containment = _name_score(asset["plant"], row["location"])
        compatible = _technology_compatible(asset["technology"], row["type"])
        owner_bonus = 0.0
        if str(asset.get("owner") or "").upper() == "KSEBL":
            owner_bonus = 0.04 if row["owner"] == "KSEBL" else -0.05
        tech_bonus = 0.06 if compatible else -0.08
        status_bonus = 0.02 if row["status"] == "In Service" else -0.08
        total = base + owner_bonus + tech_bonus + status_bonus
        ranked.append((total, base, jac, ratio, containment, row))
    ranked.sort(key=lambda x: (x[0], x[1], x[2], x[3], x[5]["code"]), reverse=True)
    if not ranked:
        return None, {"method": "NO_PUBLIC_FEATURE", "score": 0.0, "margin": 0.0}
    best = ranked[0]
    second_score = ranked[1][0] if len(ranked) > 1 else -1.0
    total, base, jac, ratio, containment, row = best
    margin = total - second_score
    exact_norm = _norm(asset["plant"]) == _norm(row["location"])
    # Strict admission: exact normalized identity, or strong name agreement plus
    # a clear separation from the second-best candidate.
    compatible = _technology_compatible(asset["technology"], row["type"])
    admitted = compatible and (exact_norm or (base >= 0.72 and jac >= 0.50 and margin >= 0.08))
    evidence = {
        "method": "STRICT_NAME_MATCH" if admitted else "REVIEW_ONLY_NAME_CANDIDATE",
        "score": round(total, 6),
        "base_name_score": round(base, 6),
        "jaccard": round(jac, 6),
        "sequence_ratio": round(ratio, 6),
        "containment": containment,
        "margin": round(margin, 6),
        "candidate_location": row["location"],
        "candidate_code": row["code"],
    }
    return (row if admitted else None), evidence


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", type=Path, default=DEFAULT_CENSUS)
    parser.add_argument("--acquisition", type=Path, default=DEFAULT_ACQ)
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    census = _load_csv(args.census)
    public = _public_points(args.acquisition / "geojson/GeneratingStations_17.geojson")
    graph = json.loads(args.graph.read_text(encoding="utf-8"))
    nodes = graph.get("nodes") or []
    active_nodes_by_code: dict[str, list[dict[str, Any]]] = {}
    for node in nodes:
        active_nodes_by_code.setdefault(str(node.get("code") or "").upper(), []).append(node)

    rows: list[dict[str, Any]] = []
    for asset in census:
        capacity = _as_float(asset["capacity_mw"])
        basis = str(asset.get("capacity_basis") or "")
        base = {
            "asset_id": asset["asset_id"],
            "plant": asset["plant"],
            "technology": asset["technology"],
            "owner": asset.get("owner", ""),
            "commercial_class": asset.get("commercial_class", ""),
            "capacity_mw": capacity,
            "capacity_basis": basis,
        }
        if basis not in PHYSICAL_BASES:
            rows.append({
                **base,
                "site_match_status": "AGGREGATE_NOT_PUBLIC_SITE_MAPPABLE",
                "bus_attachment_status": "NOT_ATTEMPTED_AGGREGATE",
                "network_node_id": "",
            })
            continue

        direct_code = DIRECT_SUBSTATION_ALIASES.get(asset["asset_id"])
        if direct_code and direct_code in active_nodes_by_code:
            node = active_nodes_by_code[direct_code][0]
            rows.append({
                **base,
                "site_match_status": "DIRECT_PUBLIC_SUBSTATION_ALIAS",
                "site_match_method": "EXPLICIT_NAMED_SITE_ALIAS",
                "public_generation_location": "",
                "public_generation_code": "",
                "public_generation_status": "",
                "public_generation_type": "",
                "public_generation_owner": "",
                "bus_attachment_status": "DIRECT_NAMED_SUBSTATION",
                "network_node_id": node["node_id"],
                "network_node_location": node["location"],
                "network_node_code": node["code"],
                "network_node_kind": node["kind"],
                "network_node_voltage_class_kv": node.get("voltage_class_kv"),
                "network_node_district": node.get("district"),
                "site_to_bus_distance_km": 0.0,
            })
            continue

        site, evidence = _best_public_match(asset, public)
        if site is None:
            rows.append({
                **base,
                "site_match_status": "NO_ADMITTED_PUBLIC_GENERATION_MATCH",
                "site_match_method": evidence.get("method", ""),
                "site_match_score": evidence.get("score", ""),
                "site_match_margin": evidence.get("margin", ""),
                "review_candidate_location": evidence.get("candidate_location", ""),
                "review_candidate_code": evidence.get("candidate_code", ""),
                "bus_attachment_status": "NO_PUBLIC_SITE",
                "network_node_id": "",
            })
            continue

        if site["status"] != "In Service":
            rows.append({
                **base,
                "site_match_status": "PUBLIC_STATUS_CONFLICT",
                "site_match_method": evidence["method"],
                "site_match_score": evidence.get("score", ""),
                "site_match_margin": evidence.get("margin", ""),
                "public_generation_location": site["location"],
                "public_generation_code": site["code"],
                "public_generation_status": site["status"],
                "public_generation_type": site["type"],
                "public_generation_owner": site["owner"],
                "public_generation_lon": site["lon"],
                "public_generation_lat": site["lat"],
                "bus_attachment_status": "BLOCKED_BY_STATUS_CONFLICT",
                "network_node_id": "",
            })
            continue

        node, bus_method, distance = _node_for_public_site(site, nodes)
        rows.append({
            **base,
            "site_match_status": "PUBLIC_GENERATION_SITE_MATCHED",
            "site_match_method": evidence["method"],
            "site_match_score": evidence.get("score", ""),
            "site_match_margin": evidence.get("margin", ""),
            "public_generation_location": site["location"],
            "public_generation_code": site["code"],
            "public_generation_status": site["status"],
            "public_generation_type": site["type"],
            "public_generation_owner": site["owner"],
            "public_generation_lon": site["lon"],
            "public_generation_lat": site["lat"],
            "bus_attachment_status": bus_method,
            "network_node_id": node["node_id"] if node else "",
            "network_node_location": node["location"] if node else "",
            "network_node_code": node["code"] if node else "",
            "network_node_kind": node["kind"] if node else "",
            "network_node_voltage_class_kv": node.get("voltage_class_kv") if node else "",
            "network_node_district": node.get("district") if node else "",
            "site_to_bus_distance_km": round(distance, 6) if distance is not None else "",
        })

    total_mw = sum(float(r["capacity_mw"]) for r in rows)
    physical = [r for r in rows if r["capacity_basis"] in PHYSICAL_BASES]
    aggregate = [r for r in rows if r["capacity_basis"] not in PHYSICAL_BASES]
    matched_site = [r for r in physical if r["site_match_status"] == "PUBLIC_GENERATION_SITE_MATCHED"]
    attached = [r for r in physical if r.get("network_node_id")]
    status_conflicts = [r for r in physical if r["site_match_status"] == "PUBLIC_STATUS_CONFLICT"]
    qa = {
        "classification": "FY2024_25_GENERATOR_TO_KSEBL_PUBLIC_BUS_CROSSWALK_V0_1_QA",
        "census_rows": len(rows),
        "census_capacity_mw": round(total_mw, 6),
        "physical_asset_rows": len(physical),
        "physical_asset_capacity_mw": round(sum(float(r["capacity_mw"]) for r in physical), 6),
        "aggregate_rows": len(aggregate),
        "aggregate_capacity_mw": round(sum(float(r["capacity_mw"]) for r in aggregate), 6),
        "physical_rows_with_public_generation_site_match": len(matched_site),
        "physical_capacity_with_public_generation_site_match_mw": round(sum(float(r["capacity_mw"]) for r in matched_site), 6),
        "physical_rows_attached_to_110plus_network": len(attached),
        "physical_capacity_attached_to_110plus_network_mw": round(sum(float(r["capacity_mw"]) for r in attached), 6),
        "physical_rows_with_public_status_conflict": len(status_conflicts),
        "physical_capacity_with_public_status_conflict_mw": round(sum(float(r["capacity_mw"]) for r in status_conflicts), 6),
        "aggregate_capacity_attached_to_bus_mw": round(sum(float(r["capacity_mw"]) for r in aggregate if r.get("network_node_id")), 6),
        "all_aggregate_capacity_left_unallocated": not any(r.get("network_node_id") for r in aggregate),
        "bus_attachment_policy": {
            "accepted": ["public code/code-root only when site is <=2 km from node", "co-location <=0.25 km", "two explicit named-site aliases"],
            "rejected": ["nearest arbitrary bus beyond 0.25 km", "aggregate/distributed bucket", "public Proposed/In Service conflict"],
        },
        "power_flow_ready": False,
    }

    args.out.mkdir(parents=True, exist_ok=True)
    _write_csv(args.out / "generator_bus_crosswalk.csv", rows)
    (args.out / "generator_bus_crosswalk.json").write_text(
        json.dumps({"classification": CLASSIFICATION, "prepared_date": "2026-09-27", "rows": rows}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (args.out / "generator_bus_crosswalk_qa.json").write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(qa, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
