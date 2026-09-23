#!/usr/bin/env python3
"""Kerala2040: offline daily SLDC × named Idukki reservoir rain/inflow, flood review,
optional daily ERA5 weather and independently evidenced observed Atlas rows.

No gap filling. 2018 event has no matching SLDC records. Descriptive only.
Usage: python analyze_sldc_hydro_flood_weather.py --curated <dir> --out <dir>
       [--weather-daily <csv>] [--atlas-observed <csv>]
Weather CSV columns: date, rainfall_mm, t2m_c (optional), dataset/source (optional),
  with exactly one row per IST DATE, spatial aggregation specified externally.
Atlas CSV columns: date, metric, value, source_type, source, source_url (optional).
  Only explicit observed/metered rows with documented source_url and verified=true become
  provenance-review candidates, never automatically certified or blended into SLDC.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

EVENTS = [
    {"event":"Kerala flood 2018", "start":"2018-08-08", "end":"2018-08-20", "class":"2018 historical anchor: outside SLDC sample", "region":"multiple Kerala basins", "source":"https://www.preventionweb.net/publication/study-report-kerala-floods-august-2018"},
    {"event":"August 2019 Kerala floods", "start":"2019-08-08", "end":"2019-08-14", "class":"flood/rainfall event review", "region":"north and central Kerala", "source":"https://www.scribd.com/document/535584539/report-on-losses-on-flood"},
    {"event":"Pettimudi 2020 landslide/heavy rain", "start":"2020-08-06", "end":"2020-08-11", "class":"landslide; not statewide flood", "region":"Idukki", "source":"https://www.ndrf.gov.in/en/operations/landslide-idukki-kerala-2020"},
    {"event":"October 2021 flood", "start":"2021-10-15", "end":"2021-10-20", "class":"documented flood/landslides", "region":"central and southern Kerala", "source":"https://sdma.kerala.gov.in/wp-content/uploads/2022/05/Event-report_October-2021.pdf"},
    {"event":"Wayanad 2024 landslide", "start":"2024-07-29", "end":"2024-08-04", "class":"landslide; separate hazard category", "region":"Wayanad", "source":"https://www.reuters.com/world/india/india-extreme-weather-events-landslides-kerala-state-2024-07-30/"},
    {"event":"Nilambur 2026 flash flood", "start":"2026-09-20", "end":"2026-09-22", "class":"localized flash flood, not state-wide", "region":"Malappuram", "source":"https://www.newindianexpress.com/states/kerala/2026/Sep/21/flash-flood-in-kottapuzha-river-claims-five-lives-in-nilambur-one-missing"},
]

OBSERVED = {"observed", "metered", "actual", "measured", "reported_official"}
SYSTEM_COLS = ["consumption_qualified_mu", "hydel_total_mu", "net_import_interface_mu", "evening_peak_mw"]
RES_COLS = ["rainfall_mm", "inflow_mcm_day", "storage_pct", "effective_storage_mcm"]


def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024*1024), b""):
            h.update(b)
    return h.hexdigest()


def add_anomaly_corr(df: pd.DataFrame, x: str, y: str) -> dict:
    z = df[["date", x, y]].dropna().copy()
    if len(z) < 50: return {"n":len(z), "raw_r":None, "year_month_demeaned_r":None}
    z["year_month"] = z.date.dt.strftime("%Y-%m")
    for col in (x, y): z[col+"_resid"] = z[col]-z.groupby("year_month")[col].transform("mean")
    return {"n":len(z),"raw_r":float(z[x].corr(z[y])), "year_month_demeaned_r":float(z[x+"_resid"].corr(z[y+"_resid"]))}


def load(curated: Path, weather: Path | None, atlas: Path | None):
    paths = {name:curated/name for name in ("daily_system.csv","reservoir_rows.csv","source_calendar.csv")}
    for p in paths.values():
        if not p.is_file(): raise FileNotFoundError(p)
    d=pd.read_csv(paths["daily_system.csv"],parse_dates=["date"],low_memory=False)
    r=pd.read_csv(paths["reservoir_rows.csv"],parse_dates=["date"],low_memory=False)
    if d.date.duplicated().any(): raise ValueError("duplicated SLDC date")
    i=r[r.reservoir.astype(str).str.upper().eq("IDUKKI")].copy()
    if i.date.duplicated().any(): raise ValueError("multiple IDUKKI reservoir rows for a date")
    for c in RES_COLS: i[c]=pd.to_numeric(i[c],errors="coerce")
    i=i[["date",*RES_COLS,"source_sha256"]].rename(columns={c:"idukki_"+c for c in RES_COLS}|{"source_sha256":"idukki_source_sha256"})
    d=d.merge(i,on="date",how="left",validate="one_to_one").sort_values("date")
    for c in SYSTEM_COLS:d[c]=pd.to_numeric(d[c],errors="coerce")
    d["event_labels"]=""
    for e in EVENTS:
        mask=d.date.between(pd.Timestamp(e["start"]),pd.Timestamp(e["end"]))
        d.loc[mask,"event_labels"] = d.loc[mask,"event_labels"].apply(lambda old: (old+" | " if old else "")+e["event"])
    provenance={str(p):sha(p) for p in paths.values()}
    if weather:
        w=pd.read_csv(weather,parse_dates=["date"])
        if "rainfall_mm" not in w:raise ValueError("Weather CSV needs rainfall_mm")
        if w.date.duplicated().any():raise ValueError("Weather CSV date duplicated; aggregate locations and IST days explicitly first")
        if w.date.dt.tz is not None:raise ValueError("Weather CSV date must be IST local date, no UTC timestamps")
        if pd.to_numeric(w.rainfall_mm,errors="coerce").lt(0).any():raise ValueError("negative weather rainfall")
        cols=["date","rainfall_mm"] + (["t2m_c"] if "t2m_c" in w else [])
        w=w[cols].rename(columns={"rainfall_mm":"weather_rainfall_mm","t2m_c":"weather_t2m_c"})
        d=d.merge(w,on="date",how="left",validate="one_to_one")
        provenance[str(weather)]=sha(weather)
    atlas_summary={"provided":bool(atlas),"accepted_rows":0,"rejected_rows":0,"accepted_labelled_candidate_series":[]}
    if atlas:
        a=pd.read_csv(atlas,parse_dates=["date"],low_memory=False)
        req={"date","metric","value","source_type","source","source_url","verified"}
        if not req.issubset(a.columns):raise ValueError(f"Atlas extract needs {sorted(req)}")
        a["source_type"]=a.source_type.astype(str).str.strip().str.lower()
        good=a[a.source_type.isin(OBSERVED)].copy()
        good=good[good.verified.astype(str).str.lower().isin(["true","1","yes"])]
        good=good[good.source_url.notna() & good.source_url.astype(str).str.startswith("https://")]
        good["value"]=pd.to_numeric(good.value,errors="coerce");good=good.dropna(subset=["value"])
        # Preserve each observed source/metric separately; do not merge conflicting providers by day.
        atlas_summary={"provided":True,"accepted_rows":len(good),"rejected_rows":len(a)-len(good),"accepted_labelled_candidate_series":sorted((good["source"].astype(str)+"::"+good["metric"].astype(str)).unique().tolist())}
        provenance[str(atlas)]=sha(atlas)
        return d, good, provenance, atlas_summary
    return d, pd.DataFrame(), provenance, atlas_summary


def run(args):
    out=args.out;out.mkdir(parents=True,exist_ok=True)
    d,atlas,source_hashes,atlas_qa=load(args.curated,args.weather_daily,args.atlas_observed)
    rain="idukki_rainfall_mm";inflow="idukki_inflow_mcm_day"
    pairs=[(rain,inflow),(rain,"hydel_total_mu"),(rain,"consumption_qualified_mu"),(rain,"net_import_interface_mu"),("idukki_storage_pct","hydel_total_mu")]
    if "weather_rainfall_mm" in d:pairs.extend([("weather_rainfall_mm","hydel_total_mu"),("weather_rainfall_mm","consumption_qualified_mu"),("weather_rainfall_mm",inflow)])
    if "weather_t2m_c" in d:pairs.append(("weather_t2m_c","consumption_qualified_mu"))
    cor={x+"__"+y:add_anomaly_corr(d,x,y) for x,y in pairs}
    ev=[]
    for e in EVENTS:
        window=d[d.date.between(pd.Timestamp(e["start"]),pd.Timestamp(e["end"]))]
        row={**e,"observed_calendar_days":len(window),"qualified_consumption_days":int(window.consumption_qualified_mu.count()),"weather_gauge_days":int(window[rain].count())}
        for col in SYSTEM_COLS + [rain,inflow,"idukki_storage_pct"]:
            row[col+"_mean"]=None if not len(window) or not window[col].notna().any() else round(float(window[col].mean()),5)
        ev.append(row)
    daily=out/"sldc_idukki_rainfall_inflow_daily_PRIVATE.csv";d.to_csv(daily,index=False)
    if len(atlas):atlas.to_csv(out/"atlas_observed_labelled_candidates_PRIVATE.csv",index=False)
    payload={"classification":"observed_SLDC_named_reservoir_gauge_descriptive_join_NOT_causal_flood_effect", "source_sha256":source_hashes,"date_start":d.date.min().date().isoformat(),"date_end":d.date.max().date().isoformat(),"date_slots":len(d),"qualified_consumption_days":int(d.consumption_qualified_mu.count()),"idukki_rainfall_available_days":int(d[rain].count()),"idukki_inflow_available_days":int(d[inflow].count()),"correlation":cor,"event_windows":ev,"atlas_qa":atlas_qa,"era5_weather_included":bool(args.weather_daily),"constraints":["2018 floods predates SLDC date scope; never fabricate 2018 daily energy", "IDUKKI rainfall is source reservoir gauge, not Kerala-wide precipitation or Nilambur rainfall", "event windows are descriptive and do not establish flood causality or physical flood extent", "2019-2026 different system baselines, incomplete days, dispatch and import energy balance confounding", "PSP cannot be inferred from reservoir storage MU or existing hydro MW"]}
    (out/"public_flood_hydro_weather_qa.json").write_text(json.dumps(payload,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"slots":len(d),"rain_days":payload["idukki_rainfall_available_days"],"inflow_days":payload["idukki_inflow_available_days"],"observed_atlas":atlas_qa["accepted_rows"],"reject_atlas":atlas_qa["rejected_rows"],"events":len(ev),"out":str(out)},indent=2))

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--curated",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--weather-daily",type=Path)
    ap.add_argument("--atlas-observed",type=Path)
    run(ap.parse_args())
