"""Strict provenance helpers for Kerala 2040 model data."""

from __future__ import annotations

from typing import Any

ALLOWED_CLASSIFICATIONS = {
    "observed",
    "official_reference",
    "reanalysis",
    "derived",
    "proxy",
    "synthetic",
    "scenario_assumption",
    "external_study_result",
    "catalogue_only",
}

SOURCE_TYPES_REQUIRING_SOURCE = {
    "observed",
    "official_reference",
    "reanalysis",
    "external_study_result",
    "catalogue_only",
}


def provenance_record(
    *,
    classification: str,
    source: str | None,
    source_type: str,
    note: str | None = None,
) -> dict[str, Any]:
    """Create and validate a compact provenance record."""
    record = {
        "classification": classification,
        "source": source,
        "source_type": source_type,
    }
    if note:
        record["note"] = note
    validate_provenance_record(record)
    return record


def validate_provenance_record(record: dict[str, Any]) -> None:
    """Reject unlabelled or misleading provenance metadata."""
    classification = record.get("classification")
    if classification not in ALLOWED_CLASSIFICATIONS:
        raise ValueError(
            "classification must be one of "
            f"{sorted(ALLOWED_CLASSIFICATIONS)}; got {classification!r}"
        )

    source_type = str(record.get("source_type") or "").strip()
    if not source_type:
        raise ValueError("source_type is required")

    source = record.get("source")
    if classification in SOURCE_TYPES_REQUIRING_SOURCE and not str(source or "").strip():
        raise ValueError(
            f"source is required for classification={classification!r}"
        )

    if classification in {"proxy", "synthetic", "scenario_assumption"}:
        note = str(record.get("note") or "").lower()
        if classification not in note and "not measured" not in note:
            raise ValueError(
                f"{classification} records must explicitly say they are "
                f"{classification} or not measured in the note"
            )
