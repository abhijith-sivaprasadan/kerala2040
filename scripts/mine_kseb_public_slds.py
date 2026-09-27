"""Mine public KSEBL single-line diagrams into an auditable equipment index.

The input PDFs are public links exposed by KSEBL's Grid Map v3.2. Extraction is
text-first: no OCR is performed automatically. PDFs with little/no extractable
text are explicitly flagged for later visual review rather than guessed.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from pypdf.errors import PdfReadError

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACQ = ROOT / "results/acquisition/network_public_v0_1"
DEFAULT_OUT = ROOT / "results/network/public_sld_mining_v0_1"

CLASSIFICATION = "KSEBL_PUBLIC_SLD_TEXT_MINING_V0_1_NOT_EQUIPMENT_MASTER"

VOLTAGE_RE = re.compile(r"(?<!\d)(11|22|33|66|110|220|230|320|400)\s*k\s*v", re.IGNORECASE)
MVA_RE = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*M\s*V\s*A\b", re.IGNORECASE)
MW_RE = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*M\s*W\b", re.IGNORECASE)
MVAR_RE = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*M\s*V\s*A\s*R\b", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"SLD\s+Not\s+Available", re.IGNORECASE)
AS_ON_RE = re.compile(
    r"\bAs\s+On\s*[:\-]?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})",
    re.IGNORECASE,
)
CONDUCTOR_AMPACITY_RE = re.compile(
    r"CONDUCTOR\s*[-:]?\s*([A-Z][A-Z0-9_-]{1,24})[^\n]{0,50}?"
    r"(?<![/\d])(\d{2,4})\s*A\b",
    re.IGNORECASE,
)
EQUIPMENT_WORDS = re.compile(
    r"\b(?:ICT|PTR|TRANSFORMER|TR\.?|AUTO\s*TRANSFORMER|BUS\s*COUPLER|"
    r"BUS\s*SECTION|MAIN\s*BUS|TRANSFER\s*BUS|REACTOR|CAPACITOR)\b",
    re.IGNORECASE,
)


def _norm_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _context(text: str, start: int, end: int, radius: int = 90) -> str:
    return _norm_space(text[max(0, start - radius): min(len(text), end + radius)])


def _numeric_hits(regex: re.Pattern[str], text: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    seen: set[tuple[float, str]] = set()
    for match in regex.finditer(text):
        value = float(match.group(1))
        snippet = _context(text, match.start(), match.end())
        key = (value, snippet)
        if key in seen:
            continue
        seen.add(key)
        hits.append({"value": value, "context": snippet})
    return hits


def _voltage_hits(text: str) -> list[int]:
    return sorted({int(match.group(1)) for match in VOLTAGE_RE.finditer(text)})


def _equipment_contexts(text: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for match in EQUIPMENT_WORDS.finditer(text):
        snippet = _context(text, match.start(), match.end(), radius=120)
        if snippet not in seen:
            seen.add(snippet)
            out.append(snippet)
    return out[:80]


def _extract_pdf(path: Path) -> dict[str, Any]:
    reader = PdfReader(str(path))
    page_text: list[str] = []
    page_errors: list[dict[str, Any]] = []
    for index, page in enumerate(reader.pages):
        try:
            page_text.append(page.extract_text() or "")
        except (PdfReadError, KeyError, TypeError, ValueError) as exc:  # source PDF quality is an evidence property
            page_text.append("")
            page_errors.append({"page": index + 1, "error": type(exc).__name__})

    text = "\n".join(page_text)
    compact = _norm_space(text)
    mva = _numeric_hits(MVA_RE, text)
    mw = _numeric_hits(MW_RE, text)
    mvar = _numeric_hits(MVAR_RE, text)
    equipment_contexts = _equipment_contexts(text)

    placeholder = bool(PLACEHOLDER_RE.search(text))
    as_on_dates = sorted({match.group(1) for match in AS_ON_RE.finditer(text)})
    conductor_ampacity_candidates = []
    for match in CONDUCTOR_AMPACITY_RE.finditer(text):
        conductor_ampacity_candidates.append(
            {
                "conductor": match.group(1).upper(),
                "ampere": int(match.group(2)),
                "context": _context(text, match.start(), match.end(), radius=100),
            }
        )

    transformer_mva_values = sorted(
        {
            hit["value"]
            for hit in mva
            if re.search(
                r"\b(?:ICT|PTR|TRANSFORMER|TR\.?|AUTO\s*TRANSFORMER)\b",
                hit["context"],
                re.IGNORECASE,
            )
        }
    )

    return {
        "pages": len(reader.pages),
        "text_chars": len(compact),
        "extractable_text": len(compact) >= 50 and not placeholder,
        "document_status": (
            "PLACEHOLDER_NOT_AVAILABLE"
            if placeholder
            else ("TEXT_EXTRACTABLE" if len(compact) >= 50 else "NO_EXTRACTABLE_TEXT")
        ),
        "as_on_dates": as_on_dates,
        "page_extraction_errors": page_errors,
        "voltages_kv": _voltage_hits(text),
        "mva_hits": mva,
        "mw_hits": mw,
        "mvar_hits": mvar,
        "transformer_mva_values": transformer_mva_values,
        "conductor_ampacity_candidates": conductor_ampacity_candidates,
        "equipment_contexts": equipment_contexts,
        "busbar_keywords": sorted(
            {
                match.group(0).upper()
                for match in re.finditer(
                    r"\b(?:MAIN\s*BUS|TRANSFER\s*BUS|BUS\s*COUPLER|BUS\s*SECTION)\b",
                    text,
                    re.IGNORECASE,
                )
            }
        ),
        "text_preview": compact[:2000],
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "location",
        "code",
        "class",
        "status",
        "owner",
        "type",
        "url",
        "pdf_present",
        "pages",
        "text_chars",
        "extractable_text",
        "document_status",
        "as_on_dates",
        "voltages_kv",
        "transformer_mva_values",
        "mva_hit_count",
        "equipment_context_count",
        "needs_visual_review",
        "error",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--acquisition", type=Path, default=DEFAULT_ACQ)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    inventory_path = args.acquisition / "public_sld_inventory.json"
    sld_dir = args.acquisition / "sld"
    if not inventory_path.is_file():
        raise SystemExit(f"missing SLD inventory: {inventory_path}")
    if not sld_dir.is_dir():
        raise SystemExit(
            f"missing SLD PDF directory: {sld_dir}; rerun acquisition with --download-sld"
        )

    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    full: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    valid_inventory = 0

    for row in inventory:
        url = str(row.get("url") or "")
        filename = Path(url.split("?", 1)[0]).name
        if not filename or filename == ".pdf":
            continue
        valid_inventory += 1
        pdf = sld_dir / filename
        result: dict[str, Any]
        error = ""
        if not pdf.is_file():
            result = {
                "pages": 0,
                "text_chars": 0,
                "extractable_text": False,
                "document_status": "PDF_NOT_AVAILABLE",
                "as_on_dates": [],
                "page_extraction_errors": [],
                "voltages_kv": [],
                "mva_hits": [],
                "mw_hits": [],
                "mvar_hits": [],
                "transformer_mva_values": [],
                "conductor_ampacity_candidates": [],
                "equipment_contexts": [],
                "busbar_keywords": [],
                "text_preview": "",
            }
            error = "PDF_NOT_DOWNLOADED"
        else:
            try:
                result = _extract_pdf(pdf)
            except (OSError, PdfReadError, KeyError, TypeError, ValueError) as exc:
                result = {
                    "pages": 0,
                    "text_chars": 0,
                    "extractable_text": False,
                    "page_extraction_errors": [],
                    "voltages_kv": [],
                    "mva_hits": [],
                    "mw_hits": [],
                    "mvar_hits": [],
                    "transformer_mva_values": [],
                    "equipment_contexts": [],
                    "busbar_keywords": [],
                    "text_preview": "",
                }
                error = f"{type(exc).__name__}: {exc}"

        record = dict(row)
        record["pdf_filename"] = filename
        record["pdf_present"] = pdf.is_file()
        record["mining"] = result
        record["error"] = error
        record["needs_visual_review"] = not result["extractable_text"]
        full.append(record)

        summary_rows.append(
            {
                "location": row.get("location", ""),
                "code": row.get("code", ""),
                "class": row.get("class", ""),
                "status": row.get("status", ""),
                "owner": row.get("owner", ""),
                "type": row.get("type", ""),
                "url": url,
                "pdf_present": pdf.is_file(),
                "pages": result["pages"],
                "text_chars": result["text_chars"],
                "extractable_text": result["extractable_text"],
                "document_status": result["document_status"],
                "as_on_dates": ";".join(result["as_on_dates"]),
                "voltages_kv": ";".join(map(str, result["voltages_kv"])),
                "transformer_mva_values": ";".join(
                    f"{value:g}" for value in result["transformer_mva_values"]
                ),
                "mva_hit_count": len(result["mva_hits"]),
                "equipment_context_count": len(result["equipment_contexts"]),
                "needs_visual_review": not result["extractable_text"],
                "error": error,
            }
        )

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "sld_equipment_mining.json").write_text(
        json.dumps(
            {
                "classification": CLASSIFICATION,
                "prepared_date": "2026-09-27",
                "records": full,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_csv(args.out / "sld_equipment_summary.csv", summary_rows)

    parseable = sum(bool(row["extractable_text"]) for row in summary_rows)
    present = sum(bool(row["pdf_present"]) for row in summary_rows)
    transformer_rows = sum(bool(row["transformer_mva_values"]) for row in summary_rows)
    placeholder_rows = sum(
        row.get("document_status") == "PLACEHOLDER_NOT_AVAILABLE"
        for row in summary_rows
    )
    dated_rows = sum(bool(row.get("as_on_dates")) for row in summary_rows)
    qa = {
        "classification": "KSEBL_PUBLIC_SLD_TEXT_MINING_V0_1_QA",
        "inventory_records_valid": valid_inventory,
        "pdfs_present": present,
        "pdfs_missing_or_failed": valid_inventory - present,
        "pdfs_with_extractable_text": parseable,
        "pdfs_needing_visual_review": valid_inventory - parseable,
        "pdfs_with_transformer_mva_candidates": transformer_rows,
        "placeholder_sld_not_available_pdfs": placeholder_rows,
        "pdfs_with_explicit_as_on_date": dated_rows,
        "automatic_ocr_used": False,
        "equipment_master_ready": False,
        "interpretation": [
            "Text extraction is a discovery aid, not final transformer admission.",
            "MVA values are preserved with local text context to avoid confusing transformer ratings with other equipment.",
            "PDFs without extractable text are flagged for later visual inspection; no OCR guessing is performed.",
        ],
    }
    (args.out / "sld_mining_qa.json").write_text(
        json.dumps(qa, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(qa, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
