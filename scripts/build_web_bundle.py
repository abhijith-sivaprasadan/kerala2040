"""Build the public Kerala 2040 web-data bundle from configs and processed evidence.

The bundle never fabricates missing observations. Files that are unavailable are reported
explicitly in metadata and omitted from data products.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from kerala2040.analysis import add_daily_indicators


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass
    return value


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _scenario_payload(config: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for key, value in config.get("scenarios", {}).items():
        code = key.split("_", 1)[0]
        label = key.split("_", 1)[1].replace("_", " ").title() if "_" in key else key
        result.append(
            {
                "id": key,
                "code": code,
                "name": label,
                "type": value.get("type"),
                "description": value.get("description"),
                "ecology_constraint": value.get("ecology_constraint"),
                "demand_flexibility": value.get("demand_flexibility"),
                "import_option": value.get("import_option"),
            }
        )
    return result


def _load_daily(root: Path) -> pd.DataFrame | None:
    analysed = root / "results/baseline/daily_indicators.parquet"
    raw = root / "data/processed/sldc_daily.parquet"
    if analysed.exists():
        data = pd.read_parquet(analysed)
        if "import_share" not in data.columns:
            data = add_daily_indicators(data)
        return data
    if raw.exists():
        return add_daily_indicators(pd.read_parquet(raw))
    return None


def _daily_products(
    data: pd.DataFrame,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    work = data.copy()
    work["date"] = pd.to_datetime(work["date"]).dt.normalize()
    wanted = [
        "date",
        "consumption_mu",
        "internal_generation_mu",
        "net_import_interface_mu",
        "hydel_total_mu",
        "import_share",
        "internal_share",
        "hydro_share_consumption",
        "storage_pct_energy_weighted",
    ]
    cols = [c for c in wanted if c in work.columns]
    daily = work[cols].sort_values("date").copy()
    daily["date"] = daily["date"].dt.strftime("%Y-%m-%d")

    work["month"] = work["date"].dt.to_period("M").astype(str)
    sum_cols = [
        c
        for c in [
            "consumption_mu",
            "internal_generation_mu",
            "net_import_interface_mu",
            "hydel_total_mu",
        ]
        if c in work.columns
    ]
    monthly = work.groupby("month", as_index=False)[sum_cols].sum(min_count=1)
    if {"net_import_interface_mu", "consumption_mu"}.issubset(monthly.columns):
        monthly["import_share"] = monthly["net_import_interface_mu"] / monthly["consumption_mu"]
    if {"internal_generation_mu", "consumption_mu"}.issubset(monthly.columns):
        monthly["internal_share"] = monthly["internal_generation_mu"] / monthly["consumption_mu"]
    if {"hydel_total_mu", "consumption_mu"}.issubset(monthly.columns):
        monthly["hydro_share_consumption"] = monthly["hydel_total_mu"] / monthly["consumption_mu"]

    duration = work[["date", "import_share"]].dropna().sort_values("import_share", ascending=False)
    duration = duration.reset_index(drop=True)
    duration["rank"] = duration.index + 1
    duration["date"] = duration["date"].dt.strftime("%Y-%m-%d")
    return daily.to_dict("records"), monthly.to_dict("records"), duration.to_dict("records")


def _grid_india_product(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    frame = pd.read_parquet(path)
    if frame.empty:
        return None
    columns = [
        c
        for c in [
            "date",
            "peak_demand_met_mw",
            "peak_shortage_mw",
            "energy_met_mu",
            "drawal_schedule_mu",
            "od_ud_mu",
            "max_od_ud_mw",
            "energy_shortage_mu",
        ]
        if c in frame.columns
    ]
    work = frame[columns].copy()
    if "date" in work.columns:
        work["date"] = pd.to_datetime(work["date"]).dt.strftime("%Y-%m-%d")
    return {
        "classification": "official_independent_cross_check",
        "source": "Grid-India Daily PSP MOP_E",
        "records": work.to_dict("records"),
    }


def _source_audit_summary(payload: dict[str, Any] | None) -> dict[str, int]:
    if not payload:
        return {}
    sources = payload.get("sources", {})
    counts: dict[str, int] = {}
    for entry in sources.values():
        status = str(entry.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("public"))
    args = parser.parse_args()

    root = args.root.resolve()
    out = (root / args.output).resolve() if not args.output.is_absolute() else args.output
    scenarios_cfg = _load_yaml(root / "configs/scenarios_2040.yaml")
    references_cfg = _load_yaml(root / "configs/published_2040_references.yaml")
    sources_cfg = _load_yaml(root / "configs/sources.yaml")
    observed_cfg = _load_yaml(root / "configs/observed_2024_25.yaml")
    cea_cfg = _load_yaml(root / "configs/cea_resource_adequacy_2025.yaml")
    circular_cfg = _load_yaml(root / "configs/circular_industry_references.yaml")
    non_electric_cfg = _load_yaml(root / "configs/non_electric_energy_references.yaml")
    ogd_cfg = _load_yaml(root / "configs/ogd_targets.yaml")
    ecology_cfg = _load_yaml(root / "configs/ecology_constraints.yaml")

    summary_path = root / "results/baseline/summary.json"
    summary = _load_json(summary_path)
    daily_frame = _load_daily(root)
    storage_path = root / "data/processed/sldc_storage_daily.parquet"
    weather_files = sorted((root / "data/processed").glob("*weather*.parquet")) + sorted(
        (root / "data/processed").glob("*nasa*.parquet")
    )
    era5_manifest = _load_json(root / "data/processed/era5_daily_manifest.json")
    grid_india = _grid_india_product(root / "data/processed/grid_india_psp.parquet")
    kseb_projects = _load_json(root / "data/processed/kseb_pms_projects.json")
    hazard_catalog = _load_json(root / "data/processed/ksdma_hazard_manifest.json")
    source_audit = _load_json(root / "results/source_audit.json")

    if (
        daily_frame is not None
        and storage_path.exists()
        and "storage_pct_energy_weighted" not in daily_frame.columns
    ):
        storage = pd.read_parquet(storage_path).copy()
        storage["date"] = pd.to_datetime(storage["date"]).dt.normalize()
        daily_frame["date"] = pd.to_datetime(daily_frame["date"]).dt.normalize()
        keep = [c for c in ["date", "storage_pct_energy_weighted"] if c in storage.columns]
        if len(keep) > 1:
            daily_frame = daily_frame.merge(storage[keep], on="date", how="left")

    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    git_sha = os.getenv("GITHUB_SHA") or os.getenv("GIT_COMMIT")
    scenarios = _scenario_payload(scenarios_cfg)

    hazard_count = len((hazard_catalog or {}).get("records", []))
    project_count = len((kseb_projects or {}).get("projects", []))
    grid_records = len((grid_india or {}).get("records", []))

    status = {
        "official_observed_2024_25": {
            "available": bool(observed_cfg),
            "evidence": "sourced observed",
            "note": "Kerala Economic Review 2025 / KSEBL annual FY2024-25 reference values.",
        },
        "sldc_daily": {
            "available": daily_frame is not None,
            "evidence": "measured",
            "note": "Kerala SLDC daily system accounting.",
        },
        "baseline_summary": {
            "available": summary is not None,
            "evidence": "derived",
            "note": "Derived only after historical calibration checks.",
        },
        "reservoir_storage": {
            "available": storage_path.exists(),
            "evidence": "measured",
            "note": "Kerala SLDC reservoir-storage chronology.",
        },
        "weather": {
            "available": bool(weather_files),
            "evidence": "measured/reanalysis",
            "note": "NASA POWER representative-point hourly weather.",
        },
        "era5_reanalysis": {
            "available": era5_manifest is not None,
            "evidence": "reanalysis",
            "note": "Copernicus ERA5 Kerala-domain daily climate manifest.",
        },
        "grid_india_psp": {
            "available": grid_records > 0,
            "evidence": "official cross-check",
            "note": (
                f"{grid_records} official state-day records available."
                if grid_records
                else "Current API integration is configured; processed FY2024-25 rows not in this bundle yet."
            ),
        },
        "kseb_project_inventory": {
            "available": project_count > 0,
            "evidence": "official project portal",
            "note": (
                f"{project_count} project records parsed from KSEB PMS."
                if project_count
                else "KSEB PMS parser configured; current project inventory not in this bundle yet."
            ),
        },
        "hazard_layers": {
            "available": hazard_count > 0,
            "evidence": "official GIS catalog",
            "note": (
                f"{hazard_count} KSDMA hazard download links catalogued."
                if hazard_count
                else "KSDMA hazard-layer manifest not in this bundle yet."
            ),
        },
        "hourly_state_load": {
            "available": False,
            "evidence": "gap",
            "note": "No authenticated FY2024-25 Kerala 8760/35040 state-load chronology is published in this bundle.",
        },
    }

    metadata = {
        "project": "Kerala 2040 — Open Energy Intelligence",
        "generated_at_utc": generated_at,
        "research_repo": "https://github.com/abhijith-sivaprasadan/kerala2040",
        "web_repo": "https://github.com/kerala2040/kerala2040.github.io",
        "git_sha": git_sha,
        "model_year": scenarios_cfg.get("model_year", 2040),
        "principle": scenarios_cfg.get("principle"),
        "status": status,
        "source_audit_summary": _source_audit_summary(source_audit),
        "files": {},
    }

    _write(
        out / "scenarios.json",
        {
            "scenarios": scenarios,
            "stress_tests": scenarios_cfg.get("stress_tests", {}),
            "rules": scenarios_cfg.get("rules", []),
        },
    )
    _write(out / "published-references.json", references_cfg)
    _write(out / "sources.json", sources_cfg)
    _write(out / "observed-reference.json", observed_cfg)
    _write(out / "cea-resource-adequacy.json", cea_cfg)
    _write(out / "circular-industry.json", circular_cfg)
    _write(out / "non-electric-energy.json", non_electric_cfg)
    _write(out / "ogd-targets.json", ogd_cfg)
    _write(out / "ecology-constraints.json", ecology_cfg)
    metadata["files"].update(
        {
            "scenarios": "scenarios.json",
            "published_references": "published-references.json",
            "sources": "sources.json",
            "observed_reference": "observed-reference.json",
            "cea_resource_adequacy": "cea-resource-adequacy.json",
            "circular_industry": "circular-industry.json",
            "non_electric_energy": "non-electric-energy.json",
            "ogd_targets": "ogd-targets.json",
            "ecology_constraints": "ecology-constraints.json",
        }
    )

    if summary is not None:
        _write(out / "baseline-summary.json", summary)
        metadata["files"]["baseline_summary"] = "baseline-summary.json"

    if daily_frame is not None:
        daily, monthly, duration = _daily_products(daily_frame)
        _write(
            out / "daily-balance.json",
            {"unit": "MU/day", "evidence": "measured/derived", "records": daily},
        )
        _write(
            out / "monthly-balance.json",
            {"unit": "MU/month", "evidence": "measured/derived", "records": monthly},
        )
        _write(
            out / "import-duration.json",
            {"evidence": "derived from measured daily balance", "records": duration},
        )
        metadata["files"].update(
            {
                "daily_balance": "daily-balance.json",
                "monthly_balance": "monthly-balance.json",
                "import_duration": "import-duration.json",
            }
        )

    if grid_india:
        _write(out / "grid-india-daily.json", grid_india)
        metadata["files"]["grid_india_daily"] = "grid-india-daily.json"

    if kseb_projects:
        _write(out / "kseb-projects.json", kseb_projects)
        metadata["files"]["kseb_projects"] = "kseb-projects.json"

    if hazard_catalog:
        _write(out / "hazard-catalog.json", hazard_catalog)
        metadata["files"]["hazard_catalog"] = "hazard-catalog.json"

    if source_audit:
        _write(out / "source-audit.json", source_audit)
        metadata["files"]["source_audit"] = "source-audit.json"

    if era5_manifest:
        _write(out / "era5-daily-manifest.json", era5_manifest)
        metadata["files"]["era5_daily_manifest"] = "era5-daily-manifest.json"

    screening_nodes = [
        {
            "name": "Kochi industrial-demand hub",
            "lat": 9.9312,
            "lon": 76.2673,
            "kind": "grid",
            "note": "Demand, industry, port and flexibility screening node.",
        },
        {
            "name": "Idukki hydro-storage system",
            "lat": 9.85,
            "lon": 76.97,
            "kind": "storage",
            "note": "Hydro flexibility, reservoir and pumped-storage screening area.",
        },
        {
            "name": "Ramakkalmedu wind area",
            "lat": 9.79,
            "lon": 77.16,
            "kind": "wind",
            "note": "Wind-resource screening area; ecology and grid constraints required.",
        },
        {
            "name": "Chavara circular-industry cluster",
            "lat": 9.0,
            "lon": 76.53,
            "kind": "circular",
            "note": "Mineral-sands, TiO2 and by-product recovery research cluster.",
        },
        {
            "name": "Vizhinjam coastal-energy node",
            "lat": 8.38,
            "lon": 76.98,
            "kind": "marine",
            "note": "Port, wave-energy history, shore-power and marine-resource screening node.",
        },
    ]
    _write(
        out / "screening-nodes.json",
        {"classification": "research screening; not siting approval", "records": screening_nodes},
    )
    metadata["files"]["screening_nodes"] = "screening-nodes.json"
    _write(out / "metadata.json", metadata)

    site_manifest = {
        "metadata": metadata,
        "observed": observed_cfg,
        "cea_resource_adequacy": cea_cfg,
        "circular_industry": circular_cfg,
        "non_electric_energy": non_electric_cfg,
        "ogd_targets": ogd_cfg,
        "ecology_constraints": ecology_cfg,
        "baseline": summary,
        "scenarios": scenarios,
        "stress_tests": scenarios_cfg.get("stress_tests", {}),
        "references": references_cfg.get("references", {}),
        "sources": sources_cfg.get("sources", {}),
        "source_audit": source_audit,
        "kseb_projects": kseb_projects,
        "hazard_catalog": hazard_catalog,
        "era5": era5_manifest,
        "screening_nodes": screening_nodes,
    }
    _write(out / "site-data.json", site_manifest)
    print(
        json.dumps(
            {"output": str(out), "files": sorted(p.name for p in out.glob("*.json"))},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
