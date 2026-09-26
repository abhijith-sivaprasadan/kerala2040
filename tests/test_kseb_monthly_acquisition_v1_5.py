from pathlib import Path

import pytest
import requests

from kerala2040.kseb_monthly_acquisition_v1_5 import (
    KSEBMonthlyAcquisitionError,
    PACKAGES,
    acquire_bundle,
    content_disposition_filename,
    detect_excel_container,
    package_by_month,
)


class FakeResponse:
    def __init__(self, content: bytes, *, url: str, headers=None, status=200):
        self.content = content
        self.url = url
        self.headers = headers or {}
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))


class FakeSession:
    def __init__(self, payloads):
        self.payloads = payloads
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        package_id = int(url.rsplit("=", 1)[1])
        return self.payloads[package_id]


def test_inventory_is_full_fy2024_25():
    assert len(PACKAGES) == 12
    assert PACKAGES[0].month == "2024-04"
    assert PACKAGES[-1].month == "2025-03"
    assert len({p.package_id for p in PACKAGES}) == 12


def test_container_detection():
    assert detect_excel_container(b"PK\x03\x04" + b"x" * 100) == "xlsx"
    assert (
        detect_excel_container(bytes.fromhex("D0CF11E0A1B11AE1") + b"x" * 100)
        == "xls"
    )
    assert detect_excel_container(b"<html>blocked</html>") == "html"


def test_content_disposition_filename():
    assert (
        content_disposition_filename('attachment; filename="April 2024.xlsx"')
        == "April 2024.xlsx"
    )
    assert (
        content_disposition_filename(
            "attachment; filename*=UTF-8''March%202025.xlsx"
        )
        == "March%202025.xlsx"
    )


def test_subset_download(tmp_path: Path):
    package = package_by_month("2024-04")
    payload = b"PK\x03\x04" + b"x" * 20_000
    session = FakeSession(
        {
            package.package_id: FakeResponse(
                payload,
                url=package.url,
                headers={
                    "Content-Disposition": 'attachment; filename="April 2024.xlsx"',
                    "Content-Type": "application/octet-stream",
                },
            )
        }
    )
    result = acquire_bundle(
        tmp_path,
        months=["2024-04"],
        session=session,
    )
    assert result["complete_fy2024_25"] is False
    assert result["downloaded_months"] == ["2024-04"]
    assert (tmp_path / "2024-04.xlsx").read_bytes() == payload


def test_wrong_container_fails_closed(tmp_path: Path):
    package = package_by_month("2024-04")
    session = FakeSession(
        {
            package.package_id: FakeResponse(
                bytes.fromhex("D0CF11E0A1B11AE1") + b"x" * 20_000,
                url=package.url,
            )
        }
    )
    with pytest.raises(KSEBMonthlyAcquisitionError, match="expected xlsx"):
        acquire_bundle(tmp_path, months=["2024-04"], session=session)
