"""Audit GSA India native PVOUT rasters: annual vs daily and all 12 months.

This is an internal-consistency QA of published long-term source layers;
NOT Kerala-only spatial eligibility, FY2024-25 measurements, or model admission.

Example (Windows PowerShell, from the kerala2040 repo):
  python scripts/qa_gsa_pvout_full_raster.py --source-root "$env:USERPROFILE\Downloads" --out "E:\GSA-qa\gsa_pvout_full_raster_qa.json"

Requires the project geo extra: python -m pip install -e ".[dev,geo]"
"""
from __future__ import annotations

import argparse
import hashlib
import json
from contextlib import ExitStack
from pathlib import Path

FOLDERS = {
    "period_totals": "India_GISdata_LTAym_YearlyMonthlyTotals_GlobalSolarAtlas-v2_GEOTIFF",
    "average_daily": "India_GISdata_LTAym_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF",
}
MONTH_DAYS = (31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
ANNUAL_DAYS = 365.25
WINDOW = 512


def source_sha256(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def find_layers(source_root: Path) -> dict[str, Path]:
    """Use exact source-folder names and reject absent/ambiguous TIFF names."""
    result: dict[str, Path] = {}
    for kind, folder in FOLDERS.items():
        parent = source_root / folder
        if not parent.is_dir():
            raise FileNotFoundError(f"Missing source folder: {parent}")
        for month in (0, *range(1, 13)):
            name = "PVOUT.tif" if month == 0 else f"PVOUT_{month:02d}.tif"
            matches = sorted(p for p in parent.rglob(name) if p.is_file())
            if len(matches) != 1:
                raise ValueError(
                    f"Expected exactly one {name} in {parent}; "
                    f"found {len(matches)}: {matches[:4]}"
                )
            label = "annual" if month == 0 else f"month_{month:02d}"
            result[f"{kind}_{label}"] = matches[0]
    return result


def start_metric(expected_days: float | None = None) -> dict:
    return {
        "expected_days": expected_days,
        "matched_positive_cells": 0,
        "source_valid_mask_mismatches": 0,
        "cells_exceeding_0_2pct_tolerance": 0,
        "max_absolute_relative_error_pct": 0.0,
        "mean_absolute_relative_error_pct": None,
        "_sum_absolute_relative_error_pct": 0.0,
    }


def compare_arrays(metric: dict, actual, expected, valid_a, valid_b) -> None:
    """Update a streaming accumulator; no full-India raster stack in RAM."""
    import numpy as np

    mismatch = valid_a ^ valid_b
    metric["source_valid_mask_mismatches"] += int(mismatch.sum())
    both = valid_a & valid_b
    metric["matched_positive_cells"] += int(both.sum())
    if not both.any():
        return
    # Relative error against the actual period-total units.
    rel = np.abs(actual[both] - expected[both]) / np.maximum(
        np.abs(actual[both]), 1e-12
    ) * 100.0
    metric["max_absolute_relative_error_pct"] = max(
        metric["max_absolute_relative_error_pct"], float(rel.max())
    )
    metric["_sum_absolute_relative_error_pct"] += float(rel.sum())
    metric["cells_exceeding_0_2pct_tolerance"] += int((rel > 0.2).sum())


def audit(source_root: Path, output: Path, tolerance_pct: float = 0.2) -> dict:
    import numpy as np
    import rasterio
    from rasterio.windows import Window

    if tolerance_pct <= 0:
        raise ValueError("Tolerance must be positive")
    layers = find_layers(source_root.resolve())
    source_info = {}
    for label, file in layers.items():
        source_info[label] = {
            "relative_to_source_root": file.relative_to(source_root.resolve()).as_posix(),
            "bytes": file.stat().st_size,
            "sha256": source_sha256(file),
        }
    metrics = {
        "annual_over_mean_day": start_metric(ANNUAL_DAYS),
        "annual_vs_sum_of_12_months": start_metric(None),
        "monthly_total_over_mean_day": {
            f"{month:02d}": start_metric(MONTH_DAYS[month - 1])
            for month in range(1, 13)
        },
    }
    with ExitStack() as stack:
        opened = {
            k: stack.enter_context(rasterio.open(v)) for k, v in layers.items()
        }
        annual = opened["period_totals_annual"]
        for label, src in opened.items():
            if (
                src.crs is None
                or src.crs.to_epsg() != 4326
                or src.width != annual.width
                or src.height != annual.height
                or not src.transform.almost_equals(annual.transform)
            ):
                raise ValueError(
                    f"Native GSA grids differ or are not EPSG:4326: {label}. "
                    "Do not silently resample for a source unit audit."
                )
            source_info[label]["crs"] = str(src.crs)
            source_info[label]["grid_shape"] = [src.height, src.width]
            source_info[label]["transform"] = tuple(src.transform)
            source_info[label]["nodata"] = src.nodata
        annual_positive = 0
        windows = 0
        for row in range(0, annual.height, WINDOW):
            for col in range(0, annual.width, WINDOW):
                windows += 1
                region = Window(
                    col, row,
                    min(WINDOW, annual.width - col),
                    min(WINDOW, annual.height - row),
                )

                def read(label: str):
                    data = opened[label].read(1, window=region, masked=True)
                    values = np.ma.filled(data, np.nan).astype("float64")
                    good = ~np.ma.getmaskarray(data) & np.isfinite(values) & (values > 0)
                    return values, good

                year, year_good = read("period_totals_annual")
                day, day_good = read("average_daily_annual")
                annual_positive += int(year_good.sum())
                compare_arrays(
                    metrics["annual_over_mean_day"],
                    year, day * ANNUAL_DAYS, year_good, day_good,
                )
                month_sum = np.zeros_like(year)
                all_month_good = np.ones_like(year_good, dtype=bool)
                for month in range(1, 13):
                    key = f"{month:02d}"
                    total, total_good = read(f"period_totals_month_{key}")
                    mean_day, mean_good = read(f"average_daily_month_{key}")
                    compare_arrays(
                        metrics["monthly_total_over_mean_day"][key],
                        total, mean_day * MONTH_DAYS[month - 1],
                        total_good, mean_good,
                    )
                    all_month_good &= total_good
                    month_sum += np.where(total_good, total, 0)
                compare_arrays(
                    metrics["annual_vs_sum_of_12_months"],
                    year, month_sum, year_good, all_month_good,
                )
    failed = []
    for name, metric in [
        ("annual_over_mean_day", metrics["annual_over_mean_day"]),
        ("annual_vs_sum_of_12_months", metrics["annual_vs_sum_of_12_months"]),
        *(
            (f"monthly_total_over_mean_day/{key}", item)
            for key, item in metrics["monthly_total_over_mean_day"].items()
        ),
    ]:
        n = metric["matched_positive_cells"]
        if n:
            metric["mean_absolute_relative_error_pct"] = (
                metric.pop("_sum_absolute_relative_error_pct") / n
            )
        else:
            metric.pop("_sum_absolute_relative_error_pct")
        metric["cells_exceeding_tolerance"] = (
            metric.pop("cells_exceeding_0_2pct_tolerance")
            if tolerance_pct == 0.2
            else None
        )
        if (
            n == 0
            or metric["source_valid_mask_mismatches"]
            or metric["max_absolute_relative_error_pct"] > tolerance_pct
        ):
            failed.append(name)
    report = {
        "classification": "LONG_TERM_GSA_INDIA_NATIVE_RASTER_INTERNAL_UNIT_QA_NOT_MODEL_ADMITTED",
        "source": "Global Solar Atlas India 2.0 / Solargis / World Bank Group / ESMAP",
        "coverage": "India raster matched source cells; NOT exact Kerala clip",
        "source_vintage": "1999-2018 long-term; not FY2024-25 production",
        "source_folders": FOLDERS,
        "months_days": list(MONTH_DAYS),
        "annual_days": ANNUAL_DAYS,
        "unit_tolerance_pct": tolerance_pct,
        "native_cell_windows_checked": windows,
        "annual_valid_positive_cells": annual_positive,
        "source_tiffs": source_info,
        "checks": metrics,
        "passed": not failed,
        "failed_checks": failed,
        "model_admitted": False,
        "feasible_capacity_MW": None,
        "warnings": [
            "GSA annual/day ratio is a 365.25-day long-term climatological normalisation",
            "February monthly/day ratio is 28.25, not February 2025's 28 days",
            "Matching GSA alternative formats is not independent real-world validation",
            "A passing result is not Kerala spatial suitability or verified buildable capacity",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--tolerance-pct", type=float, default=0.2)
    args = parser.parse_args()
    result = audit(args.source_root, args.out, args.tolerance_pct)
    print(
        f"GSA full-raster unit QA: {'PASS' if result['passed'] else 'FAIL'}; "
        f"{result['annual_valid_positive_cells']} valid positive annual cells; "
        f"{result['native_cell_windows_checked']} native raster windows"
    )
    if result["failed_checks"]:
        print("Failed source checks:", ", ".join(result["failed_checks"]))
    print(f"Source QA written to {args.out}")
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
