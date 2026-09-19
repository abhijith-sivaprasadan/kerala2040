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
FINDINGS = "configs/audit_findings.yaml"

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
    n_layers = len(gis["layers"])
    staged = sum(
        item["acquisition_status"] not in (
            "not_downloaded", "not_downloaded_in_repository",
            "authoritative_geometry_not_yet_secured",
            "current_authoritative_geometry_not_yet_secured",
            "download_form_required",
        )
        for item in gis["layers"].values()
    )
    gis_check = _check(
        STATUS_BLOCKED,
        f"{n_layers} catalogued layers; {staged} marked beyond acquisition-only status "
        "in the committed catalogue. No validated technology-specific eligibility "
        "overlay, authoritative legal status and capacity-ceiling QA are evidenced here.",
        GIS,
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
        "generator_assets": _check(
            STATUS_PARTIAL,
            "Inventory builder and project tracker exist, but commissioned plant-level "
            "assets/availability and generation are not reconciled and approved.",
            "scripts/build_generator_database.py",
        ),
        "hydro_physics": _check(
            STATUS_BLOCKED,
            "Daily observed reservoir and hydro evidence does not establish verified "
            "cascade topology, head, releases/spill or operational energy constraints.",
            "docs/OBSERVED_DAILY_PYPSA.md",
        ),
        "grid_transfer": _check(
            STATUS_BLOCKED,
            "Observed imported energy and illustrative 6500 MW screening bound are "
            "not verified transfer capability, procurement contracts or cost series.",
            "configs/pypsa_screening_example.yaml",
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
