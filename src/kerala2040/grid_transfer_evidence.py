"""Audit historical interchange against dated, explicitly non-dispatch transfer evidence."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import yaml

QA = "data/external/sldc_fy2024_25/qa_report.json"
DAILY = "data/external/sldc_fy2024_25/daily_balance.csv"
INTERFACES = "data/external/sldc_fy2024_25/import_interface_daily.csv"
EVIDENCE = "configs/grid_transfer_contract_evidence_2024_25.yaml"
OBSERVED = "configs/observed_2024_25.yaml"
SOURCE_SHA = re.compile(r"[0-9a-f]{64}")


def _csv(root: Path, path: str) -> list[dict[str, str]]:
    with (root / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _number(raw: str) -> float:
    number = float(raw)
    if not math.isfinite(number):
        raise ValueError("Non-finite import energy in SLDC extract")
    return number


def _transfer_source_checks(evidence: dict[str, Any]) -> None:
    if evidence.get("classification") != (
        "partial_public_transfer_and_procurement_evidence_not_model_constraints"
    ):
        raise ValueError("Transfer source classification cannot claim dispatch readiness")
    if evidence["period"] != "FY2024-25":
        raise ValueError("Incorrect transfer evidence financial year")
    source_ids = set(evidence["sources"])
    for key, entry in evidence["sources"].items():
        link = entry.get("url") or entry.get("third_party_access_url")
        if not link or not link.startswith("https://"):
            raise ValueError(f"Missing transfer source URL: {key}")
    prior: date | None = None
    for snapshot in evidence["transfer_snapshots"]:
        day = date.fromisoformat(snapshot["date"])
        if prior and day <= prior:
            raise ValueError("Transfer snapshots are not strictly dated/in order")
        prior = day
        if not set(snapshot["source_ids"]) <= source_ids:
            raise ValueError("Transfer snapshot source reference is missing")
        if snapshot.get("scope") != "Kerala_state_aggregate_import":
            raise ValueError("Transfer snapshot scope mismatch")
        ttc, margin, atc = (
            snapshot.get("ttc_mw"),
            snapshot.get("reliability_margin_mw"),
            snapshot.get("atc_mw"),
        )
        if snapshot.get("atc_derivation") == "ttc_minus_stated_reliability_margin":
            if any(x is None for x in (ttc, margin, atc)):
                raise ValueError("Transfer TTC/margin/ATC snapshot incomplete")
            if min(ttc, atc) <= 0 or margin < 0 or abs(ttc - margin - atc) > 0.001:
                raise ValueError("ATC inconsistent with TTC and reliability margin")
        elif atc is not None:
            raise ValueError("Unqualified ATC cannot be promoted from reported capability")
    for contract in evidence["procurement_examples"]:
        if not set(contract["source_ids"]) <= source_ids:
            raise ValueError("Procurement reference lacks source")
        if contract["fy2024_25_deliverable_mw"] is not None:
            raise ValueError("No verified FY24-25 deliverable contract MW in evidence")
        signed = contract.get("agreement_date")
        if (
            signed
            and date.fromisoformat(signed) > date(2025, 3, 31)
            and contract["classification"] != "signed_after_fy2024_25_not_historical_supply"
        ):
            raise ValueError("Post-year agreement incorrectly counted as historical")
    unresolved = evidence["unresolved_constraints"]
    if any(
        value is not None for key, value in unresolved.items()
        if key in {
            "full_fy2024_25_dated_import_atc_mw",
            "full_fy2024_25_dated_export_atc_mw",
            "full_fy2024_25_dated_ttc_mw",
            "hourly_or_blockwise_transfer_availability",
        }
    ):
        raise ValueError("Unverified transfer chronology inserted into evidence")
    use = evidence["model_use"]
    if use["status"] != "blocked_missing_verified_evidence" or any(
        use[key] is not False
        for key in (
            "can_apply_snapshot_as_full_year_import_limit",
            "can_use_daily_import_mu_as_interface_mw",
            "can_sum_contract_nameplates_as_import_atc",
            "can_treat_exchange_price_as_delivered_cost",
        )
    ):
        raise ValueError("Transfer evidence may not enable model dispatch constraints")


def audit_transfer_evidence(root: Path) -> dict[str, Any]:
    qa = json.loads((root / QA).read_text(encoding="utf-8"))
    evidence = yaml.safe_load((root / EVIDENCE).read_text(encoding="utf-8"))
    observed = yaml.safe_load((root / OBSERVED).read_text(encoding="utf-8"))
    _transfer_source_checks(evidence)
    daily = _csv(root, DAILY)
    rows = _csv(root, INTERFACES)
    if len(rows) != qa["normalized_row_counts"]["import_interface"]:
        raise ValueError("Import-interface count does not match original SLDC QA")
    if len(daily) != qa["normalized_row_counts"]["daily_balance"]:
        raise ValueError("Daily balance count does not match original SLDC QA")
    observed_days = {r["date"] for r in daily if r["status"] == "observed"}
    missing_days = {r["date"] for r in daily if r["status"] == "missing"}
    if (len(observed_days) != qa["observed_days"]
            or missing_days != set(qa["missing_dates"])
            or observed_days & missing_days
            or len(daily) != qa["expected_days"]
            or len({r["date"] for r in daily}) != len(daily)):
        raise ValueError("Import chronology has inconsistent observed/missing coverage")
    if not qa["source_archive_sha256"] or qa["bad_raw_sha256_count"]:
        raise ValueError("Source import archive integrity is not established")
    day_rows: dict[str, dict[str, float]] = defaultdict(dict)
    daily_hashes: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        day, name, digest = (
            row["date"], row["interface_name_as_reported"], row["source_sha256"]
        )
        if day not in observed_days or not SOURCE_SHA.fullmatch(digest):
            raise ValueError("Import interface lacks verified observed date or SHA")
        if name in day_rows[day]:
            raise ValueError(f"Duplicate grouped import interface {day} {name}")
        day_rows[day][name] = _number(row["import_mu"])
        daily_hashes[day].add(digest)
    if set(day_rows) != observed_days or any(len(h) != 1 for h in daily_hashes.values()):
        raise ValueError("Missing import day or inconsistent source SHA")
    names = set.union(*(set(items) for items in day_rows.values()))
    if len(names) != 8 or any(set(items) != names for items in day_rows.values()):
        raise ValueError("Import interface names/coverage change; inspect source")
    total = 0.0
    max_residual = 0.0
    max_daily_energy = -float("inf")
    for row in daily:
        if row["status"] != "observed":
            continue
        amount = _number(row["net_import_mu"])
        total += amount
        max_daily_energy = max(max_daily_energy, amount)
        residual = abs(sum(day_rows[row["date"]].values()) - amount)
        max_residual = max(max_residual, residual)
        if residual > 0.001:
            raise ValueError(f"SLDC import interface daily residual exceeds tolerance: {row['date']}")
    reference = evidence["annual_source_accounting_reference"]
    baseline = observed["electricity"]
    if abs(total - float(reference["observed_days_only_net_import_mu"])) > 0.001:
        raise ValueError("Observed-only imported MU differs from recorded source baseline")
    if abs(total - float(qa["observed_days_totals_mu"]["net_import_mu"])) > 0.001:
        raise ValueError("Import energy differs from original SLDC source QA")
    for key, reference_key in (
        ("gross_import_per_annum_mu", "all_year_ksebl_gross_import_mu"),
        ("export_per_annum_mu", "all_year_ksebl_export_mu"),
    ):
        if abs(float(baseline[key]) - float(reference[reference_key])) > 0.001:
            raise ValueError("Annual import/export boundary differs from Economic Review")
    if abs(
        float(baseline["energy_sources_2024_25_mu"]["total_power_purchase"])
        - float(reference["all_year_ksebl_total_power_purchase_mu"])
    ) > 0.001:
        raise ValueError("Annual purchases differ from Economic Review")
    if reference["observed_days"] != len(observed_days):
        raise ValueError("Observed-only import days inconsistent")
    return {
        "classification": "verified_observed_daily_import_accounting_and_partial_transfer_references_NOT_model_limits",
        "source_archive_sha256": qa["source_archive_sha256"],
        "source_evidence": [QA, DAILY, INTERFACES, EVIDENCE, OBSERVED],
        "observed_days": len(observed_days),
        "expected_days": qa["expected_days"],
        "missing_dates": sorted(missing_days),
        "import_interface_rows": len(rows),
        "reported_grouped_interfaces": len(names),
        "reported_interface_names": sorted(names),
        "max_daily_interface_reconciliation_residual_mu": max_residual,
        "observed_days_only_net_import_mu": round(total, 4),
        "maximum_observed_daily_import_energy_mu": max_daily_energy,
        "dated_transfer_snapshot_count": len(evidence["transfer_snapshots"]),
        "full_fy_atc_ttc_profile_verified": False,
        "export_transfer_profile_verified": False,
        "contract_deliverability_verified": False,
        "contract_landed_prices_verified": False,
        "model_import_limit_verified": False,
        "existing_6500_mw_is_only_scenario_assumption": True,
        "audit_gate_closed": False,
        "interpretation": (
            "Dated SLDC grouped daily import MU reconcile to daily net import on "
            "observed days only. SRPC/KSEBL dated capability references are not a "
            "full-year ATC/TTC series. Nameplate PPAs, schedules, market prices, "
            "daily MU and hourly import rights are not interchangeable."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output", type=Path, default=Path("results/grid/transfer_contract_evidence.json")
    )
    args = parser.parse_args()
    report = audit_transfer_evidence(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n",
                           encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
