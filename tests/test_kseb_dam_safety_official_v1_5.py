import pytest

from kerala2040.kseb_dam_safety_official_v1_5 import (
    KSEBSourceError,
    discover_dated_post_links,
    parse_kseb_reservoir_page,
)

OFFICIAL = "https://dams.kseb.in/?p=5178"


def page(headers: list[str], row: list[str], title: str = "18.03.2025") -> str:
    h = "".join(f"<th>{value}</th>" for value in headers)
    numbering = "".join(f"<td>{i}</td>" for i in range(1, len(headers) + 1))
    values = "".join(f"<td>{value}</td>" for value in row)
    return (
        "<html><body>"
        f'<h1 class="entry-title">{title}</h1>'
        f"<table><tr>{h}</tr><tr>{numbering}</tr><tr>{values}</tr></table>"
        "</body></html>"
    )


def current_headers() -> list[str]:
    return [
        "Sl. No.",
        "Name of Dam / Reservoir",
        "District",
        "MWL (metre)",
        "FRL (metre)",
        "Spillway Crest Level (metre)",
        "Live Storage at FRL (MCM)",
        "Rule level (metre)",
        "Blue level (metre)",
        "Orange level (metre)",
        "Red Level (metre)",
        "Today's Water level (metre)",
        "Today's Live Storage (MCM)",
        "% Storage w.r.t Live Storage at FRL",
        "Same day previous year Water level (metre)",
        "Same day previous year Live Storage (MCM)",
        "Inflow (cumecs)",
        "Power House Discharge(cumecs)",
        "Spillway release (cumecs)",
        "Total Outflow (cumecs)",
        "Rain fall (mm)",
        "Remarks",
    ]


def current_idukki_row() -> list[str]:
    return [
        "1",
        "IDUKKI",
        "IDK",
        "2408.5 ft",
        "2403 ft",
        "2373 ft",
        "1459.49",
        "2403.00 ft",
        "2395.00",
        "2401.00",
        "2402.00",
        "2356.90",
        "754.094",
        "51.67%",
        "2351.80",
        "691.446",
        "17.94",
        "32.17",
        "0.00",
        "32.17",
        "8.80",
        "",
    ]


def test_current_2025_schema_is_header_driven():
    result = parse_kseb_reservoir_page(
        page(current_headers(), current_idukki_row()),
        source_url=OFFICIAL,
    )
    assert result["date"] == "2025-03-18"
    assert result["schema"]["column_count"] == 22
    assert result["metrics"]["live_storage_mcm"] == pytest.approx(754.094)
    assert result["metrics"]["inflow_cumecs"] == pytest.approx(17.94)
    assert result["metrics"]["power_house_discharge_cumecs"] == pytest.approx(32.17)
    assert result["metrics"]["spillway_release_cumecs"] == pytest.approx(0.0)
    assert result["metrics"]["water_level_ft"] == pytest.approx(2356.90)
    assert result["units"]["water_level_ft"] == "ft"
    assert result["unit_overrides"]


def test_legacy_schema_preserves_volume_and_rate_inflow_separately():
    headers = [
        "Sl. No.",
        "Name of Dam / Reservoir",
        "District",
        "Today's Water level (metre)",
        "Today's Live Storage (MCM)",
        "% Storage w.r.t Live Storage at FRL",
        "Inflow (MCM)",
        "Average Inflow (Cumecs)",
        "Power House Discharge (MCM)",
        "Spillway release (MCM)",
        "Total Outflow (MCM)",
        "Rain fall (mm)",
        "Remarks",
    ]
    row = [
        "1",
        "IDUKKI",
        "IDK",
        "2200.00",
        "800.00",
        "54.80%",
        "4.25",
        "49.19",
        "3.10",
        "0.20",
        "3.30",
        "12.0",
        "",
    ]
    result = parse_kseb_reservoir_page(
        page(headers, row, title="01.07.2024"),
        source_url="https://dams.kseb.in/?p=4000",
    )
    assert result["metrics"]["inflow_mcm"] == pytest.approx(4.25)
    assert result["metrics"]["average_inflow_cumecs"] == pytest.approx(49.19)
    assert result["metrics"]["power_house_discharge_mcm"] == pytest.approx(3.10)
    assert result["metrics"]["spillway_release_mcm"] == pytest.approx(0.20)


def test_shifted_percentage_in_flow_column_fails_closed():
    headers = [
        "Sl. No.",
        "Name of Dam / Reservoir",
        "District",
        "Today's Water level (metre)",
        "Today's Live Storage (MCM)",
        "% Storage w.r.t Live Storage at FRL",
        "Inflow (MCM)",
        "Power House Discharge (MCM)",
        "Spillway release (MCM)",
    ]
    row = [
        "1",
        "IDUKKI",
        "IDK",
        "2200.00",
        "800.00",
        "54.80%",
        "44.85%",
        "3.10",
        "0.20",
    ]
    with pytest.raises(KSEBSourceError, match="percentage"):
        parse_kseb_reservoir_page(
            page(headers, row, title="15.10.2024"),
            source_url="https://dams.kseb.in/?p=4100",
        )


def test_non_official_host_rejected():
    with pytest.raises(KSEBSourceError, match="official KSEB"):
        parse_kseb_reservoir_page(
            page(current_headers(), current_idukki_row()),
            source_url="https://example.com/?p=5178",
        )


def test_archive_link_discovery():
    html = """
    <html><body>
      <a href="?p=5176">17.03.2025</a>
      <a href="https://dams.kseb.in/?p=5178">18.03.2025</a>
      <a href="https://example.com/19.03.2025">19.03.2025</a>
    </body></html>
    """
    links = discover_dated_post_links(
        html,
        base_url="https://dams.kseb.in/?page_id=45",
    )
    assert [item["date"] for item in links] == ["2025-03-17", "2025-03-18"]
    assert links[0]["url"] == "https://dams.kseb.in/?p=5176"
