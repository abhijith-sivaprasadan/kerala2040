"""Five-site FY2024-25 ERA5 wind/PV sensitivity *PROXIES*, NOT model admitted.

Input: 20 source-QA-passed GitHub ERA5 artifact ZIPs:
era5_<site>_q{2,3,4,1}.zip; and NWIC-Kerala NIWE/GSA source clips.
Run with --era5-dir, --clip-dir, --out. Requires h5py and standard geo stack.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import rasterio

SITES = ("kannur", "kozhikode", "kochi", "palakkad", "thiruvananthapuram")
COORDS = {
    "kannur": (75.3704, 11.8745),
    "kozhikode": (75.7804, 11.2588),
    "kochi": (76.2673, 9.9312),
    "palakkad": (76.6548, 10.7867),
    "thiruvananthapuram": (76.9366, 8.5241),
}
# Illustrative sensitivities. NOT fitted to Kerala PV or turbine measurements.
ALPHA = 0.14
HUB_M = 150.0
PR = 0.82
GAMMA = -0.004
CELL_RISE = 0.025
CUT_IN, RATED, CUT_OUT = 3.0, 12.0, 25.0


def sha(path: Path) -> str:
    d = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(2**20), b""):
            d.update(block)
    return d.hexdigest()


def turbine_proxy(speed: np.ndarray) -> np.ndarray:
    out = np.zeros_like(speed, dtype="float64")
    partial = (speed >= CUT_IN) & (speed < RATED)
    out[partial] = (speed[partial] ** 3 - CUT_IN ** 3) / (
        RATED ** 3 - CUT_IN ** 3
    )
    out[(speed >= RATED) & (speed < CUT_OUT)] = 1.0
    return out


def load_artifact(path: Path):
    """Read ERA5 original HDF5-backed NetCDF members without renaming units."""
    data = {}
    position = None
    with zipfile.ZipFile(path) as archive:
        for member in archive.namelist():
            if not member.endswith(".nc"):
                continue
            with h5py.File(io.BytesIO(archive.read(member)), "r") as h:
                times = pd.to_datetime(h["valid_time"][:], unit="s", utc=True)
                location = (float(h["longitude"][0]), float(h["latitude"][0]))
                if position is not None and position != location:
                    raise ValueError("instant/accum positions disagree")
                position = location
                for var, expected_unit in (
                    ("ssrd", "J m**-2"),
                    ("u10", "m s**-1"),
                    ("v10", "m s**-1"),
                    ("t2m", "K"),
                ):
                    if var not in h:
                        continue
                    unit = h[var].attrs.get("units", b"")
                    unit = unit.decode() if isinstance(unit, bytes) else str(unit)
                    if unit != expected_unit or var in data:
                        raise ValueError(f"duplicate or wrong units: {var} {unit}")
                    data[var] = pd.Series(
                        h[var][:, 0, 0].astype("float64"), index=times
                    )
    if set(data) != {"ssrd", "u10", "v10", "t2m"}:
        raise ValueError("missing required ERA5 variable")
    result = pd.DataFrame(data).sort_index()
    if result.index.has_duplicates or result.isna().any().any():
        raise ValueError("bad ERA5 chronology or numeric values")
    return result, position


def run(era5_dir: Path, clip_dir: Path, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    wind = pd.read_csv(clip_dir / "NIWE_150m_Kerala_NWIC_point_centres.csv.gz")
    coords = wind[["Longitude (E)", "Latitude (N)"]].to_numpy(dtype="float64")
    results, metrics, hashes = [], {}, {}
    with rasterio.open(
        clip_dir / "PVOUT_yearly_total_kWh_kWp_Kerala_NWIC.tif"
    ) as atlas:
        for site in SITES:
            quarters, locations = [], []
            for q in (2, 3, 4, 1):
                source = era5_dir / f"era5_{site}_q{q}.zip"
                frame, pos = load_artifact(source)
                quarters.append(frame)
                locations.append(pos)
                hashes[source.name] = sha(source)
            if len(set(locations)) != 1:
                raise ValueError(f"{site}: shifting ERA5 grid")
            frame = pd.concat(quarters).sort_index()
            expected = pd.date_range(
                "2024-04-01", periods=8760, freq="h", tz="UTC"
            )
            if not frame.index.equals(expected):
                raise ValueError(f"{site}: FY UTC source has gaps/duplicates")
            lon, lat = COORDS[site]
            index = np.argmin(np.sum((coords - np.array((lon, lat))) ** 2, axis=1))
            niwe = float(wind.iloc[index]["Wind Speed (m/s)"])
            gsa = float(next(atlas.sample([(lon, lat)]))[0])
            if not 0 < niwe < 20 or not 500 < gsa < 2500:
                raise ValueError("source wind/GSA reference implausible")
            # One-hour ERA5 accumulated SSRD J/m2 -> hourly mean W/m2.
            ghi = np.maximum(frame.ssrd.to_numpy() / 3600, 0)
            temp_cell = frame.t2m.to_numpy() - 273.15 + CELL_RISE * ghi
            pv = np.clip(
                ghi / 1000 * PR * np.clip(1 + GAMMA * (temp_cell - 25), 0, 1.5),
                0, 1,
            )
            speed10 = np.hypot(frame.u10.to_numpy(), frame.v10.to_numpy())
            height_proxy = speed10 * (HUB_M / 10.0) ** ALPHA
            if height_proxy.mean() <= 0:
                raise ValueError("zero wind reference")
            # Long-term NIWE mean used only to anchor a sensitivity profile.
            speed150 = height_proxy * niwe / height_proxy.mean()
            wind_cf = turbine_proxy(speed150)
            if not all(np.isfinite(x).all() for x in (pv, wind_cf)):
                raise ValueError("nonfinite proxy")
            results.append(pd.DataFrame({
                "time_utc": expected, "site": site,
                "ghi_W_m2_proxy": ghi, "wind10_era5_m_s": speed10,
                "wind150_mean_anchored_m_s": speed150,
                "solar_pv_proxy_cf": pv,
                "wind_generic_proxy_cf": wind_cf,
            }))
            metrics[site] = {
                "era5_grid_lonlat": locations[0],
                "NIWE_mean_150m_m_s": niwe,
                "GSA_LTA_kWh_kWp_year": gsa,
                "PV_ERA5_proxy_kWh_kWp_FY": float(pv.sum()),
                "wind_generic_proxy_full_load_h_FY": float(wind_cf.sum()),
                "GHI_ERA5_kWh_m2_FY": float(ghi.sum() / 1000),
            }
    out = output / "kerala_5point_FY2024_25_hourly_RESOURCE_PROXIES_NOT_VALIDATED.csv.gz"
    pd.concat(results).to_csv(
        out, index=False, compression="gzip", float_format="%.7g"
    )
    report = {
        "classification": "SENSITIVITY_PROXY_NOT_MODEL_ADMITTED",
        "hours_per_site": 8760, "point_hours": 43800,
        "FY_UTC": "2024-04-01T00:00Z/2025-03-31T23:00Z",
        "source_era5_artifact_zip_sha256": hashes,
        "source_NIWE_clip_sha256": sha(
            clip_dir / "NIWE_150m_Kerala_NWIC_point_centres.csv.gz"
        ),
        "source_GSA_clip_sha256": sha(
            clip_dir / "PVOUT_yearly_total_kWh_kWp_Kerala_NWIC.tif"
        ),
        "assumptions": {
            "wind_shear_alpha": ALPHA, "wind_hub_height_m": HUB_M,
            "wind_generic_cut_in_rated_cut_out_m_s": [CUT_IN, RATED, CUT_OUT],
            "wind_NIWE_anchor": "FY hourly mean forced to atlas long-term mean; not measured validation",
            "PV_performance_ratio": PR, "PV_gamma_per_K": GAMMA,
            "PV_cell_temperature_rise_K_per_W_m2": CELL_RISE,
            "GSA": "long-term reference only, no forced FY energy match",
        },
        "limits": [
            "only five 0.25-degree ERA5 cells, not spatially statewide",
            "NWDP FY solar has 6007/6007 zero observations; cannot validate",
            "generic PV uses GHI, not independently validated plane-of-array",
            "generic wind curve, not a turbine manufacturer power curve",
            "no confirmed project losses, location siting or curtailment",
            "weather and long-term maps cannot establish eligible MW",
        ],
        "model_admitted": False, "historical_generation_validated": False,
        "site_metrics": metrics,
        "output_file": out.name, "output_sha256": sha(out),
    }
    (output / "hourly_proxy_qa.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--era5-dir", type=Path, required=True)
    parser.add_argument("--clip-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args.era5_dir, args.clip_dir, args.out)
    print(json.dumps(summary["site_metrics"], indent=2))
