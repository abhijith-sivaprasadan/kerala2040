#!/usr/bin/env python3
"""Kerala2040 phase 4: offline Idukki source-observation hydro-energy pilot.

Uses locally curated SLDC date-labelled data; no internet, gap filling, hourly
inferences, inferred discharge/spill, or made-up 2018 electricity.

Run: python analysis/idukki_hydro_energy_phase4.py --curated PRIVATE_DIR --out PRIVATE_DIR
Optional: --weather-daily independently prepared, single-basin IST date CSV with
    date,rainfall_mm,source_id,spatial_support,precipitation_processing
External weather is kept separate and never used unless supplied and checked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler

FIRST = "2019-08-06"
LAST = "2026-09-23"
RESERVOIR = "IDUKKI"
STATION = "Idukki"
LAG_DAYS = tuple(range(0, 8))
SOURCE_FILES = ("daily_system.csv", "reservoir_rows.csv", "generation_rows.csv", "source_calendar.csv")
EVENTS = (
    ("2018 flood benchmark (no SLDC sample)", "2018-08-08", "2018-08-20", "multi-basin"),
    ("August 2019 flood review", "2019-08-08", "2019-08-14", "north/central Kerala"),
    ("Pettimudi 2020 landslide", "2020-08-06", "2020-08-11", "Idukki district"),
    ("October 2021 floods", "2021-10-15", "2021-10-20", "central/southern Kerala"),
    ("Wayanad 2024 landslide", "2024-07-29", "2024-08-04", "Wayanad district"),
    ("Nilambur 2026 flash flood", "2026-09-20", "2026-09-22", "Malappuram district"),
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def calendar_join(curated: Path) -> tuple[pd.DataFrame, dict[str, str]]:
    paths = {name: curated / name for name in SOURCE_FILES}
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(f"Missing original curated file: {path}")
    source_hashes = {name: sha256(path) for name, path in paths.items()}
    day = pd.read_csv(paths["daily_system.csv"], parse_dates=["date"], low_memory=False)
    res = pd.read_csv(paths["reservoir_rows.csv"], parse_dates=["date"], low_memory=False)
    gen = pd.read_csv(paths["generation_rows.csv"], parse_dates=["date"], low_memory=False)
    cal = pd.read_csv(paths["source_calendar.csv"], parse_dates=["date"], low_memory=False)
    dates = pd.date_range(FIRST, LAST, freq="D")
    if len(day) != len(dates) or day.date.duplicated().any():
        raise ValueError("Daily SLDC calendar is incomplete or duplicate")
    if not day.date.sort_values().reset_index(drop=True).equals(pd.Series(dates)):
        raise ValueError("Daily SLDC calendar date identity failed")
    if "date" not in cal or cal.date.nunique() != len(dates):
        raise ValueError("Source calendar incomplete or duplicate")
    idukki = res.loc[res.reservoir.astype(str).str.upper().eq(RESERVOIR)].copy()
    if idukki.date.duplicated().any():
        raise ValueError("Ambiguous Idukki reservoir rows")
    power = gen.loc[gen.source_label.astype(str).str.casefold().eq(STATION.casefold())
                    & gen.row_class.astype(str).eq("source_station_or_other")].copy()
    if power.date.duplicated().any():
        raise ValueError("Ambiguous Idukki station output rows")
    cols = ["date", "rainfall_mm", "inflow_mcm_day", "storage_pct",
            "effective_storage_mcm", "level_m", "full_storage_mcm", "source_sha256"]
    i = idukki[cols].rename(columns={"source_sha256": "idukki_reservoir_source_sha256"})
    g = power[["date", "day_mu", "source_sha256"]].rename(
        columns={"day_mu": "idukki_station_generation_mu", "source_sha256": "idukki_station_source_sha256"})
    merged = day.merge(i, on="date", how="left", validate="one_to_one")
    merged = merged.merge(g, on="date", how="left", validate="one_to_one")
    for col in ["rainfall_mm", "inflow_mcm_day", "storage_pct",
                "effective_storage_mcm", "level_m", "full_storage_mcm",
                "idukki_station_generation_mu", "hydel_total_mu",
                "net_import_interface_mu", "consumption_qualified_mu"]:
        merged[col] = pd.to_numeric(merged[col], errors="coerce")
    if merged.date.duplicated().any() or len(merged) != len(dates):
        raise ValueError("Join changed date population")
    # Sanity bounds are for model inclusion; raw source numbers remain untouched.
    merged["rainfall_valid"] = merged.rainfall_mm.ge(0) & merged.rainfall_mm.le(750)
    merged["inflow_valid"] = merged.inflow_mcm_day.ge(0) & merged.inflow_mcm_day.le(300)
    merged["storage_valid"] = (merged.storage_pct.between(0, 100) &
                               merged.effective_storage_mcm.ge(0) &
                               merged.effective_storage_mcm.le(merged.full_storage_mcm))
    merged["station_generation_valid"] = merged.idukki_station_generation_mu.ge(0)
    for col, flag in [("rainfall_mm", "rainfall_valid"),
                      ("inflow_mcm_day", "inflow_valid"),
                      ("effective_storage_mcm", "storage_valid"),
                      ("idukki_station_generation_mu", "station_generation_valid")]:
        merged[col + "_analysis"] = merged[col].where(merged[flag])
    merged = merged.set_index("date", verify_integrity=True).asfreq("D")
    for lag in LAG_DAYS:
        merged[f"rain_lag{lag}_mm"] = merged.rainfall_mm_analysis.shift(lag)
    for n in (3, 7, 14, 30):
        merged[f"rain_rolling{n}_mm"] = merged.rainfall_mm_analysis.rolling(
            n, min_periods=n).sum()
    merged["inflow_lag1_mcm_day"] = merged.inflow_mcm_day_analysis.shift(1)
    merged["storage_lag1_mcm"] = merged.effective_storage_mcm_analysis.shift(1)
    merged["delta_storage_mcm"] = merged.effective_storage_mcm_analysis.diff()
    merged["net_depletion_residual_mcm"] = (
        merged.inflow_mcm_day_analysis - merged.delta_storage_mcm
    )
    # WARNING: residual includes all water balance terms, diversions, nonphysical source
    # changes and measurement errors. NOT measured spill, releases or flood operations.
    return merged.reset_index(), source_hashes


def optional_weather(d: pd.DataFrame, weather_path: Path | None):
    if weather_path is None:
        return d, {"provided": False, "included_days": 0}
    w = pd.read_csv(weather_path, parse_dates=["date"])
    required = {"date", "rainfall_mm", "source_id", "spatial_support", "precipitation_processing"}
    if not required.issubset(w):
        raise ValueError(f"Weather source missing columns: {sorted(required - set(w))}")
    if w.date.isna().any() or w.date.duplicated().any() or w.date.dt.tz is not None:
        raise ValueError("Weather dates must be unique IST-local calendar dates")
    if w.rainfall_mm.notna().any() and ((pd.to_numeric(w.rainfall_mm, errors="coerce") < 0).any()):
        raise ValueError("Negative external rainfall")
    for c in ("source_id", "spatial_support", "precipitation_processing"):
        if w[c].isna().any() or w[c].astype(str).str.strip().eq("").any():
            raise ValueError(f"Weather rows need explicit {c} provenance")
    if not w.precipitation_processing.str.contains("deaccumul|hourly_increment", case=False).all():
        raise ValueError("Weather precipitation must document deaccumulation before IST aggregation")
    out = d.merge(w[["date", "rainfall_mm"]].rename(
        columns={"rainfall_mm": "weather_basin_rainfall_mm"}),
        on="date", how="left", validate="one_to_one")
    return out, {"provided": True, "included_days": int(out.weather_basin_rainfall_mm.count()),
                 "file_sha256": sha256(weather_path),
                 "provenance_categories": w[["source_id", "spatial_support", "precipitation_processing"]]
                 .drop_duplicates().to_dict("records")}


def paired_correlation(frame: pd.DataFrame, x: str, y: str, min_n: int = 25):
    d = frame[["date", x, y]].replace([np.inf, -np.inf], np.nan).dropna()
    out = {"paired_days": int(len(d)), "pearson_r": None, "year_month_demeaned_r": None}
    if len(d) < min_n or d[x].nunique() < 2 or d[y].nunique() < 2:
        return out
    out["pearson_r"] = round(float(d[x].corr(d[y])), 5)
    ym = d.date.dt.to_period("M")
    xx = d[x] - d.groupby(ym)[x].transform("mean")
    yy = d[y] - d.groupby(ym)[y].transform("mean")
    if xx.std() > 0 and yy.std() > 0:
        out["year_month_demeaned_r"] = round(float(xx.corr(yy)), 5)
    return out


def blocked_inflow_model(d: pd.DataFrame):
    # Retrospective one-day diagnostic: rain at t is observed, not a forecast.
    # Complete 8-day rainfall and previous-day inflow are required; gaps remain gaps.
    features = [f"rain_lag{n}_mm" for n in LAG_DAYS] + ["inflow_lag1_mcm_day"]
    f = d[["date", "inflow_mcm_day_analysis", *features]].dropna().copy()
    f = f[f.inflow_mcm_day_analysis.le(300)]
    train = f[f.date.lt("2025-01-01")]
    test = f[f.date.ge("2025-01-01")]
    result = {"features": features, "train_period": f"{FIRST} to 2024-12-31",
              "test_period": "2025-01-01 to 2026-09-23",
              "complete_case_train_days": int(len(train)),
              "complete_case_test_days": int(len(test)),
              "weather_observed_same_day": True, "model": "standardized_ridge_alpha10",
              "baseline": "previous_observed_day_inflow_exact_day"}
    if len(train) < 100 or len(test) < 50:
        return {**result, "status": "insufficient_complete_cases", "skill": None}
    scaler = StandardScaler().fit(train[features])
    model = Ridge(alpha=10.0).fit(scaler.transform(train[features]), train.inflow_mcm_day_analysis)
    prediction = np.maximum(0, model.predict(scaler.transform(test[features])))
    y = test.inflow_mcm_day_analysis.to_numpy()
    baseline = test.inflow_lag1_mcm_day.to_numpy()
    def scores(p):
        return {"mae_mcm_day": round(float(mean_absolute_error(y, p)), 4),
                "rmse_mcm_day": round(float(np.sqrt(mean_squared_error(y, p))), 4)}
    return {**result, "status": "complete_case_holdout_scored", "skill": {
        "ridge": scores(prediction), "persistence": scores(baseline),
        "mae_improvement_percent_vs_persistence": round(
            100 * (1 - mean_absolute_error(y, prediction) / mean_absolute_error(y, baseline)), 2)
        if mean_absolute_error(y, baseline) else None,
    }, "test_coverage_limitation": "Only source-dated days with complete 8-day gauge rain history and previous-day inflow; not population-representative"}


def event_review(d: pd.DataFrame):
    out = []
    for label, start, end, region in EVENTS:
        window = d[d.date.between(start, end)]
        year = start[:4]
        # Matched *within year and ±45d* control, exclude windows from all years.
        pre = pd.Timestamp(start) - pd.Timedelta(days=45)
        post = pd.Timestamp(end) + pd.Timedelta(days=45)
        controls = d[d.date.between(pre, post) & ~d.date.between(start, end)].copy()
        # This is only a seasonal nearby-day comparator; no matched weather/outage controls.
        measures = ["rainfall_mm_analysis", "inflow_mcm_day_analysis",
                    "effective_storage_mcm_analysis", "idukki_station_generation_mu_analysis",
                    "hydel_total_mu", "net_import_interface_mu", "consumption_qualified_mu"]
        row = {"event": label, "start": start, "end": end, "region": region,
               "source_sample_days": int(len(window)),
               "reference_days_in_45day_flanks": int(len(controls)),
               "not_causal": True}
        for c in measures:
            row[c] = {"event_n": int(window[c].count()),
                      "event_mean": round(float(window[c].mean()), 4) if window[c].count() else None,
                      "reference_n": int(controls[c].count()),
                      "reference_mean": round(float(controls[c].mean()), 4) if controls[c].count() else None}
        out.append(row)
    return out


def water_energy_sensitivity(*, head_m: float = 500, volume_mcm: float = 1,
                             eta_gen: float = .9, eta_pump: float = .85):
    """Illustrative ONLY, not a Kerala PSP site or a hydrological entitlement."""
    if not (0 < head_m <= 1500 and 0 < volume_mcm <= 10000
            and 0 < eta_gen <= 1 and 0 < eta_pump <= 1):
        raise ValueError("Invalid illustrative scenario")
    theoretical_gwh = 1000 * 9.81 * head_m * volume_mcm * 1e6 / 3.6e12
    return {"classification": "illustrative_physics_NOT_project_feasibility",
            "head_m_assumed": head_m, "transfer_volume_mcm_assumed": volume_mcm,
            "generation_efficiency_assumed": eta_gen, "pump_efficiency_assumed": eta_pump,
            "gross_gwh": round(theoretical_gwh, 5),
            "generated_gwh": round(theoretical_gwh * eta_gen, 5),
            "pumping_input_gwh": round(theoretical_gwh / eta_pump, 5),
            "round_trip_efficiency_assumed": round(eta_gen * eta_pump, 5),
            "no_verified_site_or_flood_operating_headroom": True}


def run(curated: Path, output: Path, weather: Path | None = None):
    output.mkdir(parents=True, exist_ok=True)
    d, hashes = calendar_join(curated)
    d, weather_status = optional_weather(d, weather)
    lag_r = {f"lag_{n}_days": paired_correlation(
        d, f"rain_lag{n}_mm", "inflow_mcm_day_analysis") for n in LAG_DAYS}
    gen_relation = {}
    for a in ["rainfall_mm_analysis", "inflow_mcm_day_analysis",
              "effective_storage_mcm_analysis"]:
        gen_relation[a] = paired_correlation(d, a, "idukki_station_generation_mu_analysis")
    skill = blocked_inflow_model(d)
    events = event_review(d)
    monthly = (d.assign(month=d.date.dt.strftime("%Y-%m"))
               .groupby("month", as_index=False)
               .agg(idukki_rain_reported_days=("rainfall_mm_analysis", "count"),
                    idukki_rain_mm_mean_on_reported_days=("rainfall_mm_analysis", "mean"),
                    idukki_inflow_reported_days=("inflow_mcm_day_analysis", "count"),
                    idukki_inflow_mcm_day_mean_on_reported_days=("inflow_mcm_day_analysis", "mean"),
                    idukki_station_generation_reported_days=("idukki_station_generation_mu_analysis", "count"),
                    idukki_station_generation_mu_day_mean_on_reported_days=("idukki_station_generation_mu_analysis", "mean"),
                    idukki_storage_reported_days=("effective_storage_mcm_analysis", "count"),
                    idukki_storage_mcm_median_on_reported_days=("effective_storage_mcm_analysis", "median")))
    monthly.to_csv(output / "idukki_phase4_monthly_observed_aggregate.csv", index=False)
    review = {"classification": "SOURCE_SLDC_IDUKKI_HYDRO_ENERGY_PILOT_NOT_CAUSAL_OR_PSP_FEASIBILITY",
       "archive_scope": {"start": FIRST, "end": LAST, "slots": len(d),
            "source_files_sha256": hashes},
       "populations": {"idukki_rain_days": int(d.rainfall_mm_analysis.count()),
                       "idukki_inflow_days": int(d.inflow_mcm_day_analysis.count()),
                       "idukki_station_generation_days": int(d.idukki_station_generation_mu_analysis.count()),
                       "idukki_storage_volume_days": int(d.effective_storage_mcm_analysis.count()),
                       "negative_inflow_reported_count": int(d.inflow_mcm_day.lt(0).sum()),
                       "outside_storage_bounds_count": int((d.storage_pct.gt(100) | d.storage_pct.lt(0)).sum()),
                       "net_depletion_residual_days": int(d.net_depletion_residual_mcm.count())},
       "rainfall_inflow_lags": lag_r,
       "station_generation_associations": gen_relation,
       "inflow_holdout_model": skill,
       "event_window_descriptive_comparisons": events,
       "weather": weather_status,
       "atlas_observed_rows_integrated": 0,
       "2018_sldc_daily_rows": 0,
       "psp": water_energy_sensitivity(),
       "limit": ["Idukki gauge is not spatially integrated basin rainfall",
                 "rainfall is available on selected report dates; complete-case models have selection bias",
                 "rain t is observed retrospectively; no live inflow prediction claim",
                 "daily station energy cannot recover turbine head or turbine releases",
                 "inflow minus storage change is a net-depletion RESIDUAL, not observed spill or releases",
                 "local event flags are not basin flood footprints or causal estimates",
                 "the 2018 event has no dates inside collected SLDC archive",
                 "no extracted ERA5 basin series, Energy Atlas metered data, or PSP project constraints supplied"]}
    (output / "idukki_phase4_private_daily.csv").write_text(d.to_csv(index=False), encoding="utf-8")
    (output / "idukki_phase4_public_qa.json").write_text(
        json.dumps(review, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"slots":len(d), "rain_days": review["populations"]["idukki_rain_days"],
        "station_days": review["populations"]["idukki_station_generation_days"],
        "holdout": skill["status"], "n_test": skill["complete_case_test_days"],
        "weather_days": weather_status["included_days"],
        "out":str(output)}, indent=2))
    return review


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--curated", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--weather-daily", type=Path)
    args = p.parse_args()
    run(args.curated, args.out, args.weather_daily)


if __name__ == "__main__":
    main()
