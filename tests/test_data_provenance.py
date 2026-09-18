import pytest

from kerala2040.data_provenance import provenance_record


def test_observed_requires_named_source():
    with pytest.raises(ValueError):
        provenance_record(
            classification="observed",
            source=None,
            source_type="primary_official",
        )


def test_proxy_requires_explicit_warning():
    with pytest.raises(ValueError):
        provenance_record(
            classification="proxy",
            source="Kerala SLDC daily energy + CEA aggregate constraints",
            source_type="reconstruction",
            note="hourly series",
        )


def test_proxy_with_warning_is_valid():
    record = provenance_record(
        classification="proxy",
        source="Kerala SLDC daily energy + CEA aggregate constraints",
        source_type="reconstruction",
        note="Proxy reconstruction; not measured hourly telemetry.",
    )
    assert record["classification"] == "proxy"
