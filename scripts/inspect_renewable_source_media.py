r"""Inspect actual source TIFF pixels and render EVERY PDF page for visual review.

No OCR is performed. PDF pages are rendered whether or not selectable text
exists. Low-text pages are FLAGGED for closer reading, not presumed blank.
GeoTIFF previews are sampled, not a substitute for the separate full-raster QA.

Windows example (from kerala2040 repo, with source folders in Downloads):
  python -m pip install -e ".[dev,geo]"
  python -m pip install "pymupdf>=1.24,<2" "pillow>=10,<12"
  python scripts/inspect_renewable_source_media.py --source-root "$env:USERPROFILE\Downloads" --out-dir "E:\Kerala2040MediaQA"
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path

FOLDERS = (
    "global-pv-potential-study-raster-data-layers-globalsolaratlas",
    "India_GISdata_LTAym_YearlyMonthlyTotals_GlobalSolarAtlas-v2_GEOTIFF",
    "India_GISdata_LTAym_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF",
    "Wind",
    "Solar",
)
CHUNK = 4 * 1024 * 1024


def sha256(path: Path) -> str:
    d = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK), b""):
            d.update(block)
    return d.hexdigest()


def find_files(root: Path, suffixes: set[str]) -> list[Path]:
    found: list[Path] = []
    for folder in FOLDERS:
        base = root / folder
        if not base.is_dir() or base.is_symlink():
            raise FileNotFoundError(f"Missing or unsafe source folder: {base}")
        for p in base.rglob("*"):
            if p.is_symlink():
                raise ValueError(f"Source contains symlink: {p}")
            if p.is_file() and p.suffix.lower() in suffixes:
                found.append(p)
    return sorted(found, key=lambda p: p.relative_to(root).as_posix())


def tiff_record(path: Path, root: Path, out: Path) -> dict:
    """Read a representative native-resolution raster sample, not full statistics."""
    import numpy as np
    import rasterio
    from PIL import Image
    from rasterio.enums import Resampling

    relative = path.relative_to(root).as_posix()
    with rasterio.open(path) as src:
        h = min(src.height, 900)
        w = max(1, round(src.width * h / max(src.height, 1)))
        if w > 900:
            w, h = 900, max(1, round(src.height * 900 / src.width))
        sampled = src.read(
            1, out_shape=(h, w), masked=True,
            resampling=Resampling.nearest,
        ).astype("float64")
        values = sampled.filled(np.nan)
        good = ~np.ma.getmaskarray(sampled) & np.isfinite(values)
        positive = good & (values > 0)
        valid = values[good]
        stats = {
            "classification": "sampled_raster_preview_NOT_FULL_PIXEL_STATISTICS",
            "file": relative,
            "source_sha256": sha256(path),
            "source_bytes": path.stat().st_size,
            "crs": str(src.crs) if src.crs else None,
            "shape": [src.height, src.width],
            "bands": src.count,
            "dtype": list(src.dtypes),
            "native_res": list(src.res),
            "bounds": [src.bounds.left, src.bounds.bottom,
                       src.bounds.right, src.bounds.top],
            "nodata": str(src.nodata) if src.nodata is not None else None,
            "band1_unit": src.units[0] if src.units else None,
            "band1_description": src.descriptions[0] if src.descriptions else None,
            "tags": src.tags(),
            "band1_tags": src.tags(1),
            "sample_size": [h, w],
            "sampled_valid": int(good.sum()),
            "sampled_positive": int(positive.sum()),
            "sampled_zero": int((good & (values == 0)).sum()),
            "sampled_negative": int((good & (values < 0)).sum()),
            "sampled_min": float(valid.min()) if valid.size else None,
            "sampled_median": float(np.median(valid)) if valid.size else None,
            "sampled_max": float(valid.max()) if valid.size else None,
            "source_meta_qa": "CHECK_REQUIRED",
            "model_admitted": False,
        }
        if good.any():
            lo, hi = np.percentile(valid, (2, 98))
            if hi <= lo:
                hi = lo + 1
            grey = np.clip((values - lo) / (hi - lo) * 255, 0, 255)
            rgb = np.repeat(np.nan_to_num(grey, nan=0)[..., None], 3, axis=2)
            alpha = (good.astype("uint8") * 255)[..., None]
            image = Image.fromarray(
                np.concatenate([rgb.astype("uint8"), alpha], axis=2),
                "RGBA",
            )
            target = out / "tiff_previews" / (
                hashlib.sha256(relative.encode()).hexdigest()[:16] + ".png"
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            image.save(target)
            stats["local_preview"] = target.relative_to(out).as_posix()
        return stats


def _emit_sheet(images: list, names: list, target: Path) -> None:
    """A contact sheet contains labeled independent renders of all pages."""
    from PIL import Image, ImageDraw

    columns, cell_w, cell_h = 4, 400, 535
    rows = (len(images) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    for i, (image, label) in enumerate(zip(images, names, strict=True)):
        x = (i % columns) * cell_w
        y = (i // columns) * cell_h
        draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1),
                       outline="#777777", width=2)
        sheet.paste(image, (x + (cell_w - image.width) // 2, y + 5))
        draw.text((x + 8, y + cell_h - 19), label, fill="black")
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target, format="JPEG", quality=83, optimize=True)


def pdf_record(path: Path, root: Path, out: Path, dpi: int) -> dict:
    """Inspect all PDF pages using actual rendering, never OCR or text-only skips."""
    import fitz
    from PIL import Image

    relative = path.relative_to(root).as_posix()
    group = hashlib.sha256(relative.encode()).hexdigest()[:16]
    record = {
        "classification": "PDF_ALL_PAGES_RENDERED_FOR_HUMAN_VISUAL_REVIEW_NO_OCR",
        "file": relative,
        "source_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "page_count": 0,
        "page_details": [],
        "contact_sheets": [],
        "visual_interpretation_completed": False,
        "model_admitted": False,
    }
    pictures, labels = [], []
    with fitz.open(path) as doc:
        if doc.needs_pass:
            raise ValueError(f"Password protected PDF cannot be reviewed: {relative}")
        record["page_count"] = len(doc)
        record["metadata"] = {
            k: v for k, v in doc.metadata.items()
            if k in {"title", "author", "creationDate", "modDate"}
        }
        for index, page in enumerate(doc):
            words = len(page.get_text("words"))
            image_refs = len(page.get_images(full=True))
            # Vector graphics can be pages of charts with no raster image.
            drawing_count = len(page.get_drawings())
            warning = (
                "LOW_TEXT_VISUAL_REVIEW_REQUIRED" if words < 20 else
                "VISUAL_REVIEW_REQUIRED"
            )
            pixmap = page.get_pixmap(dpi=dpi, alpha=False)
            frame = Image.frombytes(
                "RGB", (pixmap.width, pixmap.height), pixmap.samples
            )
            frame.thumbnail((370, 500))
            pictures.append(frame.copy())
            labels.append(f"PDF p.{index + 1} · {words} words · {image_refs} images")
            record["page_details"].append({
                "page": index + 1, "native_word_count": words,
                "embedded_image_references": image_refs,
                "vector_drawings": drawing_count,
                "visual_review": warning,
                "ocr_performed": False,
            })
            if len(pictures) == 20 or index == len(doc) - 1:
                first = index + 2 - len(pictures)
                target = out / "pdf_contact_sheets" / group / (
                    f"pages_{first:04d}_{index + 1:04d}.jpg"
                )
                _emit_sheet(pictures, labels, target)
                record["contact_sheets"].append(
                    target.relative_to(out).as_posix()
                )
                pictures.clear()
                labels.clear()
            if (index + 1) % 50 == 0:
                print(f"RENDERED PDF {relative}: {index + 1}/{len(doc)}", flush=True)
    record["low_text_pages"] = [
        row["page"] for row in record["page_details"]
        if row["visual_review"] == "LOW_TEXT_VISUAL_REVIEW_REQUIRED"
    ]
    print(
        f"PDF {relative}: {record['page_count']} pages ALL rendered, "
        f"{len(record['low_text_pages'])} low-text pages", flush=True,
    )
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--pdf-only", action="store_true")
    parser.add_argument("--tiff-only", action="store_true")
    parser.add_argument("--dpi", type=int, default=72)
    args = parser.parse_args()
    if args.pdf_only and args.tiff_only:
        parser.error("Choose PDF-only or TIFF-only, not both")
    if not 40 <= args.dpi <= 150:
        parser.error("DPI must be 40..150")
    root, out = args.source_root.resolve(), args.out_dir.resolve()
    if out == root or out.is_relative_to(root):
        parser.error("Output must be OUTSIDE the original source tree")
    # Fail BEFORE rendering thousands of PDF pages if TIFF dependencies are absent.
    if not args.pdf_only:
        import importlib.util

        missing = [
            name for name in ("numpy", "rasterio", "PIL")
            if importlib.util.find_spec(name) is None
        ]
        if missing:
            parser.error(
                "TIFF inspection requires missing packages "
                + ", ".join(missing)
                + "; use Python 3.11/3.12 with "
                'python -m pip install -e ".[dev,geo]" '
                'and python -m pip install "pillow>=10,<12". '
                "Already rendered PDFs can be preserved with --tiff-only."
            )
    out.mkdir(parents=True, exist_ok=True)
    pdfs = [] if args.tiff_only else find_files(root, {".pdf"})
    tiffs = [] if args.pdf_only else find_files(root, {".tif", ".tiff"})
    result = {
        "classification": "PRIVATE_SOURCE_MEDIA_INSPECTION_NOT_MODEL_ADMITTED",
        "source_root": str(root),
        "pdf_pages_rendered_not_ocr": True,
        "automated_visual_interpretation_done": False,
        "geotiff_sampled_previews_not_full_raster_validation": True,
        "pdfs": [],
        "tiffs": [],
        "failures": [],
        "model_admitted": False,
    }
    # A partial rerun should not erase the 2,945 already-rendered PDF page
    # records or the TIFF inventory built on a previous pass.
    previous = out / "renewable_media_inventory.json"
    if (args.tiff_only or args.pdf_only) and previous.is_file():
        old = json.loads(previous.read_text(encoding="utf-8"))
        if old.get("source_root") != str(root):
            parser.error("Existing media inventory belongs to a different source root")
        if args.tiff_only:
            result["pdfs"] = old.get("pdfs", [])
            result["failures"] = [
                row for row in old.get("failures", [])
                if row.get("file", "").lower().endswith(".pdf")
            ]
        else:
            result["tiffs"] = old.get("tiffs", [])
            result["failures"] = [
                row for row in old.get("failures", [])
                if row.get("file", "").lower().endswith((".tif", ".tiff"))
            ]
    try:
        for file in tiffs:
            try:
                result["tiffs"].append(tiff_record(file, root, out))
            except Exception as error:  # noqa: BLE001 - isolate source-file failures
                result["failures"].append({
                    "file": file.relative_to(root).as_posix(),
                    "error": f"{type(error).__name__}: {error}",
                })
        for file in pdfs:
            try:
                result["pdfs"].append(pdf_record(file, root, out, args.dpi))
            except Exception as error:  # noqa: BLE001 - isolate source-file failures
                result["failures"].append({
                    "file": file.relative_to(root).as_posix(),
                    "error": f"{type(error).__name__}: {error}",
                })
    finally:
        target = out / "renewable_media_inventory.json"
        target.write_text(
            json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
            + "\n", encoding="utf-8",
        )
        rows = [
            "<!doctype html><meta charset='utf-8'>",
            "<title>Kerala2040 private source-media index</title>",
            "<h1>Kerala2040 local visual source review</h1>",
            (
                "<p>PDF pages are rendered without OCR; contact sheets are "
                "previews, not conclusions. TIFF statistics are sampled.</p>"
            ),
        ]
        for pdf in result["pdfs"]:
            rows.append(
                f"<h2>{html.escape(pdf['file'])}</h2>"
                f"<p>{pdf['page_count']} pages; low-text pages: "
                f"{html.escape(str(pdf['low_text_pages']))}</p>"
            )
            for sheet in pdf["contact_sheets"]:
                rows.append(
                    f"<p><a href='{html.escape(sheet)}'>"
                    f"{html.escape(sheet)}</a></p>"
                    f"<a href='{html.escape(sheet)}'>"
                    f"<img loading='lazy' width='640' "
                    f"src='{html.escape(sheet)}'></a>"
                )
        rows.append("<h2>TIFF previews</h2>")
        for raster in result["tiffs"]:
            rows.append(
                f"<h3>{html.escape(raster['file'])}</h3>"
                f"<p>{html.escape(str(raster['shape']))} / "
                f"{html.escape(str(raster['crs']))}</p>"
            )
            if raster.get("local_preview"):
                ref = raster["local_preview"]
                rows.append(
                    f"<img loading='lazy' width='480' src='{html.escape(ref)}'>"
                )
        (out / "index.html").write_text("\n".join(rows), encoding="utf-8")
    print(
        f"MEDIA QA: {len(result['tiffs'])} TIFFs "
        f"({len(tiffs)} inspected this run); "
        f"{len(result['pdfs'])} PDFs "
        f"({len(pdfs)} rendered this run), "
        f"{sum(p['page_count'] for p in result['pdfs'])} rendered pages; "
        f"{len(result['failures'])} errors; open {out / 'index.html'}",
        flush=True,
    )
    return 2 if result["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
