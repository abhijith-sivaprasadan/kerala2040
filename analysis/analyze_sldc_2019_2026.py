#!/usr/bin/env python3
"""Kerala2040 phase-2 descriptive SLDC daily analysis (NO imputation, NO interval inference).

Input is the private derived nine-CSV bundle. Output is aggregate evidence only.
MU = million kWh; MW = instantaneous/selected-period peak, not daily MWh.
This script intentionally does not access a network or third-party source bytes.
"""
from __future__ import annotations
import argparse, collections, csv, datetime as dt, hashlib, json, math, statistics as st
from pathlib import Path

def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))
def f(v):
    try: return float(v) if v not in (None, '') else None
    except (ValueError, TypeError): return None
def mean(a): return round(st.mean(a),5) if a else None
def med(a): return round(st.median(a),5) if a else None
def percentile(a,p):
    if not a: return None
    a=sorted(a); v=(len(a)-1)*p; lo=int(v); hi=min(lo+1,len(a)-1)
    return round(a[lo]+(a[hi]-a[lo])*(v-lo),5)
def ratio(a,b): return round(100*a/b,4) if b else None
def md(d): return d[5:]
def season(m): return 'summer_MarMay' if m in (3,4,5) else ('monsoon_JunSep' if m in (6,7,8,9) else 'other_OctFeb')
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data-dir',type=Path,default=Path('data/external/sldc_five_sections_2019_2026'))
    ap.add_argument('--output-dir',type=Path,default=Path('results/sldc_advanced_daily_2026_09_23'))
    a=ap.parse_args(); out=a.output_dir;out.mkdir(parents=True,exist_ok=True)
    csvhash=lambda s:hashlib.sha256((a.data_dir/s).read_bytes()).hexdigest()
    manifest=json.loads((a.data_dir/'qa_manifest.json').read_text(encoding='utf-8'))
    assert manifest['raw_archive_sha256']=='2d55fefdcbfcacf7f753cebb0c429479abb6ea5eedb2533297a455735b6bfc3f'
    assert manifest['invalid_accepted_metadata_or_raw_html_sha256']==[]
    daily=read(a.data_dir/'daily_system.csv'); reservoir=read(a.data_dir/'reservoir_rows.csv'); events=read(a.data_dir/'extrema_rows.csv');cal=read(a.data_dir/'source_calendar.csv')
    assert len(daily)==2606 and len(cal)==2606*5
    qualified=[r for r in daily if r['energy_balance_qualified']=='True' and f(r['consumption_qualified_mu']) is not None]
    assert len(qualified)==2575
    assert len({r['date'] for r in daily})==2606
    assert sum(r['energy_balance_qualified']=='False' for r in daily)==1
    byfy=collections.defaultdict(list); bymonth=collections.defaultdict(list)
    for r in qualified: byfy[r['fy']].append(r); bymonth[r['date'][:7]].append(r)
    def dist(rows):
        load=[f(r['consumption_qualified_mu']) for r in rows]
        imp=[f(r['net_import_interface_mu']) for r in rows]
        hydro=[f(r['hydel_total_mu']) for r in rows]
        peak=[f(r['evening_peak_mw']) for r in rows if f(r['evening_peak_mw']) is not None]
        assert all(x is not None for x in imp+hydro)
        return {'n':len(rows),'observed_consumption_mu':round(sum(load),4),'daily_consumption_mean_mu':mean(load),
                'daily_consumption_p10_mu':percentile(load,.10),'daily_consumption_p50_mu':med(load),'daily_consumption_p90_mu':percentile(load,.90),
                'net_import_sum_mu':round(sum(imp),4),'net_import_share_weighted_pct':ratio(sum(imp),sum(load)),
                'net_import_share_daily_median_pct':med([100*x/y for x,y in zip(imp,load)]),
                'hydel_sum_mu':round(sum(hydro),4),'hydel_share_weighted_pct':ratio(sum(hydro),sum(load)),
                'hydel_share_of_internal_generation_pct':ratio(sum(hydro),sum(f(r['internal_generation_mu']) for r in rows)),
                'evening_peak_observed_days':len(peak),'evening_peak_p95_mw':percentile(peak,.95),'max_evening_peak_mw':max(peak) if peak else None}
    fy={k:dist(v) for k,v in sorted(byfy.items())}
    slots=collections.Counter(r['fy'] for r in daily)
    for k,v in fy.items(): v['calendar_days_in_scope']=slots[k];v['coverage_pct']=ratio(v['n'],slots[k])
    months={k:dist(v) for k,v in sorted(bymonth.items())}
    for k,v in months.items():v['month_in_scope_days']=sum(r['date'][:7]==k for r in daily)
    fy_months={}
    for fyid in ['2020-21','2021-22','2022-23','2023-24','2024-25','2025-26']:
        fy_months[fyid]={str(m):dist([r for r in byfy[fyid] if int(r['date'][5:7])==m]) for m in range(1,13)}
    baseline={md(r['date']):r for r in byfy['2020-21']}
    latest={md(r['date']):r for r in byfy['2025-26']}
    overlap=sorted(baseline.keys()&latest.keys())
    b=[f(baseline[d]['consumption_qualified_mu']) for d in overlap]
    l=[f(latest[d]['consumption_qualified_mu']) for d in overlap]
    matched={'baseline_fy':'2020-21','comparison_fy':'2025-26','matched_calendar_month_day_count':len(overlap),
             'baseline_same_days_mean_mu':mean(b),'comparison_same_days_mean_mu':mean(l),
             'paired_relative_change_of_means_pct':ratio(sum(l)-sum(b),sum(b)),
             'paired_absolute_change_mean_mu_per_day':round(st.mean([y-x for x,y in zip(b,l)]),5),
             'paired_days_positive_pct':ratio(sum(y>x for x,y in zip(b,l)),len(overlap))}
    matched_month={}
    for m in range(1,13):
        ix=[i for i,d in enumerate(overlap) if int(d[:2])==m]
        if ix:matched_month[str(m)]={'n':len(ix),'baseline_mean_mu':mean([b[i] for i in ix]),'latest_mean_mu':mean([l[i] for i in ix]),'change_pct':ratio(sum(l[i]-b[i] for i in ix),sum(b[i] for i in ix))}
    pairwise_growth={}
    for base_fy,comp_fy in [('2023-24','2025-26'),('2024-25','2025-26')]:
        first={md(r['date']):r for r in byfy[base_fy]}
        second={md(r['date']):r for r in byfy[comp_fy]}
        matching=sorted(first.keys() & second.keys())
        earlier=[f(first[d]['consumption_qualified_mu']) for d in matching]
        later=[f(second[d]['consumption_qualified_mu']) for d in matching]
        pairwise_growth[f'{base_fy}_to_{comp_fy}']={
            'common_month_day_n':len(matching),
            'baseline_daily_mean_mu':mean(earlier),
            'comparison_daily_mean_mu':mean(later),
            'difference_mu_per_day':round(st.mean([y-x for x,y in zip(earlier,later)]),5),
            'change_pct':ratio(sum(later)-sum(earlier),sum(earlier))}
    within_fy_strata={}
    for key in ['2023-24','2024-25','2025-26']:
        rows=byfy[key]
        lo=percentile([f(r['consumption_qualified_mu']) for r in rows],.25)
        hi=percentile([f(r['consumption_qualified_mu']) for r in rows],.75)
        within_fy_strata[key]={
            'lower_quartile':dist([r for r in rows if f(r['consumption_qualified_mu'])<=lo]),
            'upper_quartile':dist([r for r in rows if f(r['consumption_qualified_mu'])>=hi]),
            'p25_consumption_mu':lo,'p75_consumption_mu':hi}
    # Every year separated in seasonal macro-comparison; no misleading concatenated date count.
    seasonal={}
    for y in range(2020,2026):
        rows=[r for r in qualified if r['date'][:4]==str(y)]
        seasonal[str(y)]={s:dist([r for r in rows if season(int(r['date'][5:7]))==s]) for s in ['summer_MarMay','monsoon_JunSep','other_OctFeb']}
    # Supply-stress strata: high-demand dates measured by own daily distribution (no confounded inference).
    all_load=[f(r['consumption_qualified_mu']) for r in qualified]
    p90=percentile(all_load,.9);p10=percentile(all_load,.1)
    strata={'top_decile':dist([r for r in qualified if f(r['consumption_qualified_mu'])>=p90]),
            'bottom_decile':dist([r for r in qualified if f(r['consumption_qualified_mu'])<=p10]),
            'cutoffs_mu':{'p10':p10,'p90':p90}}
    peakrows=[r for r in qualified if f(r['evening_peak_mw']) is not None and f(r['morning_peak_mw']) is not None]
    peaks={'max_evening_daily_table':sorted([{'date':r['date'],'mw':f(r['evening_peak_mw']),'time_ist':r['evening_peak_time_ist'],'daily_consumption_mu':f(r['consumption_qualified_mu']),'net_import_mu':f(r['net_import_interface_mu'])} for r in peakrows],key=lambda x:-x['mw'])[:15],
           'within_day_evening_minus_morning_mw_median':med([f(r['evening_peak_mw'])-f(r['morning_peak_mw']) for r in peakrows]),
           'within_day_evening_gt_morning_pct':ratio(sum(f(r['evening_peak_mw'])>f(r['morning_peak_mw']) for r in peakrows),len(peakrows)),
           'max_daily_consumption':sorted([{'date':r['date'],'mu':f(r['consumption_qualified_mu']),'evening_peak_mw':f(r['evening_peak_mw'])} for r in qualified],key=lambda x:-x['mu'])[:12]}
    pt={}
    for k,rr in sorted(byfy.items()):
        times=[]
        for row in rr:
            try:
                hh,mm=row['evening_peak_time_ist'].strip().split(':',1)
                if 0<=int(hh)<24 and 0<=int(mm)<60: times.append(int(hh)+int(mm)/60)
            except (ValueError,AttributeError): pass
        pt[k]={'n':len(times),'median_evening_peak_clock_ist_h':med(times),'pct_21_00_or_later':ratio(sum(t>=21 for t in times),len(times))}
    # Paired extrema peak source consistency: don't conflate 'Other' block extrema with Statistics daily peak.
    eventkeys=collections.Counter((r['date'],r['event'],r['period'],r['quantity']) for r in events)
    duplicate_events=[{'date':d,'event':e,'period':p,'quantity':q,'count':n}for (d,e,p,q),n in eventkeys.items() if n>1]
    other={r['date']:f(r['mw']) for r in events if (r['event'],r['period'],r['quantity'])==('maximum','evening','consumption') and f(r['mw']) is not None}
    diffs=[(r['date'],f(r['evening_peak_mw'])-other[r['date']]) for r in daily if f(r['evening_peak_mw']) is not None and r['date'] in other]
    peak_source={'paired_days':len(diffs),'exact_equal_days':sum(abs(v)<.00001 for _,v in diffs),
                 'max_abs_difference_mw':max(abs(v) for _,v in diffs),
                 '2026_04_23':{'statistics_evening_peak_mw':f(next(r for r in daily if r['date']=='2026-04-23')['evening_peak_mw']),'other_evening_max_consumption_mw':other.get('2026-04-23')},'duplicate_source_events':duplicate_events}
    # Strict reservoir-specific statistic, not average of heterogeneous reservoirs.
    idukki=[r for r in reservoir if r['reservoir']=='IDUKKI' and f(r['storage_pct']) is not None]
    idukki_month={}
    for m in range(1,13):
        rr=[r for r in idukki if int(r['date'][5:7])==m]
        idukki_month[str(m)]={'n':len(rr),'median_storage_pct':med([f(r['storage_pct']) for r in rr]),'p10_storage_pct':percentile([f(r['storage_pct']) for r in rr],.1),'p90_storage_pct':percentile([f(r['storage_pct']) for r in rr],.9)}
    # Show full-year reservoir dry-season minimum and end-year levels, but do not calculate hydrological inflow from it.
    idukki_fy={}
    for fyid in ['2020-21','2021-22','2022-23','2023-24','2024-25','2025-26']:
        start=int(fyid[:4]); rr=[r for r in idukki if ((int(r['date'][:4])==start and int(r['date'][5:7])>=4) or (int(r['date'][:4])==start+1 and int(r['date'][5:7])<=3))]
        idukki_fy[fyid]={'days':len(rr),'median_storage_pct':med([f(r['storage_pct']) for r in rr]),'minimum_storage_pct':min(f(r['storage_pct']) for r in rr) if rr else None,
                      'minimum_date':min(rr,key=lambda r:(f(r['storage_pct']),r['date']))['date'] if rr else None}
    missing=collections.Counter((r['section'],r['status']) for r in cal)
    qa={'source_archive_sha256':manifest['raw_archive_sha256'],
        'input_daily_sha256':csvhash('daily_system.csv'),'input_reservoir_sha256':csvhash('reservoir_rows.csv'),
        'qualified_days':len(qualified),'report_date_slots':len(daily),'missing_sections':{s:{z:missing[(s,z)]for z in ['accepted','rejected','pending']}for s in ['statistics','imports','storage','availability','other_extrema']},
        'source_balance_exceptions':[{'date':r['date'],'reported_consumption_mu':f(r['consumption_mu']),'balance_error_mu':f(r['balance_error_mu'])} for r in daily if r['energy_balance_qualified']=='False'],
        'extrema_duplicate_source_events':duplicate_events,
        'reservoir_rows_storage_pct_over_100':[{'date':r['date'],'reservoir':r['reservoir'],'reported_pct':f(r['storage_pct'])}for r in reservoir if f(r['storage_pct']) is not None and f(r['storage_pct'])>100],
        'no_imputation':True,'interval_telemetry_present':False}
    result={'classification':'descriptive_observed_S L D C_daily_partially_missing_not_hourly_not_model_ready'.replace(' ',''),
            'start_date':'2019-08-06','end_date':'2026-09-23','qa':qa,'fy':fy,'matched_2020_21_vs_2025_26':matched,
            'matched_months':matched_month,'matched_other_fys':pairwise_growth,'within_fy_strata':within_fy_strata,'monthly':months,'seasonal_by_calendar_year':seasonal,
            'demand_strata':strata,'peaks':peaks,'peak_clock':pt,'peak_source_crosswalk':peak_source,
            'idukki_storage_month':idukki_month,'idukki_storage_fy':idukki_fy,
            'limitations':['2019-20 and 2026-27 are partial FY windows','FY2021-22 through FY2025-26 have confirmed missing daily observations','2019-12-05 balance error excluded, reported values retained','No missing daily observation imputed or full-year sum inferred from a partial year','Other extrema are selected half-hour maxima/minima, not interval chronology','Storage % and MU capability are not power capacity MW','In-state reporting boundary and imports are separate from allocated central-sector capacity','Generation/import section source rows overlap; source-labeled totals must not be double-counted','Hydro generation/import share associations are constrained by consumption balance; no causal claim','These are source-reported data and may include official revisions not captured by crawl']}
    (out/'advanced_results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    with (out/'fy_advanced_summary.csv').open('w',newline='',encoding='utf-8') as fh:
        writer=csv.DictWriter(fh,fieldnames=['fy']+list(next(iter(fy.values())).keys()));writer.writeheader();writer.writerows([{'fy':k,**v}for k,v in fy.items()])
    with (out/'monthly_advanced_summary.csv').open('w',newline='',encoding='utf-8') as fh:
        writer=csv.DictWriter(fh,fieldnames=['month']+list(next(iter(months.values())).keys()));writer.writeheader();writer.writerows([{'month':k,**v}for k,v in months.items()])
    with (out/'idukki_monthly_seasonality.csv').open('w',newline='',encoding='utf-8') as fh:
        writer=csv.DictWriter(fh,fieldnames=['month','n','median_storage_pct','p10_storage_pct','p90_storage_pct']);writer.writeheader();writer.writerows([{'month':k,**v}for k,v in idukki_month.items()])
    print('QA',json.dumps(qa,ensure_ascii=False))
    print('FY',json.dumps(fy))
    print('MATCHED',json.dumps(matched))
    print('MATCHED_MONTH',json.dumps(matched_month))
    print('MATCHED_OTHER',json.dumps(pairwise_growth))
    print('WITHIN_FY_STRATA',json.dumps(within_fy_strata))
    print('PEAK',json.dumps({k:v for k,v in peaks.items() if k!='max_daily_consumption'}))
    print('PEAK_SOURCE',json.dumps(peak_source))
    print('PEAK_TIMING',json.dumps(pt))
    print('IDUKKI',json.dumps(idukki_month))
    print('IDUKKI_FY',json.dumps(idukki_fy))
    print('SEASONS_2023_2025',json.dumps({k:seasonal[k]for k in ['2023','2024','2025']}))
    print('DEMAND_STRATA',json.dumps(strata))
    print('OUTPUT',out)
if __name__=='__main__':main()
