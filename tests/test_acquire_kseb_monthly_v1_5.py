import json
from pathlib import Path

from kerala2040.kseb_monthly_bundle_v1_5 import EXPECTED_FORMATS
from scripts.acquire_kseb_monthly_fy2024_25_v1_5 import acquire


def test_acquisition_accepts_complete_preexisting_bundle(tmp_path: Path):
    out_dir = tmp_path / "bundle"
    out_dir.mkdir()
    months = []
    sizes = {}
    for month, fmt in EXPECTED_FORMATS.items():
        path = out_dir / f"{month}.{fmt}"
        if fmt == "xlsx":
            payload = b"PK\x03\x04fake-xlsx"
        else:
            payload = bytes.fromhex("D0CF11E0A1B11AE1") + b"fake-xls"
        path.write_bytes(payload)
        sizes[month] = len(payload)
        months.append(
            {
                "month": month,
                "format": fmt,
                "wpdmdl": 1,
                "listed_size_kb": max(len(payload) / 1024.0, 0.01),
                "derived_short_download_url": "https://dams.kseb.in/?wpdmdl=1",
                "official_package_url": "https://dams.kseb.in/?wpdmdl=1",
            }
        )

    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"required_months": months}), encoding="utf-8")

    result = acquire(inventory, out_dir, attempts=1)
    assert result["failed"] == 0
    assert result["downloaded_or_present"] == 12
    assert result["ready_for_content_schema_audit"] is True
