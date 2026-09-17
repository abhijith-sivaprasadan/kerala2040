"""External source adapters for Kerala 2040."""

from .nasa_power import fetch_hourly_point
from .ogd import OGDClient
from .sldc import fetch_system_statistics, parse_system_statistics

__all__ = [
    "OGDClient",
    "fetch_hourly_point",
    "fetch_system_statistics",
    "parse_system_statistics",
]
