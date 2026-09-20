"""Audit evidence and fail-closed release gates for the Kerala2040 research repo.

This audits committed evidence, NOT local-only files, workflow artifacts, agency
databases or the live site. A missing verification implementation is *blocked*;
mere presence of an arbitrary self-declared manifest cannot turn a gate green.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

QA = "data/external/sldc_fy2024_25/qa_report.json"
ERA5 = "public/era5-daily-manifest.json"
TECH = "configs/techno_economics.yaml"
GIS = "configs/gis_inputs.yaml"
LULC = "configs/lulc_native_acquisition_2024_25.yaml"
GIS_3 = "configs/gis_forest_dem_wetlands_hazards_2026.yaml"
FINDINGS = "configs/audit_findings.yaml"
HYDRO_TOPOLOGY = "configs/hydro_topology_evidence_2024_25.yaml"
TRANSFER = "configs/grid_transfer_contract_evidence_2024_25.yaml"
GENERATORS = "configs/generator_reconciliation_2024_25.yaml"
PROJECTS = "public/kseb-projects.json"

STATUS_PASS = "verified_in_committed_evidence"
STATUS_PARTIAL = "partial_or_provisional"
STATUS_BLOCKED = "blocked_missing_verified_evidence"


def _json(root: Path, path: str) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _yaml(root: Path, path: str) -> dict[str, Any]:
    return yaml.safe_load((root / path).read_text(encoding="utf-8"))


def _check(status: str, detail: str, evidence: str) -> dict[str, str]:
    return {"status": status, "detail": detail, "evidence": evidence}


def _missing_costs(node: Any, prefix: str = "") -> list[str]:
    """Report unresolved model inputs, not external benchmark entries."""
    if isinstance(node, dict):
        result = []
        for key, value in node.items():
            if key == "selection_status":
                if value != "verified_for_kerala_2040":
                    result.append(f"{prefix}{key}={value}")
            else:
                result.extend(_missing_costs(value, f"{prefix}{key}."))
        return result
    return [prefix[:-1]] if node is None else []


def inspect_committed_evidence(root: Path) -> dict[str, dict[str, str]]:
    qa = _json(root, QA)
    era = _json(root, ERA5)
    techno = _yaml(root, TECH)
    gis = _yaml(root, GIS)

    expected = qa["expected_days"]
    observed = qa["observed_days"]
    missing = qa["missing_dates"]
    if expected != 365 or observed + len(missing) != expected or len(set(missing)) != len(missing):
        raise ValueError("SLDC QA coverage inconsistent: cannot issue a readiness report")
    if qa["bad_raw_sha256_count"] or qa["bad_response_report_date_count"]:
        raise ValueError("Raw SLDC source hash or report-date verification failed")
    residual = float(qa["max_abs_daily_balance_residual_mu"])
    if not 0 <= residual <= 0.001:
        raise ValueError("SLDC energy-balance integrity gate failed")
    if qa["source_archive_sha256"] == "":
        raise ValueError("SLDC raw archive identity missing")
    accounting = _check(
        STATUS_PASS,
        f"{observed}/{expected} observed daily balances; max absolute balance residual "
        f"{residual} MU; source SHA recorded. NOT full-year totals or interval validation.",
        QA,
    )
    daily = _check(
        STATUS_PASS if observed == expected else STATUS_PARTIAL,
        f"{observed}/{expected} observed days; {len(missing)} missing: {', '.join(missing)}",
        QA,
    )
    succeeded = int(era["files_succeeded"])
    total = int(era["files_expected"])
    files = era["files"]
    if succeeded != len(files) or not 0 <= succeeded <= total:
        raise ValueError("ERA5 manifest file counts inconsistent")
    # Even a complete manifest is NOT independently calibrated power output.
    weather = _check(
        STATUS_PARTIAL if succeeded else STATUS_BLOCKED,
        f"{succeeded}/{total} ERA5 source files recorded. Weather-resource modelling "
        "and measured generation validation are separate; the full-year profile "
        "is not certified by this acquisition manifest.",
        ERA5,
    )
    grid = techno["model_input_grid"]
    unresolved = _missing_costs(grid["technologies"], "technologies.")
    unresolved += _missing_costs(techno["system_finance"], "system_finance.")
    if grid.get("classification") != "unresolved" and unresolved:
        raise ValueError("Technology cost registry claims completeness with unresolved inputs")
    economic = _check(
        STATUS_BLOCKED if unresolved else STATUS_PARTIAL,
        f"{len(unresolved)} unresolved/null or unverified fields in 2040 model "
        "and finance inputs. External CEA/CERC benchmarks are NOT local cost defaults."
        if unresolved else ("Entries filled; independent unit/year/source "
                            "validation still required."),
        TECH,
    )
    generator = _yaml(root, GENERATORS)
    portal = _json(root, PROJECTS)
    official = generator["official_totals"]
    if generator.get("classification") != (
        "official_crosscheck_of_project_portal_not_complete_operating_fleet"
    ):
        raise ValueError("Generator reconciliation classification mismatch")
    if abs(
        float(official["all_kerala_installed_mw"])
        - float(_yaml(root, "configs/observed_2024_25.yaml")["electricity"][
            "installed_capacity_mw"
        ])
    ) > 0.01:
        raise ValueError("Generator all-owner capacity does not match official baseline")
    names = {item["name"]: item for item in portal["projects"]}
    events = generator["official_commissioned_during_fy"]
    crosschecked_mw = 0.0
    for event in events:
        name = event["portal_name"]
        if name not in names or names[name]["technology"] != event["technology"]:
            raise ValueError("Generator crosscheck project absent or technology differs")
        sources = event["sources"]
        if len(set(sources)) < 2 or any(
            key not in generator["primary_sources"]
            or not generator["primary_sources"][key].get("url")
            for key in sources
        ):
            raise ValueError("Generator commissioning requires two documented sources")
        mw = float(event["commissioned_mw"])
        if abs(sum(float(unit["capacity_mw"]) for unit in event["units"]) - mw) > 0.001:
            raise ValueError("Generator crosscheck unit MW differ from commissioned MW")
        crosschecked_mw += mw
    reported = int(portal["portal_reported_total"])
    observed_portal = len(portal["projects"])
    if reported < observed_portal:
        raise ValueError("Generator portal reported count is less than acquired records")
    generator_check = _check(
        STATUS_PARTIAL,
        f"{observed_portal}/{reported} portal project records captured; "
        f"{len(events)} FY2024-25 plant additions independently crosschecked "
        f"({crosschecked_mw:g} MW). KSEBL owned vs all-owner installed totals are "
        "kept separate. The project explorer is not a validated complete "
        "commissioned/available fleet; generation, outages and non-KSEBL assets "
        "are not reconciled.",
        "docs/GENERATOR_REGISTER_FY2024_25_RECONCILIATION.md",
    )
    hydro = _yaml(root, HYDRO_TOPOLOGY)
    if hydro.get("classification") != (
        "partial_official_hydro_topology_not_dispatch_constraints"
    ):
        raise ValueError("Hydro topology cannot claim validated dispatch constraints")
    hydro_count = len(hydro["observed_reservoirs"])
    hydro_edges = len(hydro["documented_links"])
    if not hydro_count or not hydro_edges:
        raise ValueError("Hydro mapping must identify sourced nodes and links")
    transfer = _yaml(root, TRANSFER)
    if transfer.get("classification") != (
        "partial_public_transfer_and_procurement_evidence_not_model_constraints"
    ):
        raise ValueError("Grid transfer evidence may not claim a validated ATC series")
    if transfer["model_use"].get("status") != STATUS_BLOCKED or any(
        transfer["model_use"].get(k) is not False
        for k in (
            "can_apply_snapshot_as_full_year_import_limit",
            "can_use_daily_import_mu_as_interface_mw",
            "can_sum_contract_nameplates_as_import_atc",
            "can_treat_exchange_price_as_delivered_cost",
        )
    ):
        raise ValueError("Grid transfer source cannot certify model constraints")
    snapshots = transfer["transfer_snapshots"]
    for snapshot in snapshots:
        if (
            snapshot.get("atc_derivation") == "ttc_minus_stated_reliability_margin"
            and abs(
                float(snapshot["ttc_mw"]) - float(snapshot["reliability_margin_mw"])
                - float(snapshot["atc_mw"])
            ) > 0.001
        ):
            raise ValueError("Grid transfer snapshot ATC/margin is inconsistent")
    if transfer["unresolved_constraints"]["full_fy2024_25_dated_import_atc_mw"] is not None:
        raise ValueError("Unverified FY transfer capacity inserted in source catalogue")
    lulc = _yaml(root, LULC)
    if lulc.get("classification") != (
        "official_lulc_discovery_no_native_kerala_raster_acquired"
    ):
        raise ValueError("LULC registry cannot claim a native raster acquisition")
    products = lulc["products"]
    if len({entry["id"] for entry in products}) != len(products):
        raise ValueError("Duplicate NRSC LULC discovery product IDs")
    preferred = [entry for entry in products if entry.get("preferred_reference")]
    if len(preferred) != 1 or preferred[0]["reported_vintage"] != "2024-25":
        raise ValueError("LULC target vintage/candidate is not source-qualified")
    if preferred[0]["native_sha256"] is not None:
        raise ValueError("Raw NRSC raster SHA claims source acquisition without inspection")
    if any(lulc["model_use"][key] is not False for key in (
        "native_kerala_lulc_acquired",
        "native_kerala_lulc_validated",
        "ecological_exclusion_ready",
    )):
        raise ValueError("LULC catalogue cannot certify real land eligibility")
    if (
        lulc["model_use"]["land_available_area_sq_km"] is not None
        or lulc["model_use"]["generation_capacity_ceiling_mw"] is not None
    ):
        raise ValueError("LULC cannot contain unsupported capacity or eligible area")
    gis_three = _yaml(root, GIS_3)
    if gis_three.get("classification") != (
        "source_scoped_three_workstream_gis_review_not_validated_geometry"
    ):
        raise ValueError("GIS workstream source review may not certify model geometry")
    reviewed = gis_three["workstreams"]
    if set(reviewed) != {
        "forest_protected_areas", "elevation_dem", "wetlands_waterbodies_landslide"
    }:
        raise ValueError("GIS workstream discovery must cover all three tasks")
    if any(gis_three["model_use"][key] is not False for key in (
        "authoritative_forest_exclusions_verified",
        "full_kerala_height_and_slope_verified",
        "wetland_waterbody_land_hazard_overlay_verified",
        "ecological_capacity_ceiling_ready",
    )):
        raise ValueError("Unverified GIS source registry cannot certify spatial exclusions")
    if any(gis_three["model_use"][key] is not None for key in (
        "eligible_area_sq_km", "potential_mw",
    )):
        raise ValueError("Unverified GIS source registry cannot invent eligibility")
    gsi_count = len(
        reviewed["wetlands_waterbodies_landslide"]["published_gsi_district_labels"]
    )
    if gsi_count != 13:
        raise ValueError("Published GSI 2022 source list must preserve district scope")
    n_layers = len(gis["layers"])
    staged = sum(
        item["acquisition_status"] not in (
            "not_downloaded", "not_downloaded_in_repository",
            "not_downloaded_native_data_requires_approved_route",
            "official_download_listed_but_not_committed_verified",
            "official_internal_gis_reported_geometry_not_secured",
            "source_routes_verified_statewide_raster_not_committed",
            "draft_notified_legal_distinction_original_geometry_not_secured",
            "authoritative_geometry_not_yet_secured",
            "current_authoritative_geometry_not_yet_secured",
            "download_form_required",
        )
        for item in gis["layers"].values()
    )
    gis_check = _check(
        STATUS_BLOCKED,
        f"{n_layers} catalogued GIS layers; {staged} beyond acquisition-only status; "
        f"{len(products)} NRSC LULC product routes and three forest/DEM/hazard "
        f"workstreams reviewed; KSDMA advertises {gsi_count} GSI 2022 district "
        "downloads but original geometry is unverified in committed evidence. "
        "Forest notifications, statewide DEM mosaic and final SWAK wetland "
        "polygons remain absent. No authenticated statewide mask, technical "
        "eligibility overlay, legal status or MW ceiling QA is evidenced here.",
        "docs/FOREST_DEM_WETLANDS_LANDSLIDE_GIS_AUDIT.md",
    )
    return {
        "sldc_accounting_integrity": accounting,
        "sldc_daily_coverage": daily,
        "measured_interval": _check(
            STATUS_BLOCKED,
            "Official sources show that FY2024-25 hourly Kerala demand was analysed "
            "by CEA and that SRPC publishes Kerala DSM actual-drawal accounting, but "
            "the repository still lacks a complete authenticated interval demand plus "
            "actual-interchange chronology with boundary, clock, revision and daily-"
            "reconciliation checks. The 8,760-hour proxy cannot satisfy this gate.",
            "docs/INTERVAL_ELECTRICITY_SOURCE_REVIEW.md",
        ),
        "generator_assets": generator_check,
        "hydro_physics": _check(
            STATUS_BLOCKED,
            f"{hydro_count} SLDC reservoir names mapped by selected official dam "
            f"descriptions across {hydro_edges} qualitative links, alongside 354 "
            "observed SLDC days. No complete hydrological network, independently "
            "reconciled water balance, release/spill routing, head curves or "
            "operative environmental/rule-curve constraints. Source MU is not "
            "an independent dispatchable reservoir Store.",
            "docs/HYDRO_RESERVOIR_OPERATIONS_AUDIT.md",
        ),
        "grid_transfer": _check(
            STATUS_BLOCKED,
            f"354 observed days with eight grouped SLDC daily energy interface rows "
            f"and {len(snapshots)} dated reported transfer snapshots. January TTC "
            "and reliability margin and March reported capability are not a "
            "revision-controlled FY ATC/TTC profile. Contract deliverability, "
            "banking obligations, actual schedules and landed costs unresolved. "
            "Illustrative 6500 MW screening bound is NOT Kerala import capability.",
            "docs/GRID_TRANSFER_CONTRACTS_FY2024_25_AUDIT.md",
        ),
        "gis_model_ready": gis_check,
        "era5_complete": weather,
        "technology_costs": economic,
        "kmml_measured": _check(
            STATUS_BLOCKED,
            "No validated KMML production-aligned material, process energy/water "
            "and effluent measurements with a declared boundary.",
            "docs/KMML_CASE_PLAN.md",
        ),
        "cstep_raw_2016": _check(
            STATUS_BLOCKED,
            "Published description of an FY2016 15-minute dataset is not the "
            "authenticated underlying time series.",
            "docs/CSTEP_FY2016_DATA_REQUEST_DRAFT.md",
        ),
    }


def build_audit(root: Path) -> dict[str, Any]:
    catalogue = _yaml(root, FINDINGS)
    checks = inspect_committed_evidence(root)
    items = []
    seen: set[str] = set()
    for entry in catalogue["findings"]:
        if entry["id"] in seen:
            raise ValueError(f"Duplicate audit finding {entry['id']}")
        seen.add(entry["id"])
        key = entry["check"]
        if key not in checks:
            raise ValueError(f"Unknown audit check {key}")
        items.append({**entry, "verification": checks[key]})
    gates = {}
    for gate, definition in catalogue["release_gates"].items():
        required = definition["required"]
        unknown = set(required) - checks.keys()
        if unknown:
            raise ValueError(f"Unknown {gate} gate checks: {sorted(unknown)}")
        gates[gate] = {
            "passed": all(checks[key]["status"] == STATUS_PASS for key in required),
            "required_checks": required,
            "blocking_checks": [
                key for key in required if checks[key]["status"] != STATUS_PASS
            ],
            "description": definition["description"],
        }
    return {
        "classification": "repository_evidence_audit_not_external_source_validation",
        "scope": catalogue["scope"],
        "source_qa_sha256": _json(root, QA)["source_archive_sha256"],
        "audit_policy": catalogue["policy"],
        "evidence_limit": (
            "Only committed repository inputs evaluated; no claim about external "
            "agency access, uncommitted local files or workflow artifacts."
        ),
        "checks": checks,
        "findings": items,
        "release_gates": gates,
        "finding_count": len(items),
        "closed_findings": sum(
            f["verification"]["status"] == STATUS_PASS for f in items
        ),
        "open_findings": sum(
            f["verification"]["status"] != STATUS_PASS for f in items
        ),
    }


def markdown_report(audit: dict[str, Any]) -> str:
    lines = [
        "# Kerala 2040 — evidence-gated audit",
        "",
        (f"**{audit['closed_findings']}/{audit['finding_count']} acquisition findings "
         "verified in committed evidence.**"),
        "",
        f"Scope: {audit['scope']}. {audit['evidence_limit']}",
        "",
        "## Release gates",
        "",
        "| Gate | Status | Blocking checks |",
        "|---|---|---|",
    ]
    for key, gate in audit["release_gates"].items():
        lines.append(
            f"| {key} | {'PASS' if gate['passed'] else 'BLOCKED'} | "
            f"{', '.join(gate['blocking_checks']) or 'none'} |"
        )
    lines.extend([
        "", "## Outstanding acquisitions", "",
        "| Priority | Finding | Committed evidence status | Required evidence |",
        "|---|---|---|---|",
    ])
    for item in audit["findings"]:
        lines.append(
            f"| {item['priority']} | {item['id']} | "
            f"{item['verification']['status']} | {item['acquisition']} |"
        )
    lines.extend([
        "", ("Daily accounting passing does not demonstrate complete-year or "
             "hourly calibration. A proxy-based 2040 HiGHS solve does not pass "
             "the techno-economic, hydro, grid, GIS or interval-data gates."), "",
    ])
    return "\n".join(lines)
