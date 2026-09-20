"""Fail-closed NRSC LULC native-raster admission audit; not a siting model.

The registry is a source catalogue. WMS images, missing native rasters and
synthetic test fixtures are never accepted as a Kerala ecological capacity ceiling.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import yaml

REGISTRY = "configs/lulc_native_acquisition_2024_25.yaml"
ACQUIRED = "validated_source_file_metadata_only_NOT_ecological_eligibility"
MISSING = "native_raster_not_acquired"
KERALA_ENVELOPE_WGS84 = (74.5, 8.0, 78.0, 12.9)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_legend(path: Path) -> set[int]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not {"code", "label"} <= set(reader.fieldnames or []):
            raise ValueError("LULC legend needs exact code,label columns")
        records = list(reader)
    if not records or any(not row["label"].strip() for row in records):
        raise ValueError("LULC class legend missing labels")
    codes = [int(row["code"]) for row in records]
    if len(set(codes)) != len(codes):
        raise ValueError("LULC class legend has duplicate codes")
    return set(codes)


def _inspect_native_raster(root: Path, entry: dict[str, Any]) -> dict[str, Any]:
    """Only run rasterio once a real TIFF and its metadata/legend are present."""
    relative = entry["native_raster_path"]
    if not relative:
        return {"id": entry["id"], "status": MISSING, "reason": "No native raster path"}
    path = root / relative
    legend_relative = entry["class_legend_path"]
    if not path.is_file():
        return {
            "id": entry["id"], "status": MISSING,
            "expected_path": relative, "reason": "No verified original bytes in repository",
        }
    if path.suffix.lower() not in {".tif", ".tiff"}:
        raise ValueError("Expected native classified GeoTIFF, not a styled WMS image")
    for field in (
        "native_sha256", "class_legend_sha256", "original_crs",
        "nodata", "redistribution_permission",
    ):
        if entry.get(field) is None:
            raise ValueError(f"Native LULC raster missing source metadata: {field}")
    if not legend_relative or not (root / legend_relative).is_file():
        raise ValueError("LULC source class legend is not present")
    if sha256(path) != entry["native_sha256"]:
        raise ValueError("LULC raster original-source SHA256 mismatch")
    legend = root / legend_relative
    if sha256(legend) != entry["class_legend_sha256"]:
        raise ValueError("LULC legend SHA256 mismatch")
    valid_codes = _read_legend(legend)
    import numpy as np
    import rasterio
    from rasterio.warp import transform_bounds

    used: set[int] = set()
    with rasterio.open(path) as image:
        if image.driver != "GTiff" or image.count != 1:
            raise ValueError("LULC original must be a single-band categorical GeoTIFF")
        if not image.crs or image.crs.to_string() != entry["original_crs"]:
            raise ValueError("Missing/mismatched original CRS")
        if image.nodata != entry["nodata"]:
            raise ValueError("Unmatched source nodata value")
        if image.colorinterp[0].name in {"red", "green", "blue"}:
            raise ValueError("Styled RGB maps are not categorical source data")
        if image.dtypes[0] not in {"uint8", "uint16", "uint32", "int8", "int16", "int32"}:
            raise ValueError("LULC categorical codes must be integers")
        if not all(math.isfinite(n) and n > 0 for n in image.res):
            raise ValueError("Missing or unusable raster resolution")
        bbox = transform_bounds(image.crs, "EPSG:4326", *image.bounds)
        west, south, east, north = bbox
        kw, ks, ke, kn = KERALA_ENVELOPE_WGS84
        if east <= kw or west >= ke or north <= ks or south >= kn:
            raise ValueError("LULC raster does not overlap Kerala approximate envelope")
        for _, window in image.block_windows(1):
            block = image.read(1, window=window, masked=True)
            if block.count() == 0:
                continue
            used.update(int(x) for x in np.unique(block.compressed()))
        if not used or not used <= valid_codes:
            raise ValueError("LULC raster codes absent or not covered by source legend")
        return {
            "id": entry["id"], "status": ACQUIRED,
            "raw_sha256": sha256(path),
            "legend_sha256": sha256(legend),
            "source_vintage": entry["reported_vintage"],
            "source_scale_denominator": entry["reported_scale_denominator"],
            "original_crs": image.crs.to_string(),
            "resolution_in_crs_units": [float(n) for n in image.res],
            "width": image.width, "height": image.height,
            "bounds_wgs84": [float(n) for n in bbox],
            "class_codes_found": sorted(used),
            "nodata": image.nodata,
            "redistribution_permission": entry["redistribution_permission"],
            "statewide_coverage_verified": False,
            "legal_eligibility_verified": False,
            "capacity_ceiling_verified": False,
            "note": (
                "Provenance, legend and envelope validated for local file only. "
                "This does not establish statewide coverage, spatial precision, "
                "legal exclusion geometry or buildable renewable capacity."
            ),
        }


def audit_lulc(root: Path) -> dict[str, Any]:
    registry = yaml.safe_load((root / REGISTRY).read_text(encoding="utf-8"))
    if registry.get("classification") != (
        "official_lulc_discovery_no_native_kerala_raster_acquired"
    ):
        raise ValueError("LULC catalogue cannot assert acquired model data")
    sources = registry["sources"]
    products = registry["products"]
    if len({p["id"] for p in products}) != len(products):
        raise ValueError("Duplicate NRSC LULC product identifiers")
    for name, source in sources.items():
        if not source.get("url", "").startswith("https://"):
            raise ValueError(f"LULC official discovery source URL missing: {name}")
    if any(
        product["source_ids"] == []
        or not set(product["source_ids"]) <= set(sources)
        or not product["reported_vintage"]
        for product in products
    ):
        raise ValueError("LULC product missing source link or vintage")
    if sum(p["preferred_reference"] is True for p in products) != 1:
        raise ValueError("Exactly one LULC priority product required")
    use = registry["model_use"]
    if any(use[k] is not False for k in (
        "native_kerala_lulc_acquired",
        "native_kerala_lulc_validated",
        "authorised_redistribution",
        "ecological_exclusion_ready",
    )) or use["land_available_area_sq_km"] is not None or (
        use["generation_capacity_ceiling_mw"] is not None
    ):
        raise ValueError("LULC acquisition catalogue cannot self-certify model eligibility")
    records = [_inspect_native_raster(root, entry) for entry in products]
    return {
        "classification": "source_discovery_and_local_native_raster_qa_NOT_eligibility",
        "source_registry": REGISTRY,
        "records": records,
        "products_catalogued": len(products),
        "native_rasters_with_local_source_qa": sum(
            row["status"] == ACQUIRED for row in records
        ),
        "statewide_native_lulc_verified": False,
        "ecological_exclusion_ready": False,
        "siting_eligible_area_sq_km": None,
        "capacity_ceiling_mw": None,
        "audit_gate_closed": False,
        "interpretation": (
            "A catalogue, WMS map, or even a single local native raster and legend "
            "cannot independently validate Kerala statewide legal/technical siting."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("results/gis/lulc_source_audit.json"))
    args = parser.parse_args()
    report = audit_lulc(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n",
                           encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
