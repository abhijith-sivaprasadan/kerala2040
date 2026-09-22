"""Validate and package one self-contained dashboard, without live API credentials."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import shutil
import subprocess
from datetime import datetime, timedelta
from html.parser import HTMLParser
from itertools import pairwise
from pathlib import Path
from urllib.parse import unquote, urlsplit

from kerala2040.audit_readiness import build_audit
from kerala2040.research_ledger import build_ledger


def validate_bundle(public: Path) -> dict:
    def read(name: str):
        path = (public / name).resolve()
        if path.parent != public.resolve() or path.suffix != ".json":
            raise ValueError(f"Invalid bundle filename: {name}")
        return json.loads(path.read_text(encoding="utf-8"))

    site = read("site-data.json")
    metadata = site["metadata"]
    files = metadata["files"]
    for name in files.values():
        read(name)
    if read("metadata.json") != metadata:
        raise ValueError("Manifest and metadata disagree")
    if "hourly_load_proxy_summary" in files:
        proxy = read(files["hourly_load_proxy_summary"])
        if proxy != site.get("hourly_load_proxy"):
            raise ValueError("Proxy summary and manifest disagree")
        if proxy.get("classification") != "proxy_reconstruction_not_measured_telemetry":
            raise ValueError("Hourly proxy must be explicitly classified as reconstruction")
        if "hourly_load_proxy" in files:
            product = read(files["hourly_load_proxy"])
            hourly = product["records"]
            if product.get("classification") != proxy["classification"]:
                raise ValueError("Hourly series classification disagrees with summary")
            times = [datetime.fromisoformat(row["timestamp"]) for row in hourly]
            if len(hourly) != proxy["hours"] or len(hourly) != 8760:
                raise ValueError("Hourly proxy must contain the complete FY2024-25 chronology")
            if times[0].isoformat() != "2024-04-01T00:00:00+05:30" or any(
                right - left != timedelta(hours=1) for left, right in pairwise(times)
            ):
                raise ValueError("Hourly proxy timestamps must be consecutive IST intervals")
            if any(not math.isfinite(row["load_mw"]) or row["load_mw"] <= 0 for row in hourly):
                raise ValueError("Hourly proxy contains invalid load values")
            if abs(sum(row["load_mw"] for row in hourly) / 1000 - proxy["annual_energy_mu"]) > 1e-6:
                raise ValueError("Hourly series energy disagrees with proxy summary")
    if "audit_readiness" in files:
        audit = read(files["audit_readiness"])
        if audit.get("classification") != "repository_evidence_audit_not_external_source_validation":
            raise ValueError("Audit evidence classification is missing or incorrect")
        if audit.get("finding_count") != len(audit.get("findings", [])):
            raise ValueError("Audit finding counts do not match the source report")
        if audit.get("open_findings", 0) + audit.get("closed_findings", 0) != audit["finding_count"]:
            raise ValueError("Audit open and closed totals disagree")
        if "sldc_station_evidence" in files:
            station = read(files["sldc_station_evidence"])
            if audit.get("source_qa_sha256") != station.get("source_archive_sha256"):
                raise ValueError("Audit and station evidence identify different SLDC archives")
        for gate in audit.get("release_gates", {}).values():
            if gate.get("passed") and gate.get("blocking_checks"):
                raise ValueError("An audit release gate is both passed and blocked")
    if "research_ledger" in files:
        ledger = read(files["research_ledger"])
        if ledger != site.get("research_ledger"):
            raise ValueError("Research ledger and site manifest disagree")
        if ledger.get("classification") != (
            "dated_repository_research_progress_NOT_geospatial_or_model_readiness"
        ):
            raise ValueError("Research ledger must retain provenance classification")
        if (ledger.get("ecological_capacity_ceiling_ready") is not False
                or ledger.get("eligible_area_sq_km") is not None
                or ledger.get("potential_mw") is not None
                or ledger["release_gates"]["ecological_capacity_ceiling"]["passed"]
                or ledger["release_gates"]["techno_economic_2040"]["passed"]):
            raise ValueError("Research ledger cannot promote GIS or 2040 model readiness")
        if "audit_readiness" in files:
            audit = read(files["audit_readiness"])
            if (ledger["audit_finding_count"] != audit["finding_count"]
                    or ledger["audit_open_findings"] != audit["open_findings"]):
                raise ValueError("Research ledger and audited finding counts disagree")
        wind = ledger.get("wind_terrain")
        if (not wind
                or wind.get("classification") != "NIWE_150M_KERALA_DESCRIPTIVE_RESOURCE_TERRAIN_NOT_CAPACITY"
                or wind.get("point_centres") != 200_692
                or wind.get("slope", {}).get("finite_point_centres") != 199_853
                or wind.get("slope", {}).get("missing_point_centres") != 839
                or sum(wind.get("speed_m_s", {}).get("bin_counts", [])) != 200_692
                or wind.get("candidate_area_km2") is not None
                or wind.get("feasible_capacity_MW") is not None
                or wind.get("model_admitted") is not False):
            raise ValueError("Executed wind evidence is absent, inconsistent or promoted to capacity")
        lris = ledger.get("lris")
        if (not lris or lris.get("classification") !=
                "LRIS_PUBLIC_PORTAL_DISCOVERY_NOT_STATUTORY_GIS_OR_SITE_ELIGIBILITY"
                or lris.get("native_land_use_geometry_acquired") is not False
                or lris.get("legal_exclusion_verified") is not False
                or lris.get("model_admitted") is not False):
            raise ValueError("LRIS portal evidence was incorrectly promoted to legal GIS")
    if "research_results" in files:
        research = read(files["research_results"])
        if research != site.get("research_results"):
            raise ValueError("Research products and manifest disagree")
        products = research["products"]
        if products.get("renewables", {}).get("classification") not in (None, "modelled_resource_profile"):
            raise ValueError("Renewables must retain modelled-resource classification")
        if products.get("gis", {}).get("model_ready"):
            raise ValueError("Raw GIS acquisition is not model-ready")
    if metadata["status"]["sldc_daily"]["available"]:
        rows = read(files["daily_balance"])["records"]
        dates = [row["date"] for row in rows]
        if not rows or len(dates) != len(set(dates)) or dates != sorted(dates):
            raise ValueError("Daily evidence must contain unique, sorted dates")
        baseline = site.get("baseline")
        if baseline:
            if baseline["rows"] != len(rows):
                raise ValueError("Baseline and daily series come from different snapshots")
            total = sum(row["consumption_mu"] for row in rows) / 1000
            if abs(total - baseline["consumption_twh"]) > 0.000001:
                raise ValueError("Baseline energy does not match daily evidence")
    return site


def live_manifest(source: dict) -> dict:
    """Keep development-only synthetic/model outputs in GitHub, never in Pages."""
    site = copy.deepcopy(source)
    metadata = site["metadata"]
    for key in ("hourly_load_proxy", "hourly_load_proxy_summary"):
        metadata["files"].pop(key, None)
        metadata.get("status", {}).pop(key, None)
        metadata.get("layer_provenance", {}).pop(key, None)
    site.pop("hourly_load_proxy", None)
    site["stress_tests"] = {}
    site["screening_nodes"] = []
    if site.get("baseline"):
        site["baseline"].pop("hourly_load_proxy_available", None)
    research = site.get("research_results", {})
    for key in ("renewables", "replay", "scenario_dimensions", "techno_economics"):
        research.get("products", {}).pop(key, None)
        research.get("artifact_provenance", {}).pop(key, None)
    research["limitations"] = [
        "Development-only synthetic series and model outputs are retained in GitHub, not this website.",
        "Published external scenarios remain labelled benchmarks, not Kerala 2040 results.",
        "Raw GIS acquisition is not a model-ready exclusion map or capacity ceiling.",
    ]
    metadata["publication_policy"] = "observed_and_derived_evidence_plus_labelled_published_external_benchmarks"
    return site


def source_revision(root: Path) -> str | None:
    """Attest the exact checked-out research commit, not the stale data-build SHA.

    A gitless copy can build, but its website explicitly says that the source
    revision is not recorded. Never use GITHUB_SHA: deploy runs in another repo.
    """
    try:
        top = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            check=True, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
        if Path(top).resolve() != root:
            return None
        sha = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
            check=True, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
        return sha if re.fullmatch(r"[a-f0-9]{40}", sha) else None
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return None



class _StaticReferenceCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str, str]] = []
        self.ids: list[str] = []
        self.routes: list[str] = []
        self.views: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        if values.get("data-route"):
            self.routes.append(values["data-route"])
        if values.get("data-view"):
            self.views.append(values["data-view"])
        for attr in ("href", "src"):
            if values.get(attr):
                self.refs.append((tag, attr, values[attr]))


def validate_static_site(output: Path) -> None:
    """Reject a packaged site with broken same-origin assets or route wiring."""
    html = (output / "index.html").read_text(encoding="utf-8")
    parser = _StaticReferenceCollector()
    parser.feed(html)

    if len(parser.ids) != len(set(parser.ids)):
        raise ValueError("Packaged site contains duplicate HTML ids")
    if not set(parser.routes) <= set(parser.views):
        raise ValueError("A data-route points at a missing view")

    root = output.resolve()
    broken = []
    for tag, attr, raw in parser.refs:
        parts = urlsplit(raw)
        if parts.scheme in {"http", "https", "mailto", "data", "blob"}:
            continue
        if raw.startswith(("#", "//")):
            continue
        local = unquote(parts.path)
        if not local:
            continue
        candidate = (output / local).resolve()
        if root not in candidate.parents and candidate != root:
            broken.append((tag, attr, raw, "escapes site root"))
        elif not candidate.exists():
            broken.append((tag, attr, raw, "missing"))
    if broken:
        raise ValueError(f"Packaged site has broken local references: {broken}")

    manifest = json.loads((output / "manifest.webmanifest").read_text(encoding="utf-8"))
    for icon in manifest.get("icons", []):
        src = icon.get("src", "")
        if not src or not (output / src).is_file():
            raise ValueError(f"Packaged manifest icon is missing: {src}")



def build_site(root: Path, output: Path) -> None:
    root, output = root.resolve(), output.resolve()
    if output == root or output == root / "docs" or output == root / "public":
        raise ValueError("Build into a separate directory, not a source directory")
    source = validate_bundle(root / "public")
    output.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "manifest.webmanifest", "robots.txt"):
        shutil.copy2(root / "docs" / name, output / name)
    assets = output / "assets"
    assets.mkdir(exist_ok=True)
    # No old chart-framework, Leaflet or unused CSS is shipped with the redesign.
    for stale in assets.iterdir():
        if stale.is_file():
            stale.unlink()
    shutil.copy2(root / "docs/assets/mark.svg", assets / "mark.svg")
    # Curated vector chapter artwork, not legacy chart libraries or GIS files.
    artwork = ("icons.svg", "chapter-electric.svg", "chapter-land.svg",
               "chapter-pathways.svg", "chapter-industry.svg")
    for name in artwork:
        shutil.copy2(root / "docs/assets" / name, assets / name)
    # Social providers require a real PNG, not an SVG thumbnail or a browser
    # screenshot. Rasterise the authored local vector artwork deterministically.
    # The PNG and iOS touch icon are generated as build outputs, not source
    # evidence or external-network downloads.
    import cairosvg

    share = assets / "kerala2040-share.png"
    cairosvg.svg2png(
        bytestring=(root / "docs/assets/social-card.svg").read_bytes(),
        write_to=str(share), output_width=1200, output_height=630,
    )
    cairosvg.svg2png(
        bytestring=(root / "docs/assets/mark.svg").read_bytes(),
        write_to=str(assets / "kerala2040-touch.png"),
        output_width=180, output_height=180,
    )
    if share.read_bytes()[:8] != bytes.fromhex("89504e470d0a1a0a"):
        raise ValueError("The social thumbnail did not render as a PNG")
    # Immutable filenames prevent a new HTML page from running an old cached app.
    html = (output / "index.html").read_text(encoding="utf-8")
    for name in ("app.js", "kerala.css"):
        asset = root / "docs/assets" / name
        digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
        versioned = f"{asset.stem}.{digest}{asset.suffix}"
        shutil.copy2(asset, output / "assets" / versioned)
        html = html.replace(f"assets/{name}", f"assets/{versioned}")
    (output / "index.html").write_text(html, encoding="utf-8")
    site = live_manifest(source)
    # Observation data may predate research QA: publish both clocks separately.
    site["metadata"]["research_source_commit"] = source_revision(root)
    # The expanded station-level report is an optional, user-acquired public evidence
    # layer; future config-only bundle rebuilds cannot silently remove its provenance.
    station_path = root / "public" / "sldc-station-evidence.json"
    if station_path.exists():
        station = json.loads(station_path.read_text(encoding="utf-8"))
        if (station.get("classification") != "derived_from_measured"
                or station.get("observed_days") != 354
                or station.get("expected_days") != 365
                or len(station.get("missing_dates", [])) != 11
                or len(station.get("monthly", [])) != 12
                or len(station.get("source_archive_sha256", "")) != 64):
            raise ValueError("Expanded SLDC evidence has missing provenance/coverage")
        site["metadata"]["files"]["sldc_station_evidence"] = "sldc-station-evidence.json"
        site["sldc_station_evidence"] = station
    data_dir = output / "data"
    data_dir.mkdir(exist_ok=True)
    allowed = set(site["metadata"]["files"].values()) | {"site-data.json", "metadata.json"}
    # Remove stale files from a previous build, including direct proxy download URLs.
    for path in data_dir.iterdir():
        if path.is_file() and path.name not in allowed:
            path.unlink()
    for name in allowed:
        shutil.copy2(root / "public" / name, data_dir / name)
    products = {"site-data.json": site, "metadata.json": site["metadata"],
                "baseline-summary.json": site.get("baseline"),
                "research-results.json": site.get("research_results"),
                "screening-nodes.json": {"classification": "unresolved", "records": [], "note": "Verified site geometries not yet published; illustrative markers remain in GitHub."}}
    for name, payload in products.items():
        if payload is not None:
            (data_dir / name).write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    if station_path.exists():
        # Full CSV archive is separately downloadable; original raw HTML archive
        # remains outside Pages and is identified by SHA-256 in the QA report.
        published = root / "public" / "sldc-processed-evidence.zip"
        if not published.exists():
            raise ValueError("Expanded SLDC source summaries must have the processed CSV download")
        shutil.copy2(published, data_dir / published.name)
    # The audit is computed from committed QA, costs and GIS inventories, not from
    # unverified live APIs or the development-only hourly screening output.
    audit = build_audit(root)
    if station_path.exists() and audit["source_qa_sha256"] != station["source_archive_sha256"]:
        raise ValueError("Audit and published station evidence identify different source archives")
    if site["metadata"]["files"].get("audit_readiness"):
        raise ValueError("Audit readiness must be generated by the build, not a stale bundle")
    site["metadata"]["files"]["audit_readiness"] = "audit-readiness.json"
    (data_dir / "audit-readiness.json").write_text(
        json.dumps(audit, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    # Build a public progress ledger from the same committed QA as release gates.
    # Never publish a result inferred from an ephemeral Actions artifact alone.
    ledger = build_ledger(root, audit)
    site["metadata"]["files"]["research_ledger"] = "research-ledger.json"
    site["research_ledger"] = ledger
    (data_dir / "research-ledger.json").write_text(
        json.dumps(ledger, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "site-data.json").write_text(
        json.dumps(site, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "metadata.json").write_text(
        json.dumps(site["metadata"], indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    validate_bundle(data_dir)
    validate_static_site(output)
    (output / ".nojekyll").touch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("_site"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        validate_bundle(args.root / "public")
        print("Public bundle is internally consistent")
    else:
        build_site(args.root, args.output)
        print(f"Dashboard ready: {args.output.resolve()}")