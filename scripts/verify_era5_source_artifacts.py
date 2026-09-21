"""Verify raw CDS artifact ZIPs without admitting ERA5 to the energy model.

Download each GitHub Actions source artifact ZIP, then:
    pip install 'numpy>=2,<3' 'h5py>=3.12,<5'
    python scripts/verify_era5_source_artifacts.py *.zip --require-full-year \
        --output results/acquisition/era5/source_qa.json

One CDS response can contain *two* NetCDF files (instant and accum). The
source request and component file counts are not interchangeable. This audit
checks bytes, UTC timestamps, all five variables/units and true grid geometry;
it never computes statewide resource availability or generation.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import h5py
import numpy as np

UNITS = {"t2m": "K", "u10": "m s**-1", "v10": "m s**-1",
         "ssrd": "J m**-2", "tp": "m"}
POINTS = {"thiruvananthapuram", "kochi", "palakkad", "kozhikode", "kannur"}
PERIODS = {"2024-04_to_2024-06", "2024-07_to_2024-09",
           "2024-10_to_2024-12", "2025-01_to_2025-03"}


def hourly_window(year: int, months: list[str]) -> np.ndarray:
    nums = [int(m) for m in months]
    if not nums or nums != list(range(nums[0], nums[-1] + 1)):
        raise ValueError("Duplicate, unordered or noncontiguous source months")
    start = datetime(year, nums[0], 1, tzinfo=UTC)
    end = (datetime(year + 1, 1, 1, tzinfo=UTC)
           if nums[-1] == 12 else
           datetime(year, nums[-1] + 1, 1, tzinfo=UTC))
    return np.arange(int(start.timestamp()), int(end.timestamp()), 3600, dtype=np.int64)


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def inspect_artifact(path: Path) -> dict:
    """Inspect either a downloaded GitHub artifact ZIP or its extracted directory."""
    if path.is_dir():
        def read_artifact(name: str) -> bytes:
            return (path / name).read_bytes()

        artifact_name = path.name
        close = None
    else:
        archive = zipfile.ZipFile(path)
        read_artifact = archive.read
        artifact_name = path.name
        close = archive.close

    try:
        report = json.loads(read_artifact("retrieval_attempt.json"))
        points, periods = report["selection"]["points"], report["selection"]["periods"]
        if (len(points) != 1 or len(periods) != 1 or points[0] not in POINTS
                or periods[0] not in PERIODS):
            raise ValueError(f"Unexpected point/quarter: {path}")
        point, quarter = points[0], periods[0]
        if (report["windows_completed"] != 1 or report["source_windows_succeeded"] != 1
                or report["files_attempted"] != 1 or report["failures"]):
            raise ValueError(f"Source acquisition incomplete: {point} {quarter}")
        first, last = int(quarter[5:7]), int(quarter[-2:])
        expected = hourly_window(int(quarter[:4]), [f"{m:02d}" for m in range(first, last + 1)])
        seen = defaultdict(set)
        grids = set()
        archives = {}
        proofs = []
        for entry in report["files"]:
            if entry["point"] != point or entry["selected_quarter"] != quarter:
                raise ValueError("Crossed source provenance")
            data = read_artifact("source_files/" + Path(entry["path"]).name)
            if sha256(data) != entry["sha256"] or len(data) != entry["bytes"]:
                raise ValueError("NetCDF member hash/size mismatch")
            if entry.get("source_archive_member"):
                key = "source_files/" + Path(entry["source_archive_path"]).name
                original = read_artifact(key)
                if (sha256(original) != entry["source_archive_sha256"]
                        or len(original) != entry["source_archive_bytes"]):
                    raise ValueError("Original CDS ZIP hash/size mismatch")
                with zipfile.ZipFile(io.BytesIO(original)) as source:
                    if source.read(entry["source_archive_member"]) != data:
                        raise ValueError("Original ZIP and extracted bytes differ")
                archives[key] = sha256(original)
            with h5py.File(io.BytesIO(data)) as nc:
                timestamps = nc["valid_time"][:].astype(np.int64)
                window = hourly_window(int(quarter[:4]), entry["months"])
                if not np.array_equal(timestamps, window):
                    raise ValueError(f"Missing/duplicate UTC hours: {point} {entry['period']}")
                units = nc["valid_time"].attrs.get("units", b"")
                if units != b"seconds since 1970-01-01":
                    raise ValueError("Unrecognised UTC epoch units")
                lats, lons = nc["latitude"][:], nc["longitude"][:]
                if (not 1 <= len(lats) <= 3 or not 1 <= len(lons) <= 3
                        or np.min(abs(lats - entry["latitude"])) > .15
                        or np.min(abs(lons - entry["longitude"])) > .15
                        or np.max(abs(lats - entry["latitude"])) > .35
                        or np.max(abs(lons - entry["longitude"])) > .35):
                    raise ValueError("Unexpected ERA5 grid geometry")
                grids.add((tuple(map(float, lats)), tuple(map(float, lons))))
                fields = set(nc) & set(UNITS)
                if not fields:
                    raise ValueError("Source member has no requested variables")
                for variable in fields:
                    values = nc[variable][:]
                    if (values.shape != (len(window), len(lats), len(lons))
                            or not np.isfinite(values).all()
                            or nc[variable].attrs["units"].decode() != UNITS[variable]):
                        raise ValueError(f"Bad variable, dimensions or unit: {variable}")
                    hours = set(map(int, timestamps))
                    if seen[variable].intersection(hours):
                        raise ValueError(f"Overlapping {variable} source hours")
                    seen[variable].update(hours)
            proofs.append({"period": entry["period"],
                           "component_sha256": entry["sha256"],
                           "original_zip_member": entry.get("source_archive_member")})
        if len(grids) != 1:
            raise ValueError(f"Conflicting grid geometry: {point} {quarter}")
        expected_hours = set(map(int, expected))
        if any(seen[key] != expected_hours for key in UNITS):
            raise ValueError(f"Missing quarter-hour/variable coverage: {point} {quarter}")
        lat, lon = next(iter(grids))
        return {"point": point, "quarter": quarter, "hours": len(expected),
                "grid": {"latitude": list(lat), "longitude": list(lon)},
                "original_zip_sha256": archives, "components": proofs,
                "source_artifact": artifact_name}
    finally:
        if close:
            close()


def verify(paths: list[Path], require_full_year: bool = False) -> dict:
    rows = [inspect_artifact(path) for path in paths]
    slots = {(row["point"], row["quarter"]) for row in rows}
    if len(slots) != len(rows):
        raise ValueError("Duplicate location-quarter artifacts")
    if require_full_year:
        all_slots = {(point, quarter) for point in POINTS for quarter in PERIODS}
        if slots != all_slots:
            raise ValueError(f"Missing full-year source artifacts: {sorted(all_slots - slots)}")
        for point in POINTS:
            items = [row for row in rows if row["point"] == point]
            if sum(row["hours"] for row in items) != 8760:
                raise ValueError(f"FY2024-25 UTC hours incomplete at {point}")
            if len({json.dumps(row["grid"], sort_keys=True) for row in items}) != 1:
                raise ValueError(f"Grid changed between quarters at {point}")
    return {"classification": "verified_reanalysis_source_not_model_ready",
            "full_year_source_qc_passed": require_full_year,
            "location_quarters_verified": len(rows),
            "point_hours_verified": sum(row["hours"] for row in rows),
            "records": sorted(rows, key=lambda row: (row["point"], row["quarter"])),
            "scope_warning": "Not measured PV/wind output, statewide renewable capacity or admitted model data."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", type=Path, nargs="+")
    parser.add_argument("--require-full-year", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.artifacts, require_full_year=args.require_full_year)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in
                      ("classification", "full_year_source_qc_passed",
                       "location_quarters_verified", "point_hours_verified")}, indent=2))


if __name__ == "__main__":
    main()
