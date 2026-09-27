"""Promote high-confidence transformer/bus evidence from public KSEBL SLD text mining.

This stage consumes text-first SLD mining output. It admits only tuples where a
transformer term, explicit voltage pair/triple, and MVA rating occur locally in
one context. Fault-level/short-circuit MVA values are rejected. The resulting
records are evidence tuples, not a nameplate-complete equipment master.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results/network/public_sld_mining_v0_1/sld_equipment_mining.json"
DEFAULT_OUT = ROOT / "results/network/public_sld_transformers_v0_1"

CLASSIFICATION = "KSEBL_PUBLIC_SLD_TRANSFORMER_EVIDENCE_V0_1_NOT_NAMEPLATE_MASTER"

KV_LEVELS = (400, 320, 230, 220, 110, 66, 33, 22, 11)
KV = r"(?:400|320|230|220|110|66|33|22|11)"
VOLTAGE_EXPR_RE = re.compile(
    rf"(?<!\d)({KV})\s*(?:k\s*v)?\s*(?:/|-)\s*"
    rf"({KV})\s*(?:k\s*v)?"
    rf"(?:\s*(?:/|-)\s*({KV})\s*(?:k\s*v)?)?\b",
    re.IGNORECASE,
)
COMPACT_VOLTAGE_MAP = {
    f"{high}{low}": (high, low)
    for high in KV_LEVELS
    for low in KV_LEVELS
    if high > low
}
COMPACT_VOLTAGE_MAP.update(
    {
        f"{high}{middle}{low}": (high, middle, low)
        for high in KV_LEVELS
        for middle in KV_LEVELS
        for low in KV_LEVELS
        if high > middle > low
    }
)
_COMPACT_PATTERN = "|".join(sorted(COMPACT_VOLTAGE_MAP, key=len, reverse=True))
COMPACT_VOLTAGE_RE = re.compile(
    rf"(?<!\d)({_COMPACT_PATTERN})\s*k\s*v\b",
    re.IGNORECASE,
)

RATING_EXPR_RE = re.compile(
    r"(?<![\d.])(\d+(?:\.\d+)?)"
    r"(?:\s*/\s*(\d+(?:\.\d+)?))?"
    r"(?:\s*/\s*(\d+(?:\.\d+)?))?\s*M\s*V\s*A\b",
    re.IGNORECASE,
)
TRANSFORMER_RE = re.compile(
    r"\b(?:POWER\s+TRANSFORMER|AUTO\s*TRANSFORMER|AUTOTRANSFORMER|TRANSFORMER|ICT|PTR|TFR|TR)\b",
    re.IGNORECASE,
)
FAULT_RE = re.compile(r"\b(?:FAULT\s*LEVEL|SHORT\s*CIRCUIT|SC\s*LEVEL|FAULT\s*MVA)\b", re.IGNORECASE)
PROPOSED_RE = re.compile(r"\bPROPOSED\b", re.IGNORECASE)
COMPONENT_BANK_RE = re.compile(r"M\s*V\s*A\s*[xX×]\s*\d+", re.IGNORECASE)

LABEL_PATTERNS = [
    re.compile(r"(?:TRANSFORMER|ICT|PTR|TFR|TR)\s*(?:BANK\s*)?(?:NO\.?|#|[-:]\s*)\s*([A-Z0-9IVX]+)\b", re.IGNORECASE),
    re.compile(r"TRANSFORMER\s+BANK\s*[-:]?\s*([IVX]+|\d+)\b", re.IGNORECASE),
    re.compile(r"\b(?:ICT|PTR|TFR|TR)\s*[-#:]\s*([A-Z0-9IVX]+)\b", re.IGNORECASE),
]


def _norm_space(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _normalize_voltage_notation(text: str) -> tuple[str, bool]:
    """Normalize only unambiguous KSEBL transformer voltage notation.

    Public SLD text extraction often emits either repeated units
    (220KV/110KV/11KV) or concatenated voltage levels (11066 KV, 6611 KV).
    Compact forms are expanded only when the complete numeric token is an
    ordered pair/triple of known system voltage levels and is immediately
    followed by kV. Other numeric strings are left untouched.
    """
    normalized = _norm_space(text)

    def expand(match: re.Match[str]) -> str:
        levels = COMPACT_VOLTAGE_MAP[match.group(1)]
        return "/".join(map(str, levels)) + " kV"

    expanded = COMPACT_VOLTAGE_RE.sub(expand, normalized)
    return expanded, expanded != normalized


def _span_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    if a[1] < b[0]:
        return b[0] - a[1]
    if b[1] < a[0]:
        return a[0] - b[1]
    return 0


def _extract_label(text: str, center: tuple[int, int]) -> str | None:
    lo = max(0, center[0] - 70)
    hi = min(len(text), center[1] + 70)
    window = text[lo:hi]
    for pattern in LABEL_PATTERNS:
        match = pattern.search(window)
        if match:
            label = re.sub(r"[^A-Z0-9]+", "-", match.group(1).upper()).strip("-")
            if label and label not in {"KV", "MVA"}:
                return label
    return None


def _parse_context(context: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_text = _norm_space(context)
    if not source_text:
        return [], []
    text, voltage_notation_normalized = _normalize_voltage_notation(source_text)
    voltages = list(VOLTAGE_EXPR_RE.finditer(text))
    ratings = list(RATING_EXPR_RE.finditer(text))
    transformers = list(TRANSFORMER_RE.finditer(text))
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for rating in ratings:
        values = [float(v) for v in rating.groups() if v is not None]
        reason = None
        if not values or max(values) < 0.1 or max(values) > 700:
            reason = "RATING_OUTSIDE_PLAUSIBLE_TRANSFORMER_RANGE"
        local_fault = text[max(0, rating.start()-65): min(len(text), rating.end()+65)]
        if reason is None and FAULT_RE.search(local_fault):
            reason = "FAULT_OR_SHORT_CIRCUIT_MVA"
        after = text[rating.end(): min(len(text), rating.end()+16)]
        if reason is None and COMPONENT_BANK_RE.search(rating.group(0) + after):
            reason = "COMPONENT_MVA_TIMES_BANK_COUNT"

        nearest_v = min(voltages, key=lambda m: _span_distance(rating.span(), m.span()), default=None)
        nearest_t = min(transformers, key=lambda m: _span_distance(rating.span(), m.span()), default=None)
        vdist = _span_distance(rating.span(), nearest_v.span()) if nearest_v else 9999
        tdist = _span_distance(rating.span(), nearest_t.span()) if nearest_t else 9999
        if reason is None and (nearest_v is None or vdist > 50):
            reason = "NO_NEARBY_EXPLICIT_VOLTAGE_PAIR"
        if reason is None and (nearest_t is None or tdist > 50):
            reason = "NO_NEARBY_TRANSFORMER_TERM"

        base = {
            "context": source_text,
            "normalized_context": text if voltage_notation_normalized else None,
            "voltage_notation_normalized": voltage_notation_normalized,
            "rating_values_mva": values,
            "rating_expression": rating.group(0),
            "voltage_distance_chars": None if nearest_v is None else vdist,
            "transformer_distance_chars": None if nearest_t is None else tdist,
        }
        if reason is not None:
            rejected.append({**base, "reason": reason})
            continue

        levels = [int(v) for v in nearest_v.groups() if v is not None]
        local = text[max(0, min(rating.start(), nearest_v.start(), nearest_t.start())-55):
                     min(len(text), max(rating.end(), nearest_v.end(), nearest_t.end())+55)]
        label = _extract_label(text, nearest_t.span())
        accepted.append({
            **base,
            "voltage_levels_kv": levels,
            "voltage_expression": nearest_v.group(0),
            "equipment_term": nearest_t.group(0),
            "equipment_label": label,
            "identity_complete": bool(label),
            "proposed": bool(PROPOSED_RE.search(local)),
            "admission_class": (
                "HIGH_CONFIDENCE_TEXT_TUPLE_NORMALIZED_VOLTAGE_NOTATION"
                if voltage_notation_normalized
                else "HIGH_CONFIDENCE_TEXT_TUPLE"
            ),
        })
    return accepted, rejected


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    records = source.get("records") or []

    admitted: list[dict[str, Any]] = []
    review: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    rejection_counts: Counter[str] = Counter()

    for station in records:
        code = str(station.get("code") or "").strip()
        location = str(station.get("location") or "").strip()
        mining = station.get("mining") or {}
        contexts = mining.get("equipment_contexts") or []
        for context_index, context in enumerate(contexts):
            accepted, rejected = _parse_context(context)
            for item in rejected:
                rejection_counts[item["reason"]] += 1
                # Keep only transformer-related MVA contexts in the manual-review queue.
                if TRANSFORMER_RE.search(str(context)) and RATING_EXPR_RE.search(str(context)):
                    review.append({
                        "code": code,
                        "location": location,
                        "class": station.get("class", ""),
                        "status": station.get("status", ""),
                        "pdf_filename": station.get("pdf_filename", ""),
                        "context_index": context_index,
                        **item,
                    })
            for item in accepted:
                key = (
                    code,
                    tuple(item["voltage_levels_kv"]),
                    tuple(item["rating_values_mva"]),
                    item["equipment_label"],
                    item["proposed"],
                )
                if key in seen:
                    continue
                seen.add(key)
                digest = hashlib.sha1(repr(key).encode("utf-8")).hexdigest()[:10]
                admitted.append({
                    "evidence_id": f"{code or 'NO_CODE'}:{digest}",
                    "code": code,
                    "location": location,
                    "class": station.get("class", ""),
                    "status": station.get("status", ""),
                    "owner": station.get("owner", ""),
                    "type": station.get("type", ""),
                    "url": station.get("url", ""),
                    "pdf_filename": station.get("pdf_filename", ""),
                    **item,
                })

    # Station-level bus evidence. Public station class is retained alongside voltage
    # levels explicitly seen in admitted transformer tuples; proposed-only levels do
    # not establish an active bus.
    by_station: dict[str, list[dict[str, Any]]] = defaultdict(list)
    metadata: dict[str, dict[str, Any]] = {}
    for station in records:
        code = str(station.get("code") or "").strip()
        if code:
            metadata[code] = station
    for row in admitted:
        by_station[row["code"]].append(row)

    buses: list[dict[str, Any]] = []
    for code, rows in sorted(by_station.items()):
        meta = metadata.get(code, {})
        active = [r for r in rows if not r["proposed"]]
        proposed = [r for r in rows if r["proposed"]]
        levels: set[int] = set()
        try:
            station_class = int(float(str(meta.get("class") or "")))
            if station_class > 0:
                levels.add(station_class)
        except ValueError:
            pass
        for row in active:
            levels.update(row["voltage_levels_kv"])
        buses.append({
            "code": code,
            "location": meta.get("location", ""),
            "class": meta.get("class", ""),
            "status": meta.get("status", ""),
            "owner": meta.get("owner", ""),
            "type": meta.get("type", ""),
            "bus_voltage_levels_kv": ";".join(map(str, sorted(levels, reverse=True))),
            "active_transformer_evidence_records": len(active),
            "labelled_active_records": sum(bool(r["equipment_label"]) for r in active),
            "unlabelled_active_tuple_records": sum(not bool(r["equipment_label"]) for r in active),
            "proposed_transformer_evidence_records": len(proposed),
            "exact_equipment_count_known": bool(active) and all(bool(r["equipment_label"]) for r in active),
        })

    qa = {
        "classification": "KSEBL_PUBLIC_SLD_TRANSFORMER_EVIDENCE_V0_1_QA",
        "source_records": len(records),
        "high_confidence_evidence_records": len(admitted),
        "stations_with_high_confidence_evidence": len({r["code"] for r in admitted if r["code"]}),
        "active_evidence_records": sum(not r["proposed"] for r in admitted),
        "proposed_evidence_records": sum(bool(r["proposed"]) for r in admitted),
        "labelled_evidence_records": sum(bool(r["equipment_label"]) for r in admitted),
        "unlabelled_tuple_records": sum(not bool(r["equipment_label"]) for r in admitted),
        "station_bus_inventory_records": len(buses),
        "review_queue_records": len(review),
        "rejection_reason_counts": dict(sorted(rejection_counts.items())),
        "automatic_ocr_used": False,
        "equipment_master_ready": False,
        "power_flow_ready": False,
        "interpretation": [
            "Each admitted row is a high-confidence text evidence tuple, not necessarily one unique physical transformer.",
            "Unlabelled duplicate tuples are de-duplicated conservatively and never used to infer transformer counts.",
            "Proposed equipment is retained but excluded from active bus evidence.",
            "Fault-level/short-circuit MVA values and component-times-bank expressions are rejected.",
            "KSEBL text-extraction forms such as 220KV/110KV/11KV, 11066 KV and 6611 KV are normalized only when they resolve unambiguously to known ordered system voltage levels.",
        ],
    }

    args.out.mkdir(parents=True, exist_ok=True)
    payload = {
        "classification": CLASSIFICATION,
        "prepared_date": "2026-09-27",
        "rules": {
            "max_voltage_rating_separation_chars": 50,
            "max_transformer_rating_separation_chars": 50,
            "rating_range_mva": [0.1, 700.0],
            "fault_level_rejected": True,
            "proposed_separated_from_active": True,
            "ocr_used": False,
            "compact_voltage_notation_normalized": True,
            "repeated_kv_voltage_notation_supported": True,
        },
        "transformer_evidence": admitted,
        "station_bus_inventory": buses,
    }
    (args.out / "transformer_evidence.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.out / "transformer_evidence_qa.json").write_text(
        json.dumps(qa, indent=2) + "\n", encoding="utf-8"
    )
    _write_csv(
        args.out / "transformer_evidence.csv",
        [{**r,
          "voltage_levels_kv": ";".join(map(str, r["voltage_levels_kv"])),
          "rating_values_mva": ";".join(f"{v:g}" for v in r["rating_values_mva"])} for r in admitted],
        ["evidence_id","code","location","class","status","owner","type","pdf_filename",
         "voltage_levels_kv","rating_values_mva","rating_expression","equipment_term",
         "equipment_label","identity_complete","proposed","admission_class","context"],
    )
    _write_csv(
        args.out / "station_bus_inventory.csv", buses,
        ["code","location","class","status","owner","type","bus_voltage_levels_kv",
         "active_transformer_evidence_records","labelled_active_records",
         "unlabelled_active_tuple_records","proposed_transformer_evidence_records",
         "exact_equipment_count_known"],
    )
    _write_csv(
        args.out / "transformer_review_queue.csv", review,
        ["code","location","class","status","pdf_filename","context_index","reason",
         "rating_expression","rating_values_mva","voltage_distance_chars",
         "transformer_distance_chars","context"],
    )
    print(json.dumps(qa, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
