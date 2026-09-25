#!/usr/bin/env python3
"""Rebuild the exact Step 7 synthetic inputs and Step 8 SciPy reference from committed SLDC daily evidence."""
import argparse,csv,json,math,random,pathlib,collections,datetime as dt
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
DT=.25; N=96
SHAPES=('flat','morning_evening','evening_stress')
CASES=('diagnostic_fixed','hydro_flex_1p5','hydro_flex_1p5_import_flex_1p25')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=pathlib.Path,default=pathlib.Path('.'));a=ap.parse_args();root=a.root
 source=root/'data/external/sldc_fy2024_25/daily_balance.csv'
 with source.open(newline='') as f: daily=[r for r in csv.DictReader(f) if r['status']=='observed']
 if len(daily)!=354: raise RuntimeError(f'expected 354 observed days, got {len(daily)}')
 s7=root/'kerala2040_integrated_step7';s8=root/'kerala2040_balancing_step8';s7.mkdir(exist_ok=True);s8.mkdir(exist_ok=True)
 acct=[]
 for r in daily:
  hydro=float(r['hydro_mu']);internal=float(r['internal_generation_mu']);imp=float(r['net_import_mu']);demand=float(r['consumption_mu'])
  acct.append(dict(date=r['date'],demand_mu=demand,hydro_mu=hydro,nonhydro_internal_mu=internal-hydro,internal_generation_mu=internal,net_import_mu=imp,balance_residual_mu=internal+imp-demand,source_response_sha256=r['source_sha256'],classification='OBSERVED_DAILY_ENERGY_ACCOUNTING_NOT_DISPATCH'))
 with (s7/'integrated_daily_accounting.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=acct[0].keys());w.writeheader();w.writerows(acct)
 for method in SHAPES:
  out=[]
  for r in daily:
   d=r['date'];energy=float(r['consumption_mu']);rng=random.Random(f'2040:{d}:{method}');weights=[]
   for slot in range(96):
    hour=slot/4;morning=math.exp(-.5*((hour-9)/2.6)**2);evening=math.exp(-.5*((hour-19.25)/2.2)**2)
    v=1 if method=='flat' else (.77+.19*morning+.43*evening if method=='morning_evening' else .65+.15*morning+.8*evening)
    weights.append(v*(1+.015*rng.uniform(-1,1)))
   powers=[4000*energy*w/sum(weights) for w in weights]
   h=float(r['hydro_mu'])*1000/24;n=(float(r['internal_generation_mu'])-float(r['hydro_mu']))*1000/24;i=float(r['net_import_mu'])*1000/24
   day=dt.date.fromisoformat(d)
   for slot,p in enumerate(powers):
    local=dt.datetime.combine(day,dt.time(),dt.timezone(dt.timedelta(hours=5,minutes=30)))+dt.timedelta(minutes=15*slot)
    out.append(dict(timestamp_ist=local.isoformat(),date=d,scenario=method,demand_mw=round(p,9),hydro_fixed_mw=h,nonhydro_internal_fixed_mw=n,net_import_fixed_mw=i,unserved_or_surplus_diagnostic_mw=round(p,9)-h-n-i,classification='SYNTHETIC_LOAD_FIXED_DAILY_SUPPLY_NOT_OPTIMISED_DISPATCH'))
  with (s7/f'integrated_{method}_15min.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
 A=lil_matrix((N+2,4*N),dtype=float)
 for i in range(N):A[i,i]=1;A[i,N+i]=1;A[i,2*N+i]=1;A[i,3*N+i]=-1
 A[N,:N]=DT;A[N+1,N:2*N]=DT;A=A.tocsr();cost=np.r_[np.full(N,1e-6),np.full(N,1e-6),np.ones(N),np.ones(N)]
 refs=[]
 for shape in SHAPES:
  days=collections.defaultdict(list)
  with (s7/f'integrated_{shape}_15min.csv').open(newline='') as f:
   for r in csv.DictReader(f):days[r['date']].append(r)
  for case in CASES:
   for date,records in sorted(days.items()):
    load=np.array([float(r['demand_mw']) for r in records]);h0=float(records[0]['hydro_fixed_mw']);i0=float(records[0]['net_import_fixed_mw']);g0=float(records[0]['nonhydro_internal_fixed_mw'])
    if case=='diagnostic_fixed':
     hydro=np.full(N,h0);imp=np.full(N,i0);res=load-hydro-imp-g0;short=np.maximum(res,0);surp=np.maximum(-res,0);solver='direct_identity'
    else:
     hc=1.5*h0;ic=i0 if case=='hydro_flex_1p5' else 1.25*i0
     bounds=[(0,hc)]*N+([(i0,i0)]*N if case=='hydro_flex_1p5' else [(0,ic)]*N)+[(0,None)]*(2*N)
     b=np.r_[load-g0,N*DT*h0,N*DT*i0];q=linprog(cost,A_eq=A,b_eq=b,bounds=bounds,method='highs')
     if not q.success:raise RuntimeError((date,shape,case,q.message))
     hydro,imp,short,surp=np.split(q.x,4);solver='scipy_highs_linear_program'
    bal=hydro+imp+g0+short-surp-load
    refs.append(dict(date=date,scenario=shape,case=case,demand_mwh=DT*sum(load),hydro_mwh=DT*sum(hydro),nonhydro_mwh=24*g0,net_import_mwh=DT*sum(imp),diagnostic_unserved_mwh=DT*sum(short),diagnostic_surplus_mwh=DT*sum(surp),max_shortfall_mw=max(short),max_surplus_mw=max(surp),max_balance_error_mw=max(abs(bal)),hydro_daily_energy_error_mwh=DT*sum(hydro)-24*h0,import_daily_energy_error_mwh=DT*sum(imp)-24*i0,solver=solver))
 with (s8/'balancing_daily.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=refs[0].keys());w.writeheader();w.writerows(refs)
 print(json.dumps({'status':'PASS','source':str(source),'observed_days':len(daily),'step7_intervals_per_shape':len(daily)*96,'step8_daily_cases':len(refs)},indent=2))
if __name__=='__main__':main()
