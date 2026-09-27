"""Extract KSEBL Power System Statistics 2022-23 grid evidence.

The public PSS report is dated 31 March 2023. This parser crosswalks its
Table 33 substation transformer inventory and Table 34 line conductor inventory
to the newer public KSEBL grid-map graph. Matches are deliberately fail-closed:
no unmatched PSS row is promoted to a graph asset.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH = ROOT / "results/network/public_grid_graph_v0_2/network_graph_110plus.json"
DEFAULT_SOURCE_EDGES = ROOT / "results/network/public_grid_graph_v0_2/network_source_edges_110plus.csv"
DEFAULT_OUT = ROOT / "results/network/public_pss_evidence_v0_1"
DEFAULT_CACHE = ROOT / "results/acquisition/kseb_pss_2022_23/power_system_statistics_2022_23.pdf"
PSS_URL = (
    "https://old.kseb.in/index.php?Itemid=811&catid=70&id=35634&lang=en"
    "&m=0&option=com_jdownloads&task=download.send"
)
SOURCE_AS_OF = "2023-03-31"
CLASSIFICATION = "KSEBL_PSS_2022_23_PUBLIC_GRID_EVIDENCE_V0_1"

VOLTAGE_RATIO_RE = re.compile(
    r"(?<!\d)(400|320|220|110|66|33|22)\s*/\s*(220|110|66|33|22|11)(?!\d)"
)
NUMBER_RE = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?")
CONDUCTOR_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("TWIN_GREAT_HORNBILL", re.compile(r"\bTWIN\s+GREAT\s+HORNBILL\b", re.I)),
    ("QUAD_MOOSE", re.compile(r"\bQUAD\s+(?:ACSR\s+)?MOOSE\b", re.I)),
    ("TWIN_MOOSE", re.compile(r"\b(?:TWIN|2)\s+(?:ACSR\s+)?MOOSE\b", re.I)),
    ("TWIN_PANTHER", re.compile(r"\bTWIN\s+(?:ACSR\s+)?PANTHER\b", re.I)),
    ("ACCC_DRAKE", re.compile(r"\bACCC\s*,?\s*DRAKE\b", re.I)),
    ("ACCC_ERANAD", re.compile(r"\bACCC\s+ERANAD\b", re.I)),
    (
        "ACSR_KUNDAH_TWIN_PANTHER",
        re.compile(r"\bACSR\s+KUNDAH\s*/\s*TWIN\s+PANTHER\b", re.I),
    ),
    ("ACSR_WOLF_PANTHER", re.compile(r"\bACSR\s+WOLF\s*/\s*PANTHER\b", re.I)),
    ("ACSR_WOLF_TIGER", re.compile(r"\bACSR\s+WOLF\s*/\s*TIGER\b", re.I)),
    ("ACSR_MOOSE", re.compile(r"\bACSR\s+MOOSE\b", re.I)),
    ("ACSR_KUNDAH", re.compile(r"\b(?:ACSR\s+)?KUNDAH\b", re.I)),
    ("ACSR_PANTHER", re.compile(r"\bACSR\s+PANTHER\b", re.I)),
    ("ACSR_LYNX", re.compile(r"\bACSR\s+LYNX\b", re.I)),
    ("ACSR_WOLF", re.compile(r"\bACSR\s+WOLF\b", re.I)),
    ("ACSR_TIGER", re.compile(r"\b(?:ACSR\s+)?TIGER\b", re.I)),
    ("HTLS", re.compile(r"\bHTLS\b", re.I)),
    ("AL59", re.compile(r"\bAL\s*59\b", re.I)),
    ("ACCC", re.compile(r"\bACCC\b", re.I)),
    ("LAPWING", re.compile(r"\bLAPWING\b", re.I)),
    (
        "UG_CABLE",
        re.compile(
            r"\b(?:UG|UNDERGROUND)\b.*?\bCABLE\b|\b\d+\s*SQ\s*MM\s+UG\b",
            re.I,
        ),
    ),
]


def _norm_space(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _norm_code(value: Any) -> str:
    return re.sub(r"[^A-Z0-9]+", "", str(value or "").upper())


def _norm_name(value: Any) -> str:
    text = str(value or "").upper()
    for old, new in {
        "ANGAMALLY": "ANGAMALY",
        "AMBALAMUGHAL": "AMBALAMUGAL",
        "AREACODE": "AREEKODE",
        "CHENGANOOR": "CHENGANNUR",
    }.items():
        text = text.replace(old, new)
    return re.sub(r"[^A-Z0-9]+", "", text)


def _download_pdf(url: str, cache: Path) -> bytes:
    if cache.exists() and cache.stat().st_size > 100_000:
        data = cache.read_bytes()
        if data.startswith(b"%PDF"):
            return data
    request = urllib.request.Request(
        url, headers={"User-Agent": "kerala2040-public-research/1.0"}
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        data = response.read()
    if not data.startswith(b"%PDF") or len(data) < 100_000:
        raise RuntimeError(
            "KSEBL Power System Statistics download did not return a usable PDF"
        )
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(data)
    return data


def _pdf_lines(data: bytes) -> list[dict[str, Any]]:
    reader = PdfReader(io.BytesIO(data))
    rows: list[dict[str, Any]] = []
    for page_index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        for line_index, raw in enumerate(text.splitlines()):
            line = _norm_space(raw)
            if line:
                rows.append(
                    {
                        "page_index": page_index,
                        "line_index": line_index,
                        "text": line,
                    }
                )
    return rows


def _extract_conductor(text: str) -> str | None:
    for name, pattern in CONDUCTOR_PATTERNS:
        if pattern.search(text):
            return name
    return None


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


def _line_context(lines: list[dict[str, Any]], index: int) -> str:
    base = lines[index]
    parts = [base["text"]]
    for offset in (1, 2):
        if index + offset >= len(lines):
            break
        nxt = lines[index + offset]
        if nxt["page_index"] != base["page_index"]:
            break
        if re.match(r"^\d+\s+", nxt["text"]):
            break
        parts.append(nxt["text"])
    return " ".join(parts)


def _extract_line_evidence(
    lines: list[dict[str, Any]],
    source_edges: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    code_meta: dict[str, dict[str, Any]] = {}
    for edge in source_edges:
        raw_code = _norm_space(edge.get("feeder_code"))
        norm = _norm_code(raw_code)
        voltage = int(float(edge.get("voltage_kv") or 0))
        if len(norm) < 4 or voltage < 110:
            continue
        item = code_meta.setdefault(
            norm, {"raw_codes": set(), "voltages": set()}
        )
        item["raw_codes"].add(raw_code)
        item["voltages"].add(voltage)
    code_order = sorted(code_meta, key=len, reverse=True)

    by_code: dict[str, dict[str, Any]] = {}
    ambiguous: list[dict[str, Any]] = []
    table_started = False
    table_ended = False
    for index, line_row in enumerate(lines):
        text = line_row["text"]
        upper = text.upper()
        if "LIST OF EHV AND 33 KV TRANSMISSION LINES" in upper:
            table_started = True
            continue
        if table_started and (
            "TABLE 35" in upper or "COST PER UNIT SENT OUT" in upper
        ):
            table_ended = True
        if not table_started or table_ended:
            continue
        norm_line = _norm_code(text)
        matches = [code for code in code_order if code in norm_line]
        if not matches:
            continue
        longest = len(matches[0])
        candidates = [code for code in matches if len(code) == longest]
        if len(candidates) != 1:
            ambiguous.append(
                {
                    "page_index": line_row["page_index"],
                    "raw_text": text,
                    "candidate_normalized_codes": ";".join(candidates),
                }
            )
            continue
        code = candidates[0]
        context = _line_context(lines, index)
        conductor = _extract_conductor(context)
        if conductor is None:
            context = text
        evidence = {
            "normalized_feeder_code": code,
            "source_feeder_codes": ";".join(
                sorted(code_meta[code]["raw_codes"])
            ),
            "source_voltage_kv": ";".join(
                map(str, sorted(code_meta[code]["voltages"]))
            ),
            "conductor": conductor or "",
            "pdf_page_index": line_row["page_index"],
            "raw_text": context,
            "source_as_of": SOURCE_AS_OF,
            "source_url": PSS_URL,
            "mapping_basis": (
                "EXACT_NORMALIZED_GRAPH_FEEDER_CODE_IN_PSS_ROW"
            ),
        }
        previous = by_code.get(code)
        if previous is None or (
            not previous["conductor"] and evidence["conductor"]
        ):
            by_code[code] = evidence
    return list(by_code.values()), ambiguous


def _node_candidates(graph: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for node in graph.get("nodes", []):
        if node.get("synthetic") or node.get("kind") == "geometry_junction":
            continue
        node_id = str(node.get("node_id") or "")
        location = _norm_space(node.get("location"))
        norm = _norm_name(location)
        if not node_id or len(norm) < 4 or node_id in seen:
            continue
        seen.add(node_id)
        out.append(
            {
                "node_id": node_id,
                "location": location,
                "code": _norm_space(node.get("code")),
                "kind": _norm_space(node.get("kind")),
                "voltage_class_kv": node.get("voltage_class_kv"),
                "norm_location": norm,
            }
        )
    return out


def _match_station(
    prefix: str, candidates: list[dict[str, Any]]
) -> tuple[dict[str, Any] | None, str]:
    norm_prefix = _norm_name(prefix)
    exact: list[tuple[int, int, dict[str, Any]]] = []
    for node in candidates:
        loc = node["norm_location"]
        pos = norm_prefix.find(loc)
        if pos >= 0:
            exact.append((pos, -len(loc), node))
    if not exact:
        return None, "NO_EXACT_NORMALIZED_LOCATION_MATCH"
    exact.sort(
        key=lambda item: (
            item[0],
            item[1],
            0 if str(item[2]["node_id"]).startswith("SS:") else 1,
        )
    )
    best = exact[0]
    tied = [item for item in exact if item[0:2] == best[0:2]]
    ss = [
        item
        for item in tied
        if str(item[2]["node_id"]).startswith("SS:")
    ]
    if len(ss) == 1:
        return (
            ss[0][2],
            "EXACT_NORMALIZED_LOCATION_SUBSTATION_PREFERRED",
        )
    unique_ids = {item[2]["node_id"] for item in tied}
    if len(unique_ids) > 1:
        return None, "AMBIGUOUS_EXACT_NORMALIZED_LOCATION_MATCH"
    return best[2], "EXACT_NORMALIZED_LOCATION"


def _extract_station_transformers(
    lines: list[dict[str, Any]], graph: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates = _node_candidates(graph)
    evidence: list[dict[str, Any]] = []
    unmatched: list[dict[str, Any]] = []
    table_started = False
    table_ended = False
    for row in lines:
        text = row["text"]
        upper = text.upper()
        if "LIST OF EHV AND 33 KV SUBSTATIONS" in upper:
            table_started = True
            continue
        if (
            table_started
            and "LIST OF EHV AND 33 KV TRANSMISSION LINES" in upper
        ):
            table_ended = True
        if not table_started or table_ended:
            continue
        ratios = list(VOLTAGE_RATIO_RE.finditer(text))
        if not ratios:
            continue
        first_ratio = ratios[0]
        prefix = text[: first_ratio.start()]
        node, basis = _match_station(prefix, candidates)
        if node is None:
            unmatched.append(
                {
                    "pdf_page_index": row["page_index"],
                    "raw_text": text,
                    "reason": basis,
                }
            )
            continue
        for ratio_index, match in enumerate(ratios):
            high, low = int(match.group(1)), int(match.group(2))
            seg_end = (
                ratios[ratio_index + 1].start()
                if ratio_index + 1 < len(ratios)
                else len(text)
            )
            after = text[match.end() : seg_end]
            numbers = [
                float(value) for value in NUMBER_RE.findall(after)
            ]
            unit_mva = numbers[0] if len(numbers) >= 1 else None
            count = (
                int(numbers[1])
                if len(numbers) >= 2 and numbers[1].is_integer()
                else None
            )
            total_mva = numbers[2] if len(numbers) >= 3 else None
            if (
                unit_mva is not None
                and count is not None
                and total_mva is not None
            ):
                expected = unit_mva * count
                if abs(expected - total_mva) > max(
                    0.2, 0.02 * max(expected, total_mva, 1.0)
                ):
                    total_mva = None
            evidence.append(
                {
                    "node_id": node["node_id"],
                    "code": node["code"],
                    "location": node["location"],
                    "kind": node["kind"],
                    "voltage_class_kv": node["voltage_class_kv"],
                    "high_kv": high,
                    "low_kv": low,
                    "unit_mva": unit_mva,
                    "transformer_count": count,
                    "total_mva": total_mva,
                    "pdf_page_index": row["page_index"],
                    "raw_text": text,
                    "source_as_of": SOURCE_AS_OF,
                    "source_url": PSS_URL,
                    "mapping_basis": basis,
                    "capacity_tuple_reconciled": total_mva is not None,
                }
            )
    dedup: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in evidence:
        key = (
            row["node_id"],
            row["high_kv"],
            row["low_kv"],
            row["unit_mva"],
            row["transformer_count"],
            row["total_mva"],
            row["raw_text"],
        )
        dedup[key] = row
    return list(dedup.values()), unmatched


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    parser.add_argument(
        "--source-edges", type=Path, default=DEFAULT_SOURCE_EDGES
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--cache-pdf", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--source-url", default=PSS_URL)
    args = parser.parse_args()

    graph = json.loads(args.graph.read_text(encoding="utf-8"))
    with args.source_edges.open(newline="", encoding="utf-8") as handle:
        source_edges = list(csv.DictReader(handle))
    pdf = _download_pdf(args.source_url, args.cache_pdf)
    lines = _pdf_lines(pdf)

    line_evidence, line_ambiguous = _extract_line_evidence(
        lines, source_edges
    )
    station_evidence, station_unmatched = _extract_station_transformers(
        lines, graph
    )

    code_to_evidence = {
        row["normalized_feeder_code"]: row for row in line_evidence
    }
    edge_rows: list[dict[str, Any]] = []
    for edge in source_edges:
        code = _norm_code(edge.get("feeder_code"))
        ev = code_to_evidence.get(code)
        edge_rows.append(
            {
                "source_edge_id": edge.get("source_edge_id", ""),
                "feeder_code": edge.get("feeder_code", ""),
                "normalized_feeder_code": code,
                "voltage_kv": edge.get("voltage_kv", ""),
                "name": edge.get("name", ""),
                "pss_conductor": ev["conductor"] if ev else "",
                "pss_row_matched": ev is not None,
                "pss_conductor_resolved": bool(
                    ev and ev["conductor"]
                ),
                "pss_pdf_page_index": (
                    ev["pdf_page_index"] if ev else ""
                ),
                "pss_raw_text": ev["raw_text"] if ev else "",
                "source_as_of": SOURCE_AS_OF if ev else "",
                "mapping_basis": ev["mapping_basis"] if ev else "",
            }
        )

    aggregate: dict[tuple[str, int, int], dict[str, Any]] = {}
    for row in station_evidence:
        if not row["capacity_tuple_reconciled"]:
            continue
        key = (
            row["node_id"],
            int(row["high_kv"]),
            int(row["low_kv"]),
        )
        current = aggregate.setdefault(
            key,
            {
                "node_id": row["node_id"],
                "code": row["code"],
                "location": row["location"],
                "high_kv": row["high_kv"],
                "low_kv": row["low_kv"],
                "aggregate_total_mva": 0.0,
                "source_tuple_count": 0,
                "source_as_of": SOURCE_AS_OF,
            },
        )
        current["aggregate_total_mva"] += float(row["total_mva"])
        current["source_tuple_count"] += 1
    aggregate_rows = list(aggregate.values())

    graph_codes = {
        _norm_code(row.get("feeder_code"))
        for row in source_edges
        if len(_norm_code(row.get("feeder_code"))) >= 4
    }
    matched_codes = {
        row["normalized_feeder_code"] for row in line_evidence
    }
    qa = {
        "classification": CLASSIFICATION + "_QA",
        "source_url": args.source_url,
        "source_as_of": SOURCE_AS_OF,
        "pdf_bytes": len(pdf),
        "pdf_text_lines": len(lines),
        "graph_feeder_codes_considered": len(graph_codes),
        "pss_feeder_codes_matched": len(matched_codes),
        "source_edges": len(edge_rows),
        "source_edges_with_pss_row_match": sum(
            row["pss_row_matched"] for row in edge_rows
        ),
        "source_edges_with_conductor_identity": sum(
            row["pss_conductor_resolved"] for row in edge_rows
        ),
        "line_ambiguous_rows": len(line_ambiguous),
        "station_transformer_evidence_rows": len(station_evidence),
        "station_transformer_rows_with_reconciled_capacity": sum(
            row["capacity_tuple_reconciled"]
            for row in station_evidence
        ),
        "stations_mapped": len(
            {row["node_id"] for row in station_evidence}
        ),
        "aggregate_transformer_voltage_links_with_capacity": len(
            aggregate_rows
        ),
        "station_unmatched_rows": len(station_unmatched),
        "conductor_counts_on_source_edges": dict(
            sorted(
                Counter(
                    row["pss_conductor"]
                    for row in edge_rows
                    if row["pss_conductor"]
                ).items()
            )
        ),
        "interpretation": [
            "PSS 2022-23 is official historical inventory as of 31 March 2023, not proof of unchanged 2026 equipment.",
            "Line rows are crosswalked only by exact normalized feeder code already present in the newer public graph.",
            "Substation rows are promoted only when the station name maps to a unique public graph node.",
            "Transformer MVA is admitted only when per-unit MVA times count reconciles to the printed total MVA.",
            "Unmatched and ambiguous source rows remain outside the model evidence layer.",
        ],
    }

    args.out.mkdir(parents=True, exist_ok=True)
    _write_csv(
        args.out / "pss_line_feeder_evidence.csv",
        line_evidence,
        [
            "normalized_feeder_code",
            "source_feeder_codes",
            "source_voltage_kv",
            "conductor",
            "pdf_page_index",
            "raw_text",
            "source_as_of",
            "source_url",
            "mapping_basis",
        ],
    )
    _write_csv(
        args.out / "pss_source_edge_crosswalk.csv",
        edge_rows,
        [
            "source_edge_id",
            "feeder_code",
            "normalized_feeder_code",
            "voltage_kv",
            "name",
            "pss_conductor",
            "pss_row_matched",
            "pss_conductor_resolved",
            "pss_pdf_page_index",
            "pss_raw_text",
            "source_as_of",
            "mapping_basis",
        ],
    )
    _write_csv(
        args.out / "pss_line_ambiguous_rows.csv",
        line_ambiguous,
        ["page_index", "raw_text", "candidate_normalized_codes"],
    )
    _write_csv(
        args.out / "pss_station_transformer_evidence.csv",
        station_evidence,
        [
            "node_id",
            "code",
            "location",
            "kind",
            "voltage_class_kv",
            "high_kv",
            "low_kv",
            "unit_mva",
            "transformer_count",
            "total_mva",
            "capacity_tuple_reconciled",
            "pdf_page_index",
            "raw_text",
            "source_as_of",
            "source_url",
            "mapping_basis",
        ],
    )
    _write_csv(
        args.out / "pss_station_transformer_capacity_links.csv",
        aggregate_rows,
        [
            "node_id",
            "code",
            "location",
            "high_kv",
            "low_kv",
            "aggregate_total_mva",
            "source_tuple_count",
            "source_as_of",
        ],
    )
    _write_csv(
        args.out / "pss_station_unmatched_rows.csv",
        station_unmatched,
        ["pdf_page_index", "raw_text", "reason"],
    )
    (args.out / "pss_evidence_qa.json").write_text(
        json.dumps(qa, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(qa, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
