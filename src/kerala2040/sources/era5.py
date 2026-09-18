"""Pure ERA5 request specification for Kerala representative-point weather inputs."""

from __future__ import annotations

from typing import Any

DATASET = "reanalysis-era5-single-levels"
VARIABLES = [
    "2m_temperature",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "surface_solar_radiation_downwards",
    "total_precipitation",
]
POINTS = {
    "thiruvananthapuram": (8.5241, 76.9366),
    "kochi": (9.9312, 76.2673),
    "palakkad": (10.7867, 76.6548),
    "kozhikode": (11.2588, 75.7804),
    "kannur": (11.8745, 75.3704),
}
# Three-month chunks stay below the CDS request-cost threshold encountered for
# the original nine-month Apr-Dec request.
PERIODS = [
    ("2024-04_to_2024-06", "2024", [f"{m:02d}" for m in range(4, 7)]),
    ("2024-07_to_2024-09", "2024", [f"{m:02d}" for m in range(7, 10)]),
    ("2024-10_to_2024-12", "2024", [f"{m:02d}" for m in range(10, 13)]),
    ("2025-01_to_2025-03", "2025", [f"{m:02d}" for m in range(1, 4)]),
]
DAYS = [f"{d:02d}" for d in range(1, 32)]
HOURS = [f"{h:02d}:00" for h in range(24)]


def request_for(lat: float, lon: float, year: str, months: list[str]) -> dict[str, Any]:
    """Build a small-box ERA5 request around one representative Kerala point."""
    pad = 0.13
    return {
        "product_type": ["reanalysis"],
        "variable": VARIABLES,
        "year": [year],
        "month": months,
        "day": DAYS,
        "time": HOURS,
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": [lat + pad, lon - pad, lat - pad, lon + pad],
    }
