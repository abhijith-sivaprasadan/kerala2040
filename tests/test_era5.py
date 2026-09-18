from pathlib import Path
import runpy

_module = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts" / "ingest_era5_points.py"))
PERIODS = _module["PERIODS"]
POINTS = _module["POINTS"]
request_for = _module["request_for"]


def test_era5_periods_cover_fy2024_25_in_three_month_chunks() -> None:
    assert [label for label, _, _ in PERIODS] == [
        "2024-04_to_2024-06",
        "2024-07_to_2024-09",
        "2024-10_to_2024-12",
        "2025-01_to_2025-03",
    ]
    months = [(year, month) for _, year, period_months in PERIODS for month in period_months]
    assert months == [
        *[("2024", f"{month:02d}") for month in range(4, 13)],
        *[("2025", f"{month:02d}") for month in range(1, 4)],
    ]
    assert all(len(months_) <= 3 for _, _, months_ in PERIODS)
    assert len(POINTS) * len(PERIODS) == 20


def test_era5_request_is_hourly_and_small_box() -> None:
    request = request_for(9.9312, 76.2673, "2024", ["04", "05", "06"])
    assert request["year"] == ["2024"]
    assert request["month"] == ["04", "05", "06"]
    assert len(request["time"]) == 24
    north, west, south, east = request["area"]
    assert north > south
    assert east > west
