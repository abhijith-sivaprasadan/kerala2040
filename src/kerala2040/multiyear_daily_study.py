"""Private-source multi-year observed Kerala SLDC daily demand admission.

The dataset contains source-recorded DAILY energy, not hourly loads. Never
publish the source-derived row-level table from this private archive without
separately reviewing source redistribution permissions.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from kerala2040.daily_demand_ml import (
    CALENDAR_FEATURES,
    FEATURES,
    build_daily_feature_table,
    regression_metrics,
)


def read_private_daily_source(archive: Path, manifest_path: Path) -> tuple[pd.DataFrame, dict]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entry = next(
        (r for r in manifest["files"] if r["name"] == "daily_system.csv.gz"), None
    )
    if not entry:
        raise ValueError("Verified private archive manifest lacks daily_system.csv.gz")
    compressed = archive.read_bytes()
    digest = hashlib.sha256(compressed).hexdigest()
    if digest != entry["sha256"]:
        raise ValueError("Original private compressed source digest mismatch")
    raw = gzip.decompress(compressed)
    if hashlib.sha256(raw).hexdigest() != entry["original_sha256"]:
        raise ValueError("Decompressed original table digest mismatch")
    source = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if len(source) != 2606:
        raise ValueError("Expected 2,606 dated original archive rows")
    dates = [r["date"] for r in source]
    if len(set(dates)) != len(dates) or dates != sorted(dates):
        raise ValueError("Missing ordering or duplicate source dates")
    accepted = []
    for row in source:
        value = row.get("consumption_qualified_mu", "").strip()
        if value:
            if row.get("energy_balance_qualified") != "True":
                raise ValueError("Unqualified source value cannot enter model target")
            amount = float(value)
            if not np.isfinite(amount) or amount <= 0:
                raise ValueError("Invalid observed daily consumption")
            accepted.append({"date": row["date"], "consumption_mu": amount})
    if len(accepted) < 2000:
        raise ValueError("Insufficient qualified source observations")
    frame = pd.DataFrame(accepted)
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    return frame, {
        "private_source_gzip_sha256": digest,
        "original_csv_sha256": hashlib.sha256(raw).hexdigest(),
        "qualified_rows": len(accepted),
        "calendar_rows": len(source),
        "source_scope": "SLDC reported and balance-qualified daily consumption MU",
    }


def fixed_fiscal_year_design(table: pd.DataFrame) -> list[dict]:
    """Expanding strictly-past training; retrospective, NOT pristine holdout."""
    result = []
    dates = pd.to_datetime(table["date"])
    if dates.duplicated().any():
        raise ValueError("Duplicate observed dates")
    for fy in (2022, 2023, 2024):
        start = pd.Timestamp(year=fy, month=4, day=1)
        stop = pd.Timestamp(year=fy + 1, month=4, day=1)
        beginning = pd.Timestamp("2020-04-01")
        train = table.loc[(dates >= beginning) & (dates < start)]
        test = table.loc[(dates >= start) & (dates < stop)]
        if len(train) < 650 or len(test) < 300:
            raise ValueError(f"Insufficient independent daily years at {fy}-{fy+1}")
        if train["date"].max() >= test["date"].min():
            raise ValueError("Leakage into later fiscal-year holdout")
        result.append({
            "fiscal_year": f"{fy}-{str(fy+1)[-2:]}",
            "train": train,
            "test": test,
        })
    return result


def evaluate_multiyear_daily_weather(observed: pd.DataFrame, weather: pd.DataFrame) -> dict:
    features = build_daily_feature_table(observed, weather)
    # Reject partial weather source coverage, including early and late years.
    if set(features["date"]) != set(observed["date"]):
        raise ValueError("Matched SLDC observations lack complete ERA5 daily features")
    folds = fixed_fiscal_year_design(features)
    records = []
    for fold in folds:
        row = {"fiscal_year": fold["fiscal_year"], "train_days": len(fold["train"]),
               "heldout_days": len(fold["test"])}
        for name, cols in (("calendar", CALENDAR_FEATURES), ("calendar_weather", FEATURES)):
            model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
            model.fit(fold["train"][cols], fold["train"]["consumption_mu"])
            pred = model.predict(fold["test"][cols])
            row[name] = regression_metrics(
                fold["test"]["consumption_mu"].to_numpy(), pred
            )
        baseline = row["calendar"]["rmse_mu"]
        row["weather_rmse_change_pct"] = (
            100.0 * (baseline - row["calendar_weather"]["rmse_mu"]) / baseline
        )
        records.append(row)
    return {
        "status": "RETROSPECTIVE_MULTIFISCAL_YEAR_RIDGE_COMPARISON",
        "folds": records,
        "weather_data_source_required": "independently pinned exact original ERA5 hours",
        "method": "Fixed Ridge alpha=1, scaled features, past-only training, 3 FY heldouts",
        "caveat": "2024 data were previously inspected; this is not a blind holdout, "
                  "a causal association, or a day-ahead forecast",
    }
