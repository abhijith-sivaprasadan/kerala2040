import pytest

from kerala2040.evidence import evidence_label, validate_evidence_record


def test_observed_evidence_requires_source():
    with pytest.raises(ValueError):
        validate_evidence_record({"classification": "measured"})


def test_synthetic_evidence_is_explicit():
    record = {"classification": "proxy_reconstruction", "claimed_as_measured": False}
    validate_evidence_record(record)
    assert "SYNTHETIC" in evidence_label("proxy_reconstruction")


def test_synthetic_cannot_claim_measured():
    with pytest.raises(ValueError):
        validate_evidence_record(
            {"classification": "scenario_assumption", "claimed_as_measured": True}
        )
