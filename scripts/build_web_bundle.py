#!/usr/bin/env python
"""Build the public Kerala 2040 web-data bundle from configs and processed evidence.

The bundle never fabricates missing observations. Files that are unavailable are reported
explicitly in metadata and omitted from data products.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from kerala2040.analysis import add_daily_indicators


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, pd.Timestamp):
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


def _daily_products(data: pd.DataFrame) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
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

    summary_path = root / "results/baseline/summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else None
    daily_frame = _load_daily(root)
    storage_path = root / "data/processed/sldc_storage_daily.parquet"
    weather_files = sorted((root / "data/processed").glob("*weather*.parquet")) + sorted(
        (root / "data/processed").glob("*nasa*.parquet")
    )

    if daily_frame is not None and storage_path.exists() and "storage_pct_energy_weighted" not in daily_frame.columns:
        storage = pd.read_parquet(storage_path).copy()
        storage["date"] = pd.to_datetime(storage["date"]).dt.normalize()
        daily_frame["date"] = pd.to_datetime(daily_frame["date"]).dt.normalize()
        keep = [c for c in ["date", "storage_pct_energy_weighted"] if c in storage.columns]
        if len(keep) > 1:
            daily_frame = daily_frame.merge(storage[keep], on="date", how="left")

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    git_sha = os.getenv("GITHUB_SHA") or os.getenv("GIT_COMMIT")
    scenarios = _scenario_payload(scenarios_cfg)

    status = {
        "sldc_daily": {"available": daily_frame is not None, "evidence": "measured"},
        "baseline_summary": {"available": summary is not None, "evidence": "derived"},
        "reservoir_storage": {"available": storage_path.exists(), "evidence": "measured"},
        "weather": {"available": bool(weather_files), "evidence": "measured/reanalysis"},
        "hourly_state_load": {
            "available": False,
            "evidence": "gap",
            "note": "No authenticated FY2024-25 Kerala 8760/35040 load chronology is published in this bundle.",
        },
        "grid_india_psp": {
            "available": False,
            "evidence": "cross-check source",
            "note": "Integration remains non-blocking because upstream access has been unreliable.",
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
        "files": {},
    }

    _write(out / "scenarios.json", {"scenarios": scenarios, "stress_tests": scenarios_cfg.get("stress_tests", {}), "rules": scenarios_cfg.get("rules", [])})
    _write(out / "published-references.json", references_cfg)
    _write(out / "sources.json", sources_cfg)
    metadata["files"].update(
        {
            "scenarios": "scenarios.json",
            "published_references": "published-references.json",
            "sources": "sources.json",
        }
    )

    if summary is not None:
        _write(out / "baseline-summary.json", summary)
        metadata["files"]["baseline_summary"] = "baseline-summary.json"

    if daily_frame is not None:
        daily, monthly, duration = _daily_products(daily_frame)
        _write(out / "daily-balance.json", {"unit": "MU/day", "evidence": "measured/derived", "records": daily})
        _write(out / "monthly-balance.json", {"unit": "MU/month", "evidence": "measured/derived", "records": monthly})
        _write(out / "import-duration.json", {"evidence": "derived from measured daily balance", "records": duration})
        metadata["files"].update(
            {
                "daily_balance": "daily-balance.json",
                "monthly_balance": "monthly-balance.json",
                "import_duration": "import-duration.json",
            }
        )

    screening_nodes = [
        {"name": "Kochi industrial-demand hub", "lat": 9.9312, "lon": 76.2673, "kind": "grid", "note": "Demand, industry, port and flexibility screening node."},
        {"name": "Idukki hydro-storage system", "lat": 9.85, "lon": 76.97, "kind": "storage", "note": "Hydro flexibility, reservoir and pumped-storage screening area."},
        {"name": "Ramakkalmedu wind area", "lat": 9.79, "lon": 77.16, "kind": "wind", "note": "Wind-resource screening area; ecology and grid constraints required."},
        {"name": "Chavara circular-industry cluster", "lat": 9.0, "lon": 76.53, "kind": "circular", "note": "Mineral-sands, TiO2 and by-product recovery research cluster."},
        {"name": "Vizhinjam coastal-energy node", "lat": 8.38, "lon": 76.98, "kind": "marine", "note": "Port, wave-energy history, shore-power and marine-resource screening node."},
    ]
    _write(out / "screening-nodes.json", {"classification": "research screening; not siting approval", "records": screening_nodes})
    metadata["files"]["screening_nodes"] = "screening-nodes.json"
    _write(out / "metadata.json", metadata)

    site_manifest = {
        "metadata": metadata,
        "baseline": summary,
        "scenarios": scenarios,
        "stress_tests": scenarios_cfg.get("stress_tests", {}),
        "references": references_cfg.get("references", {}),
        "sources": sources_cfg.get("sources", {}),
        "screening_nodes": screening_nodes,
    }
    _write(out / "site-data.json", site_manifest)
    print(json.dumps({"output": str(out), "files": sorted(p.name for p in out.glob("*.json"))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
