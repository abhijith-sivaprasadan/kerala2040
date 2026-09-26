"""Download the twelve official KSEB FY2024-25 monthly reservoir files.

The URLs and expected formats come from a preserved raw HTML snapshot of the
official KSEB Download Manager listing. Every response is validated by magic
bytes before it is saved. HTML error pages, redirects to unrelated content,
and format mismatches are rejected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import requests

from kerala2040.kseb_monthly_bundle_v1_5 import EXPECTED_FORMATS, detect_format

PACKAGES = {
    "2024-04": ("water-level-of-main-reservoirs-of-kseb-limited-during-april-2024", 4421),
    "2024-05": ("water-level-of-main-reservoirs-of-kseb-limited-during-may-2024", 4488),
    "2024-06": ("water-level-of-main-reservoirs-of-kseb-limited-during-june-2024", 4570),
    "2024-07": ("water-level-of-main-reservoirs-of-kseb-limited-during-july-2024", 4668),
    "2024-08": ("water-level-of-main-reservoirs-of-kseb-limited-during-august-2024", 4742),
    "2024-09": ("water-level-of-main-reservoirs-of-kseb-limited-during-september-2024", 4806),
    "2024-10": ("water-level-of-main-reservoirs-of-kseb-limited-during-october-2024", 4874),
    "2024-11": ("water-level-of-main-reservoirs-of-kseb-limited-during-november-2024", 4940),
    "2024-12": ("water-level-of-main-reservoirs-of-kseb-limited-during-december-2024", 5012),
    "2025-01": ("water-level-of-main-reservoirs-of-kseb-ltd-during-january-2025", 5081),
    "2025-02": ("water-level-of-main-reservoir-of-kseb-limited-during-february-2025", 5143),
    "2025-03": ("water-level-of-main-reservoirs-of-kseb-limited-during-march-2025", 5212),
}

BASE = "https://dams.kseb.in/"
UA = "kerala2040-research/1.5 (official KSEB monthly reservoir acquisition)"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=45.0)
    parser.add_argument("--manifest-out", type=Path)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    records = []
    failures = []

    for month, (slug, package_id) in PACKAGES.items():
        expected = EXPECTED_FORMATS[month]
        url = f"{BASE}?wpdmpro={slug}&wpdmdl={package_id}"
        suffix = f".{expected}"
        target = args.out_dir / f"{month}{suffix}"
        temp = args.out_dir / f".{month}.part"

        try:
            response = session.get(url, timeout=args.timeout, stream=True)
            response.raise_for_status()
            with temp.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)

            detected = detect_format(temp)
            if detected != expected:
                prefix = temp.read_bytes()[:160]
                raise ValueError(
                    f"{month}: expected {expected}, received {detected}; "
                    f"first bytes={prefix!r}"
                )

            temp.replace(target)
            records.append(
                {
                    "month": month,
                    "path": target.name,
                    "wpdmdl": package_id,
                    "source_url": url,
                    "detected_format": detected,
                    "size_bytes": target.stat().st_size,
                    "sha256": sha256(target),
                }
            )
        except Exception as exc:  # noqa: BLE001 - acquisition must record all failures
            temp.unlink(missing_ok=True)
            failures.append(
                {
                    "month": month,
                    "wpdmdl": package_id,
                    "source_url": url,
                    "error": str(exc),
                }
            )

    manifest = {
        "classification": "KSEB_OFFICIAL_MONTHLY_DOWNLOAD_ATTEMPT_V1_5",
        "records": records,
        "failures": failures,
        "record_count": len(records),
        "failure_count": len(failures),
        "complete": len(records) == 12 and not failures,
        "files": [
            {"month": record["month"], "path": record["path"]}
            for record in records
        ],
    }

    manifest_path = args.manifest_out or (args.out_dir / "manifest.json")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
