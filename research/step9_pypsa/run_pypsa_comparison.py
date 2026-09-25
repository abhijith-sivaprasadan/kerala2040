#!/usr/bin/env python3
"""Independent PyPSA reproduction of Kerala2040 Step 8 daily balancing LP.
Run with: python run_pypsa_comparison.py --root /path/to/step7-and-step8 --days 354
Requires pypsa, highspy, pandas, numpy. No SciPy optimisation is used here.
"""
import argparse, collections, csv, json, pathlib
import numpy as np
import pandas as pd
import pypsa

CASES=('diagnostic_fixed','hydro_flex_1p5','hydro_flex_1p5_import_flex_1p25')
SHAPES=('flat','morning_evening','evening_stress')
DT=.25

def solve_day(records, case):
    demand=np.array([float(r['demand_mw']) for r in records]); h=float(records[0]['hydro_fixed_mw']); imp=float(records[0]['net_import_fixed_mw']); other=float(records[0]['nonhydro_internal_fixed_mw'])
    if len(records)!=96 or min(h,imp,other)<-1e-8: raise ValueError('Invalid day or negative fixed supply')
    idx=pd.date_range('2024-01-01',periods=96,freq='15min')
    n=pypsa.Network();n.set_snapshots(idx);n.snapshot_weightings.loc[:,'objective']=DT
    n.add('Bus','kerala')
    n.add('Load','synthetic_demand',bus='kerala',p_set=demand)
    n.add('Generator','fixed_nonhydro',bus='kerala',p_nom=max(other,1e-8),p_min_pu=other/max(other,1e-8),p_max_pu=other/max(other,1e-8))
    n.add('Generator','hydro',bus='kerala',p_nom=max(1.5*h,1e-8),p_min_pu=(h/max(1.5*h,1e-8) if case=='diagnostic_fixed' else 0),p_max_pu=(h/max(1.5*h,1e-8) if case=='diagnostic_fixed' else 1),marginal_cost=1e-6)
    icap=imp if case!='hydro_flex_1p5_import_flex_1p25' else 1.25*imp
    n.add('Generator','net_import',bus='kerala',p_nom=max(icap,1e-8),p_min_pu=(imp/max(icap,1e-8) if case!='hydro_flex_1p5_import_flex_1p25' else 0),p_max_pu=(imp/max(icap,1e-8) if case!='hydro_flex_1p5_import_flex_1p25' else 1),marginal_cost=1e-6)
    n.add('Generator','diagnostic_unserved',bus='kerala',p_nom=1e6,marginal_cost=1)
    n.add('Generator','diagnostic_surplus',bus='kerala',p_nom=1e6,marginal_cost=1,sign=-1)
    model=n.optimize.create_model()
    # Exact daily energy constraints in MWh. PyPSA snapshot objective weights are not assumed to enforce these.
    gp=model.variables['Generator-p']
    model.add_constraints(DT*gp.loc[:, 'hydro'].sum('snapshot') == 24*h,name='hydro_daily_mwh')
    model.add_constraints(DT*gp.loc[:, 'net_import'].sum('snapshot') == 24*imp,name='import_daily_mwh')
    status,termination=n.optimize.solve_model(solver_name='highs')
    if status!='ok' or termination!='optimal':raise RuntimeError((status,termination))
    p=n.generators_t.p
    hyd=p['hydro'].to_numpy();imports=p['net_import'].to_numpy();short=p['diagnostic_unserved'].to_numpy();surplus=p['diagnostic_surplus'].to_numpy()
    residual=hyd+imports+other+short-surplus-demand
    assert max(abs(residual))<1e-4
    assert abs(DT*sum(hyd)-24*h)<1e-4 and abs(DT*sum(imports)-24*imp)<1e-4
    return dict(unserved_mwh=float(DT*sum(short)),surplus_mwh=float(DT*sum(surplus)),max_balance_error_mw=float(max(abs(residual))),hydro_budget_error_mwh=float(DT*sum(hyd)-24*h),import_budget_error_mwh=float(DT*sum(imports)-24*imp))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=pathlib.Path,required=True);ap.add_argument('--days',type=int,default=354);ap.add_argument('--output',type=pathlib.Path,default=pathlib.Path('pypsa_comparison.json'));a=ap.parse_args()
    with (a.root/'kerala2040_balancing_step8'/'balancing_daily.csv').open(newline='') as f:reference={(r['date'],r['scenario'],r['case']):r for r in csv.DictReader(f)}
    results=[];max_error=0
    for shape in SHAPES:
        days=collections.defaultdict(list)
        with (a.root/'kerala2040_integrated_step7'/f'integrated_{shape}_15min.csv').open(newline='') as f:
            for r in csv.DictReader(f):days[r['date']].append(r)
        for date in sorted(days)[:a.days]:
            for case in CASES:
                computed=solve_day(days[date],case);ref=reference[date,shape,case]
                e1=computed['unserved_mwh']-float(ref['diagnostic_unserved_mwh']);e2=computed['surplus_mwh']-float(ref['diagnostic_surplus_mwh']);max_error=max(max_error,abs(e1),abs(e2))
                results.append(dict(date=date,shape=shape,case=case,**computed,unserved_difference_mwh=e1,surplus_difference_mwh=e2))
            print('SOLVED',shape,date,flush=True)
    # Daily optimal slack objective is the comparison target. Individual generator MW schedules may be nonunique.
    report=dict(pypsa_version=pypsa.__version__,days_per_shape=min(a.days,354),solves=len(results),max_abs_daily_slack_difference_mwh=max_error,comparison_tolerance_mwh=1e-3,status='PASS' if max_error<1e-3 else 'FAIL',results=results)
    a.output.write_text(json.dumps(report,indent=2));print('RESULT',report['status'],'solves',len(results),'max difference MWh',max_error)
    if report['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
