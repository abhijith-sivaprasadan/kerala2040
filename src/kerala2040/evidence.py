"""Evidence classification helpers enforcing provenance-first modelling."""

from __future__ import annotations

from typing import Any

OBSERVED_CLASSES = {
    "measured",
    "official_observed_reference",
    "derived_from_measured",
    "reanalysis",
    "remote_sensing_or_reanalysis",
}
NONOBSERVED_CLASSES = {
    "modelled_resource_profile",
    "proxy_reconstruction",
    "scenario_assumption",
    "published_external_scenario",
    "illustrative",
    "unresolved",
}
ALLOWED_CLASSES = OBSERVED_CLASSES | NONOBSERVED_CLASSES


def validate_evidence_record(record: dict[str, Any]) -> None:
    """Validate a compact evidence record.

    Organic/observed/reanalysis evidence must identify its source. Synthetic/modelled
    evidence must be explicitly non-observed.
    """
    classification = record.get("classification")
    if classification not in ALLOWED_CLASSES:
        raise ValueError(f"unsupported or missing evidence classification: {classification!r}")

    if classification in OBSERVED_CLASSES:
        source = record.get("source")
        if not source:
            raise ValueError(f"{classification} evidence requires a source")

    if classification in NONOBSERVED_CLASSES and record.get("claimed_as_measured") is True:
        raise ValueError(f"{classification} evidence cannot be claimed as measured")


def evidence_label(classification: str) -> str:
    """Return a human-facing label that cannot hide synthetic/modelled status."""
    labels = {
        "measured": "Measured",
        "official_observed_reference": "Official observed reference",
        "derived_from_measured": "Derived from measured data",
        "reanalysis": "Reanalysis",
        "remote_sensing_or_reanalysis": "Remote-sensing/reanalysis input",
        "modelled_resource_profile": "MODELLED RESOURCE PROFILE — NOT MEASURED GENERATION",
        "proxy_reconstruction": "SYNTHETIC PROXY — NOT MEASURED",
        "scenario_assumption": "SCENARIO ASSUMPTION — NOT OBSERVED",
        "published_external_scenario": "External published scenario — not this model's result",
        "illustrative": "Illustrative only",
        "unresolved": "Unresolved / missing",
    }
    if classification not in labels:
        raise ValueError(f"unsupported evidence classification: {classification!r}")
    return labels[classification]
