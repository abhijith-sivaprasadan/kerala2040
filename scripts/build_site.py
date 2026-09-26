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
from kerala2040.energy_ghg_bridge import validate_energy_ghg_bridge
from kerala2040.flexibility_cooling import build_pilot
from kerala2040.flexibility_dispatch import build_demonstration
from kerala2040.flexibility_integrated import build_integrated
from kerala2040.flexibility_storage import build_screen
from kerala2040.ppac_full_year import validate_ppac_sales
from kerala2040.research_ledger import build_ledger
from kerala2040.total_energy_atlas import validate_total_energy_source_register


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
    if "research_ledger" in files:
        district = read(files["research_ledger"]).get("district_qa")
        if (not district
                or district.get("original_point_centres") != 200_692
                or district.get("unique_district_point_centres") != 200_362
                or district.get("unassigned_point_centres") != 330
                or district.get("ambiguous_point_centres") != 0
                or district.get("complete_district_partition") is not False
                or district.get("district_publication_ready") is not False
                or district.get("eligible_area_km2") is not None
                or district.get("feasible_capacity_MW") is not None
                or district.get("model_admitted") is not False):
            raise ValueError("LRIS district boundary gap incorrectly packaged as complete GIS")
    if "research_ledger" in files:
        district = read(files["research_ledger"]).get("nwic_district")
        if (not district
                or district.get("classification") !=
                "NIWE_NWIC_14_DISTRICT_DESCRIPTIVE_POINT_PARTITION_NOT_CAPACITY"):
            raise ValueError("NWIC district aggregate absent from pinned research snapshot")
        assignment = district.get("point_assignment", {})
        rows = district.get("districts", [])
        if (assignment.get("source_points") != 200_692
                or assignment.get("uniquely_assigned") != 200_692
                or assignment.get("unassigned") != 0
                or assignment.get("ambiguous") != 0
                or assignment.get("complete_descriptive_partition") is not True
                or len(rows) != 14
                or len({row["district"] for row in rows}) != 14
                or sum(row["point_centres"] for row in rows) != 200_692
                or sum(row["slope_finite"] for row in rows) != 199_853
                or sum(row["slope_missing"] for row in rows) != 839
                or district.get("eligible_area_km2") is not None
                or district.get("feasible_capacity_MW") is not None
                or district.get("model_admitted") is not False
                or district.get("source", {}).get("source_reuse_rights_verified") is not False):
            raise ValueError("NWIC district bundle incomplete or incorrectly promoted to eligible capacity")
    if "research_ledger" in files:
        wind_phase = read(files["research_ledger"]).get("wind_phase1", {})
        normalized = wind_phase.get("normalized", {})
        example = normalized.get("spotlight_descriptive_example", {})
        if (wind_phase.get("descriptive_wind_phase1_complete") is not True
                or normalized.get("classification") !=
                "NIWE_NWIC_DISTRICT_NORMALIZED_DESCRIPTIVE_WIND_TERRAIN_SENSITIVITY_NOT_SUITABILITY"
                or normalized.get("qa", {}).get("all_16_threshold_cell_counts_reconciled") is not True
                or normalized.get("statewide", {}).get("source_point_centres") != 200_692
                or normalized.get("statewide", {}).get("finite_DSM_slope_point_centres") != 199_853
                or len(normalized.get("districts", [])) != 14
                or example.get("statewide_matching_point_centres") != 8_637
                or example.get("palakkad_matching_point_centres") != 6_330
                or example.get("idukki_matching_point_centres") != 1_804
                or normalized.get("source_reuse_rights_verified") is not False
                or normalized.get("eligible_area_km2") is not None
                or normalized.get("feasible_capacity_MW") is not None
                or normalized.get("model_admitted") is not False
                or wind_phase.get("site_eligibility_verified") is not False
                or wind_phase.get("feasible_capacity_MW") is not None
                or wind_phase.get("model_admitted") is not False):
            raise ValueError("Wind descriptive phase 1 was not reproducible or was promoted to capacity")
    if "research_ledger" in files:
        solar = read(files["research_ledger"]).get("solar_phase1", {})
        result = solar.get("aggregate", {})
        qa = result.get("qa", {})
        districts = result.get("districts", [])
        if (solar.get("descriptive_solar_phase1_complete") is not True
                or qa.get("NWIC_Kerala_district_pixels") != 46_241
                or qa.get("inside_district_missing_any_of_14_PVOUT_layers") != 0
                or qa.get("inside_district_multiple_assignments") != 0
                or qa.get("all_14_district_counts_reconcile") is not True
                or len(districts) != 14
                or sum(r.get("finite_native_source_pixel_centres", 0) for r in districts) != 46_241
                or result.get("statewide", {}).get("median_paired_Feb_minus_Jul_kWh_kWp_day") != 2.267
                or result.get("statewide", {}).get("median_paired_Feb_to_Jul_drop_pct") != 43.60289
                or solar.get("site_eligibility_verified") is not False
                or solar.get("eligible_area_km2") is not None
                or solar.get("installed_capacity_MW") is not None
                or result.get("installed_capacity_MW") is not None
                or result.get("model_admitted") is not False
                or solar.get("model_admitted") is not False):
            raise ValueError("Descriptive solar phase 1 lacks reconciliation or was promoted to MW")
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
    # Preserve the original decorative identity; quantitative charts stay live Canvas.
    for name in (
        "mark.svg", "icons.svg", "chapter-electric.svg", "chapter-land.svg",
        "chapter-pathways.svg", "chapter-industry.svg",
    ):
        shutil.copy2(root / "docs/assets" / name, assets / name)
    # Preserve the original published identity thumbnails; no static chart images.
    for name in ("kerala2040-share.png", "kerala2040-touch.png"):
        shutil.copy2(root / "docs/assets" / name, assets / name)
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
    # Scenario cards are generated from the canonical public specification rather
    # than the older pinned site-data snapshot. This prevents S0-S5 vocabulary
    # and scenario-count drift while keeping them explicitly unsolved.
    scenario_spec = json.loads(
        (root / "public" / "scenarios.json").read_text(encoding="utf-8")
    )
    scenarios = scenario_spec.get("scenarios", [])
    if (
        len(scenarios) != 6
        or [row.get("code") for row in scenarios] != ["S0", "S1", "S2", "S3", "S4", "S5"]
        or any(row.get("type") is not None for row in scenarios)
    ):
        raise ValueError("Public scenario specification must contain exactly unsolved S0-S5")
    site["scenarios"] = scenarios
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
    # The research chapter is distinct from the pinned FY2024-25 observed bundle.
    # Publish a frozen, public-safe aggregate JSON, never private SLDC row data.
    historic = json.loads((root / "data/evidence/sldc/cet_historical_electricity_story_2026_09_24.json").read_text(encoding="utf-8"))
    if (historic.get("classification") != "source_derived_historical_electricity_story_distinct_reporting_boundaries"
            or historic.get("qa", {}).get("missing_fy2024_25") != 11
            or historic.get("qa", {}).get("no_imputation") is not True
            or historic.get("qa", {}).get("interval_telemetry_present") is not False
            or historic.get("paired_fy_2020_21_2025_26", {}).get("matched_calendar_month_day_count") != 356
            or len(historic.get("official_economic_review_2025_kerala_consumption_mu", {})) != 5
            or len(historic.get("sldc_observed_fy", {})) != 6):
        raise ValueError("Historical research data cannot be promoted without provenance/coverage")
    name = "cet-historical-electricity.json"
    (data_dir / name).write_text(json.dumps(historic, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    site["metadata"]["files"]["historical_electricity"] = name
    (data_dir / "site-data.json").write_text(
        json.dumps(site, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "metadata.json").write_text(
        json.dumps(site["metadata"], indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    # KMML process-only release: do not convert company claims to measured recovery.
    kmml = json.loads((root / "data/evidence/industry/kmml_source_bounded_case_2026_09_24.json").read_text(encoding="utf-8"))
    kmml_scope = kmml.get("scientific_scope", {})
    if (kmml.get("classification") != "KMML_CHAVARA_SOURCE_BOUNDED_PROCESS_CASE_NOT_MEASURED_2024_25_NOT_RECOVERY_FORECAST"
            or len(kmml.get("units", [])) != 9
            or len(kmml.get("streams", [])) != 10
            or kmml_scope.get("measured_mass_energy_water_balance_complete") is not False
            or kmml_scope.get("measured_recovery_credits_available") is not False
            or kmml_scope.get("kmml_case_release_gate_passed") is not False
            or kmml.get("ready_for_numerical_2040_industry_scenario") is not False
            or kmml.get("published_numeric_recovery_by_Kerala2040") is not None
            or any(stream.get("annual_tonnes") is not None
                   or stream.get("annual_mwh") is not None
                   or stream.get("avoided_co2_t") is not None
                   for stream in kmml["streams"])):
        raise ValueError("KMML is a source-bounded process case, not measured circularity")
    site["metadata"]["files"]["kmml_case"] = "kmml-case.json"
    (data_dir / "kmml-case.json").write_text(
        json.dumps(kmml, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "site-data.json").write_text(
        json.dumps(site, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "metadata.json").write_text(
        json.dumps(site["metadata"], indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    # This is a historical TFEC panel plus a distinct provisional six-month sales slice.
    # Never stitch unlike dates or interpret nominal infrastructure as measured consumption.
    energy = json.loads(
        (root / "data/evidence/total_energy/kerala_total_energy_source_register_2026_09_24.json").read_text(
            encoding="utf-8"
        )
    )
    validate_total_energy_source_register(energy)
    site["metadata"]["files"]["total_energy_atlas"] = "total-energy-atlas.json"
    (data_dir / "total-energy-atlas.json").write_text(
        json.dumps(energy, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "site-data.json").write_text(
        json.dumps(site, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "metadata.json").write_text(
        json.dumps(site["metadata"], indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    # Annual oil-company sales are NOT electricity data or Kerala final energy.
    ppac_full = json.loads(
        (root / "data/evidence/total_energy/ppac_full_fy_kerala_source_audit_2026_09_24.json").read_text(
            encoding="utf-8"
        )
    )
    validate_ppac_sales(ppac_full)
    site["metadata"]["files"]["ppac_full_year_sales"] = "ppac-annual-sales.json"
    (data_dir / "ppac-annual-sales.json").write_text(
        json.dumps(ppac_full, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "site-data.json").write_text(
        json.dumps(site, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "metadata.json").write_text(
        json.dumps(site["metadata"], indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    # Calendar-2023 state greenhouse-gas inventory is NOT a fuel, energy,
    # FY2024-25 emissions, or petroleum-import accounting population.
    ghg = json.loads(
        (root / "data/evidence/total_energy/kerala_ghg_sector_bridge_2026_09_24.json").read_text(
            encoding="utf-8"
        )
    )
    validate_energy_ghg_bridge(ghg)
    site["metadata"]["files"]["energy_ghg_bridge"] = "energy-ghg-bridge.json"
    (data_dir / "energy-ghg-bridge.json").write_text(
        json.dumps(ghg, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "site-data.json").write_text(
        json.dumps(site, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "metadata.json").write_text(
        json.dumps(site["metadata"], indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    # WP6 first quantitative experiment is synthetic by construction, and is
    # regenerated from committed inputs. Do not publish it as Kerala grid results.
    cooling = build_pilot()
    if (cooling["classification"]
            != "WP6_SYNTHETIC_24H_1R1C_COOLING_COMPARISON_NOT_KERALA_GRID_RESULT"
            or any(cooling["science_gates"].values())
            or any(len(result["hourly"]) != 24 for result in cooling["cases"].values())
            or len(cooling["sensitivity"]) != 9):
        raise ValueError("WP6 experimental origin, coverage or publication gate changed")
    site["metadata"]["files"]["wp6_cooling_pilot"] = "wp6-cooling-pilot.json"
    (data_dir / "wp6-cooling-pilot.json").write_text(
        json.dumps(cooling, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "site-data.json").write_text(
        json.dumps(site, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "metadata.json").write_text(
        json.dumps(site["metadata"], indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    # WP6 synthetic EV and optional industrial dispatch preserve service,
    # availability and connection constraints; NO measured Kerala or KMML claims.
    for kind, filename in (("ev", "wp6-ev-pilot.json"),
                           ("industry", "wp6-industry-pilot.json")):
        trial = build_demonstration(kind)
        if (len(trial["baseline"]["hourly"]) != 24
                or len(trial["managed"]["hourly"]) != 24
                or len(trial["sensitivity"]) != 9
                or any(trial["science_gates"].values())
                or trial["comparison"]["total_electricity_change_kwh"] != 0
                or trial["managed"]["summary"]["missed_deadlines"] != 0):
            raise ValueError("WP6 flex source, terminal service or real-Kerala gate breached")
        site["metadata"]["files"][f"wp6_{kind}_pilot"] = filename
        (data_dir / filename).write_text(
            json.dumps(trial, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    (data_dir / "site-data.json").write_text(
        json.dumps(site, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "metadata.json").write_text(
        json.dumps(site["metadata"], indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    # Storage is a synthetic fixed-service electrical cell. Hydro head and water
    # are NOT Idukki/Pallivasal or source-calibrated cascade constraints.
    storage = build_screen()
    if (storage["classification"]
            != "WP6_SYNTHETIC_BESS_PSP_FIXED_SERVICE_NOT_KERALA_FEASIBILITY"
            or any(storage["release"].values())
            or storage["input"]["source_discovery"]["source_page_image_verified"] is not False
            or any(len(x["hourly"]) != 24 for x in storage["cases"].values())
            or any(len(x) != 9 for x in storage["sensitivities"].values())
            or any(x["summary"]["terminal_stored_kwh"] != 0
                   for x in storage["cases"].values())):
        raise ValueError("WP6 storage source/physics/final-state release gate failed")
    site["metadata"]["files"]["wp6_storage_screen"] = "wp6-bess-psp.json"
    (data_dir / "wp6-bess-psp.json").write_text(
        json.dumps(storage, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "site-data.json").write_text(
        json.dumps(site, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "metadata.json").write_text(
        json.dumps(site["metadata"], indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    integrated = build_integrated()
    if (integrated["classification"] != "WP6_SYNTHETIC_SYNCHRONIZED_SITE_NOT_KERALA_GRID_DISPATCH"
            or any(integrated["release"].values())
            or any(len(case["hourly"]) != 24 for case in integrated["cases"].values())):
        raise ValueError("Integrated WP6 synthetic-only gate failed")
    site["metadata"]["files"]["wp6_integrated_dispatch"] = "wp6-integrated-dispatch.json"
    (data_dir / "wp6-integrated-dispatch.json").write_text(
        json.dumps(integrated, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "site-data.json").write_text(
        json.dumps(site, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (data_dir / "metadata.json").write_text(
        json.dumps(site["metadata"], indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    # Durable, explicitly classified research results; not a validated capacity plan.
    model_records = []
    source_audits = []
    for filename, source_path in {
        "idukki-reservoir.json": "data/evidence/models/full_pypsa_idukki_reservoir_v1_3_2026_09_26.json",
        "idukki-source-gate.json": "data/evidence/hydro/idukki_v1_4_real_source_gate_2026_09_26.json",
        "idukki-cumulative-recovery.json": "data/evidence/hydro/idukki_v1_4_cumulative_recovery_2026_09_26.json",
        "idukki-cumulative-qa.json": "data/evidence/hydro/idukki_v1_4b_cumulative_inflow_qa_2026_09_26.json",
        "kseb-source-boundary.json": "data/evidence/hydro/idukki_v1_5_official_source_boundary_2026_09_26.json",
        "kseb-monthly-inventory.json": "data/evidence/hydro/kseb_monthly_reservoir_inventory_fy2024_25_2026_09_26.json",
        "hydro-flex.json": "data/evidence/models/full_pypsa_hydro_flex_v1_1_2026_09_26.json",
        "hydro-interday.json": "data/evidence/models/full_pypsa_hydro_interday_v1_2_2026_09_26.json",
        "import-economics.json": "data/evidence/models/full_pypsa_import_economics_v1_0_2026_09_26.json",
        "model-equivalence.json": "data/evidence/models/full_pypsa_pypsa_equivalence_v0_9_2026_09_25.json",
        "expansion-screen.json": "data/evidence/models/full_pypsa_proxy_expansion_v0_8_2026_09_25.json",
    }.items():
        raw = (root / source_path).read_bytes()
        record = json.loads(raw)
        if not record.get("classification") or not record.get("prepared_date"):
            raise ValueError("Published model evidence must retain classification and date")
        if (record.get("model_admission", {}).get("validated_capacity_plan")
                or record.get("guardrails", {}).get("validated_capacity_plan")
                or record.get("release", {}).get("validated_capacity_plan")):
            raise ValueError("V2 research experiments cannot be promoted to a capacity plan")
        shutil.copy2(root / source_path, data_dir / filename)
        records = model_records if "/models/" in source_path else source_audits
        records.append({"file": filename, "source_path": source_path,
                              "sha256": hashlib.sha256(raw).hexdigest(),
                              "prepared_date": record["prepared_date"],
                              "classification": record["classification"]})
        site["metadata"]["files"][filename.removesuffix(".json").replace("-", "_")] = filename
    site["metadata"]["published_model_records"] = model_records
    site["metadata"]["published_source_audits"] = source_audits
    site["metadata"]["website_edition"] = 2
    site["metadata"]["publication_policy"] = (
        "observed_and_derived_evidence_plus_explicitly_labelled_resource_and_model_experiments"
    )
    for name, payload in (("metadata.json", site["metadata"]), ("site-data.json", site)):
        (data_dir / name).write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n",
                                     encoding="utf-8")
    catalogue = []
    for path in sorted(data_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        classification = payload.get("classification", payload.get("evidence", "Source bundle")) if isinstance(payload, dict) else "Source records"
        catalogue.append({"file": path.name, "classification": classification})
    (data_dir / "catalogue.json").write_text(json.dumps(catalogue, indent=2) + "\n", encoding="utf-8")
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
