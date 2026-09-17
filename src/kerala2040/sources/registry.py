"""Canonical v1 source registry and connectivity modes."""

from __future__ import annotations

SOURCES = {
    "kerala_sldc": {
        "authority": "Kerala State Load Despatch Centre",
        "mode": "public_html_form",
        "url": "https://sldckerala.com/index.php?id=1",
        "v1_role": "daily generation/import/consumption and station statistics",
    },
    "nasa_power": {
        "authority": "NASA POWER",
        "mode": "public_json_api",
        "url": "https://power.larc.nasa.gov/api/temporal/hourly/point",
        "v1_role": "hourly meteorology and solar-resource inputs",
    },
    "data_gov_in": {
        "authority": "Government of India Open Government Data Platform",
        "mode": "authenticated_json_api",
        "url": "https://api.data.gov.in/resource",
        "credential_env": "DATA_GOV_API_KEY",
        "v1_role": "resource-specific official datasets",
    },
    "niti_iced": {
        "authority": "NITI Aayog India Climate & Energy Dashboard",
        "mode": "discovery_download",
        "url": "https://www.iced.niti.gov.in/",
        "v1_role": "dataset discovery and cross-checking; not a primary API",
    },
}
