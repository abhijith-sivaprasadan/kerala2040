"""Integrate a user-acquired FY2024-25 SLDC public archive with explicit provenance.

Run this against the *raw* 5-section HTML archive and first-pass processed ZIP.
No observations, plant ratings, interval telemetry or hydro cascade mappings are imputed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import zipfile
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

NAMES = (
    "daily_balance.csv", "hydro_station_daily.csv", "import_interface_daily.csv",
    "reservoir_daily.csv", "selected_intraday_extrema.csv",
)


def read_rows(source: zipfile.ZipFile, filename: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(source.read(f"sldc_processed/{filename}").decode("utf-8-sig"))))


def summary_from_processed(processed: zipfile.ZipFile, report: dict, raw_digest: str) -> dict:
    rows = {name: read_rows(processed, name) for name in NAMES}
    balance = rows[NAMES[0]]
    if len(balance) != 365 or len({r['date'] for r in balance}) != 365:
        raise ValueError("Expected 365 unique dated rows, including unobserved days")
    observed = [r for r in balance if r['status'] == 'observed']
    missing = [r['date'] for r in balance if r['status'] == 'missing']
    if missing != report['missing_dates'] or len(observed) != report['observed_days']:
        raise ValueError("QA report and daily dates disagree")
    expected_dates = [(date(2024, 4, 1) + timedelta(days=i)).isoformat() for i in range(365)]
    if [r['date'] for r in balance] != expected_dates:
        raise ValueError("Daily chronology is incomplete or out of order")
    for row in observed:
        if abs(float(row['internal_generation_mu']) + float(row['net_import_mu']) - float(row['consumption_mu'])) > .001:
            raise ValueError(f"Energy balance failed for {row['date']}")
    actual_totals = {
        key: round(sum(float(r[key]) for r in observed), 4)
        for key in ('hydro_mu','internal_generation_mu','net_import_mu','consumption_mu')
    }
    for key, total in actual_totals.items():
        if abs(total - report['observed_days_totals_mu'][key]) > 0.0001:
            raise ValueError(f"QA {key} does not match raw processed records")
    if any(int(report[k]) for k in ('bad_raw_sha256_count', 'bad_response_report_date_count')):
        raise ValueError("Raw archive already failed SHA/date validation")
    if report['source_archive_sha256'] != raw_digest:
        raise ValueError("Uploaded original SLDC archive differs from the verified archive")
    lookup = {'hydro_station_daily.csv':'hydro_station', 'import_interface_daily.csv':'import_interface',
              'reservoir_daily.csv':'reservoir','selected_intraday_extrema.csv':'selected_intraday_extrema'}
    for name in NAMES:
        key = lookup.get(name, name.removesuffix('.csv'))
        if len(rows[name]) != report['normalized_row_counts'][key]:
            raise ValueError(f"QA row count mismatch for {name}")
    monthly = defaultdict(lambda: defaultdict(float))
    stations = defaultdict(lambda: {'generation_mu': 0.0, 'days_with_reported_generation': 0})
    interfaces = defaultdict(lambda: {'import_mu':0.0, 'days_with_reported_import':0})
    reservoirs = defaultdict(list)
    for row in rows['hydro_station_daily.csv']:
        if row['generation_mu'] != '':
            st = stations[row['station_name_as_reported']]
            st['generation_mu'] += float(row['generation_mu'])
            st['days_with_reported_generation'] += 1
            monthly[row['date'][:7]][f"station::{row['station_name_as_reported']}"] += float(row['generation_mu'])
    for row in rows['import_interface_daily.csv']:
        if row['import_mu'] != '':
            it = interfaces[row['interface_name_as_reported']]
            it['import_mu'] += float(row['import_mu'])
            it['days_with_reported_import'] += 1
    for row in rows['reservoir_daily.csv']:
        if row['storage_percent'] != '':
            reservoirs[row['reservoir_name_as_reported']].append((row['date'],float(row['storage_percent'])))
    station_order = sorted(stations, key=lambda name: stations[name]['generation_mu'], reverse=True)
    for row in observed:
        bucket = monthly[row['date'][:7]]
        bucket['observed_days'] += 1
        for source, dest in [('hydro_mu','hydro_mu'), ('net_import_mu','net_import_mu'),
                             ('consumption_mu','consumption_mu'), ('internal_generation_mu','internal_generation_mu')]:
            bucket[dest] += float(row[source])
    mrows = []
    for month, values in sorted(monthly.items()):
        mrows.append({'month':month,'observed_days':int(values['observed_days']),
                      **{k:round(values[k],4) for k in ('hydro_mu','net_import_mu','consumption_mu','internal_generation_mu')},
                      'top_station_mu': {s:round(values[f'station::{s}'],4) for s in station_order[:8]}})
    return {
        'classification':'derived_from_measured',
        'source_type':'normalised_official_sldc_daily_public_reports',
        'source':'Kerala SLDC Generation, Imports, Storage, Availability and Others; FY2024–25',
        'source_url':'https://sldckerala.com/index.php?id=1',
        'source_archive_sha256':raw_digest,
        'period':'2024-04-01 to 2025-03-31',
        'resolution':'daily; selected reported intraday extrema only',
        'observed_days':len(observed),
        'expected_days':365,
        'missing_dates':missing,
        'reported_row_counts':report['normalized_row_counts'],
        'energy_balance_max_error_mu': report['max_abs_daily_balance_residual_mu'],
        'observed_totals_mu':actual_totals,
        'monthly':mrows,
        'stations':[{'station_name_as_reported':s,'generation_mu':round(stations[s]['generation_mu'],4),
                     'days_with_reported_generation':stations[s]['days_with_reported_generation']}
                    for s in station_order],
        'interfaces':[{'interface_name_as_reported':s,'import_mu':round(interfaces[s]['import_mu'],4),
                       'days_with_reported_import':interfaces[s]['days_with_reported_import']}
                      for s in sorted(interfaces,key=lambda s:interfaces[s]['import_mu'],reverse=True)],
        'reservoirs':[{'reservoir_name_as_reported':name,'observation_count':len(seq),
                       'first_date':seq[0][0],'last_date':seq[-1][0],
                       'storage_pct_min':min(v for _,v in seq),
                       'storage_pct_max':max(v for _,v in seq)}
                      for name,seq in sorted(reservoirs.items())],
        'limitations': [
          '354 of 365 days are observed; missing days are not zero or interpolated.',
          'Reported daily station generation is not measured hourly dispatch or nameplate capacity.',
          'Empty source cells are unknown, not zero; station totals cover days with reported numeric values only.',
          'Interface energy is not transfer capability; monthly/annual totals are sums of observed days only.',
          'Reservoir storage and station generation are separate observations, not a validated cascade/energy conversion.',
          'Reported extrema are isolated peak/minimum observations, not a continuous hourly or 15-minute load profile.',
          'Availability/merit-order tables remain in the raw archive; they are not fully normalised here.'
        ]
    }


def integrate(raw_path: Path, processed_path: Path, root: Path) -> dict:
    digest = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    with zipfile.ZipFile(processed_path) as z:
        report = json.loads(z.read('sldc_processed/qa_report.json'))
        summary = summary_from_processed(z,report,digest)
        out = root/'data/external/sldc_fy2024_25'
        out.mkdir(parents=True,exist_ok=True)
        for name in NAMES:
            (out/name).write_bytes(z.read(f'sldc_processed/{name}'))
        (out/'qa_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        (out/'README.md').write_bytes(z.read('sldc_processed/README.md'))
    dest=root/'public/sldc-station-evidence.json'
    dest.write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    archive=root/'public/sldc-processed-evidence.zip'
    shutil.copy2(processed_path,archive)
    return summary


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw',type=Path,required=True)
    parser.add_argument('--processed',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    result=integrate(args.raw,args.processed,args.root)
    print(json.dumps({'observed_days':result['observed_days'],'station_count':len(result['stations']),
                      'interface_count':len(result['interfaces']),'reservoir_count':len(result['reservoirs']),
                      'summary':str(args.root/'public/sldc-station-evidence.json')},indent=2))