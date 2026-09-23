#!/usr/bin/env python3
# ruff: noqa: E701, E702  # Intentional compact offline row extraction loops.
"""Offline, provenance-preserving Kerala SLDC five-section archive normalization.

Input: uploaded collector ZIP of accepted/rejected dated HTML + parsed rows.
Outputs: calendar QA, system day, labelled generation/import rows, reservoir rows,
         extrema rows, source-shaped availability rows, summaries and manifest.
No network. Nothing missing is imputed. MU=1e6 kWh, not MW.
"""
import argparse
import collections
import csv
import datetime
import hashlib
import json
import math
import re
import zipfile
from pathlib import Path

SECTIONS=('statistics','imports','storage','availability','other_extrema')
KEYS={'Generation':'internal_generation_mu','Internal Generation':'internal_generation_mu',
      'Net Import':'net_import_interface_mu','Consumption':'consumption_mu',
      'Hydel Total':'hydel_total_mu','Thermal Total':'thermal_total_mu',
      'IPP Total':'ipp_total_mu','Net Schedule':'net_schedule_mu',
      'CGS AVAILABILITY':'cgs_availability_mu','Unscheduled Interchange (Import +)':'ui_import_net_reported_mu'}
RESERVOIRS={'IDUKKI','PAMBA','KAKKI','SHOLAYAR','IDAMALAYAR','KUNDALA','MADUPPATTY',
 'KUTTIADI','THARIODE','ANAYIRANKAL','PONMUDI','NERIAMANGALAM','PORINGAL',
 'SENGULAM (SBR)','LOWER PERIYAR','KAKKAD'}
AGG={'group i total','groupii total','group iii total','hydel total','thermal total',
     'ipp total','sum: small hydels','sum: wind mills','generation','internal generation',
     'consumption','net import','net schedule','cgs availability','import (mu)','export (mu)',
     'unscheduled interchange (import +)'}
COLUMNS={
 'source_calendar.csv':['date','section','status','reason','schema_variant','row_count','response_sha256','html_path'],
 'daily_system.csv':['date','fy','statistics_status','imports_status','storage_status','availability_status','other_extrema_status',
  'statistics_schema','internal_generation_mu','net_import_interface_mu','consumption_mu',
  'hydel_total_mu','thermal_total_mu','ipp_total_mu','net_schedule_mu','cgs_availability_mu',
  'imports_section_net_import_mu','ui_import_net_reported_mu','balance_error_mu','import_section_difference_mu','energy_balance_qualified','consumption_qualified_mu',
  'morning_peak_mw','morning_peak_time_ist','evening_peak_mw','evening_peak_time_ist',
  'frequency_min_hz','frequency_max_hz','frequency_avg_hz','reservoir_total_storage_mu','reservoir_total_storage_pct',
  'statistics_sha256','imports_sha256','storage_sha256','availability_sha256','other_extrema_sha256'],
 'generation_rows.csv':['date','source_label','source_row','row_class','day_mu','month_cumulative_mu','reported_daily_average_mu','maximum_demand_mw','maximum_demand_time','machines_planned','machines_forced','machines_available','source_sha256'],
 'import_rows.csv':['date','source_label','source_row','row_class','day_mu','month_cumulative_mu','reported_daily_average_mu','source_sha256'],
 'reservoir_rows.csv':['date','reservoir','source_row','minimum_drawdown_m','full_reservoir_level_m','full_storage_mcm','full_storage_mu','level_m','effective_storage_mcm','storage_pct','generation_capability_mu','other_generation_capability_mu','rainfall_mm','inflow_mcm_day','month_inflow_mu','previous_day_storage_pct','source_sha256'],
 'extrema_rows.csv':['date','event','period','quantity','mw','time_from_ist','time_to_ist','frequency_hz','source_sha256'],
 'availability_rows.csv':['date','source_row','source_label','source_columns_json','source_sha256']}

def dec(v):
 s=str(v or '').strip().replace(',','').replace('\x00','')
 if not s or not re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)',s):return None
 x=float(s)
 return x if math.isfinite(x) else None

def val(row,i):return dec(row[i]) if i<len(row) else None

def fy(d):
 y=int(d[:4]);return f'{y if d[5:7]>="04" else y-1}-{str((y+1 if d[5:7]>="04" else y)%100).zfill(2)}'

def status_json(d,day,sec):
 return d.get('accepted') is True and d.get('requested_date')==day and d.get('section')==sec and d.get('source_report_dates')==[day]

def write_csv(path,records,headers):
 with path.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,headers,extrasaction='ignore');w.writeheader();w.writerows(records)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('archive',type=Path)
 ap.add_argument('--out',type=Path,default=Path('Kerala2040_SLDC_Curated_2019_2026'))
 args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
 results={k:[] for k in COLUMNS};errors=[];section_counts=collections.Counter();versions=collections.Counter()
 rawhash=hashlib.sha256(args.archive.read_bytes()).hexdigest()
 with zipfile.ZipFile(args.archive) as z:
  index={x.filename:x for x in z.infolist()};root=next(x.split('/')[0]+'/' for x in index if '/accepted/' in x)
  sourceqa=json.loads(z.read(root+'archive_qa.json'))
  start=datetime.date.fromisoformat(sourceqa['requested_start']);end=datetime.date.fromisoformat(sourceqa['requested_end'])
  day=start
  while day<=end:
   iso=day.isoformat();daily={'date':iso,'fy':fy(iso)}
   for sec in SECTIONS:
    jf=f'{root}accepted/{sec}/{iso}.json';h=f'{root}accepted/{sec}/{iso}.html'
    rj=f'{root}rejected/{sec}/{iso}.json';rh=f'{root}rejected/{sec}/{iso}.html'
    if jf not in index:
     code='rejected' if rj in index else 'uncollected'
     rsn='';hashstr='';rowcount='';htmlpath=''
     if rj in index:
      rd=json.loads(z.read(rj));rsn=';'.join(rd.get('qa_errors') or [])
      hashstr=rd.get('response_sha256','');rowcount=rd.get('table_row_count','');htmlpath=rh
     results['source_calendar.csv'].append({'date':iso,'section':sec,'status':code,'reason':rsn,'row_count':rowcount,'response_sha256':hashstr,'html_path':htmlpath})
     daily[sec+'_status']=code;section_counts[(sec,code)]+=1;continue
    d=json.loads(z.read(jf));reported=d.get('response_sha256');actual=hashlib.sha256(z.read(h)).hexdigest() if h in index else None
    good=status_json(d,iso,sec) and actual==reported and len(d.get('rows',[]))>=5
    if not good:
     errors.append({'date':iso,'section':sec,'accepted_metadata':d.get('accepted'),'returned_date':d.get('source_report_dates'),
                   'json_sha':reported,'computed_html_sha':actual})
     code='checksum_or_date_rejected'
     results['source_calendar.csv'].append({'date':iso,'section':sec,'status':code,'reason':'invalid_metadata_or_html_checksum','row_count':d.get('table_row_count'),'response_sha256':reported,'html_path':h})
     daily[sec+'_status']=code;section_counts[(sec,code)]+=1;continue
    section_counts[(sec,'accepted')]+=1;daily[sec+'_status']='accepted';daily[sec+'_sha256']=reported
    rows=d['rows'];variant=d.get('statistics_schema_variant') or ('station_generation_without_full_energy_balance' if sec=='statistics' and len(rows)<60 else 'full_energy_balance')
    results['source_calendar.csv'].append({'date':iso,'section':sec,'status':'accepted','reason':';'.join(d.get('qa_warnings') or []),'schema_variant':variant if sec=='statistics' else '',
       'row_count':len(rows),'response_sha256':reported,'html_path':h})
    versions[(sec,variant)]+=1
    if sec=='statistics':
     daily['statistics_schema']=variant
     for idx,row in enumerate(rows):
      if len(row)<2:continue
      label=row[0].strip().replace('\x00','');num=val(row,1)
      if label in KEYS and num is not None:daily[KEYS[label]]=num
      if idx<=2 or num is None or not label or label in {'For the month','All time','For the Financial Year','Cumulative figures in mu'}:continue
      if label=='Generation':label='Internal Generation (early-layout source label Generation)'
      results['generation_rows.csv'].append({'date':iso,'source_label':label,'source_row':idx,'row_class':'aggregate' if label.lower() in AGG or label.startswith('Internal Generation (early') else 'source_station_or_other',
         'day_mu':num,'month_cumulative_mu':val(row,2),'reported_daily_average_mu':val(row,3),
         'maximum_demand_mw':val(row,4),'maximum_demand_time':row[5] if len(row)>5 else '',
         'machines_planned':val(row,6),'machines_forced':val(row,7),'machines_available':val(row,8),
         'source_sha256':reported})
    elif sec=='imports':
     for idx,row in enumerate(rows):
      if len(row)<2 or idx<=1:continue
      label=row[0].strip().replace('\x00','');num=val(row,1)
      if label=='Net Import' and num is not None:daily['imports_section_net_import_mu']=num
      if label=='Unscheduled Interchange (Import +)' and num is not None:daily['ui_import_net_reported_mu']=num
      if not label or num is None:continue
      results['import_rows.csv'].append({'date':iso,'source_label':label,'source_row':idx,'row_class':'aggregate' if label.lower() in AGG else 'source_station_or_interface',
         'day_mu':num,'month_cumulative_mu':val(row,2),'reported_daily_average_mu':val(row,3),'source_sha256':reported})
    elif sec=='storage':
     for idx,row in enumerate(rows):
      if len(row)<10 or row[4].strip().upper() not in RESERVOIRS:continue
      results['reservoir_rows.csv'].append({'date':iso,'reservoir':row[4].strip().upper(),'source_row':idx,
        'minimum_drawdown_m':val(row,0),'full_reservoir_level_m':val(row,1),'full_storage_mcm':val(row,2),'full_storage_mu':val(row,3),
        'level_m':val(row,5),'effective_storage_mcm':val(row,6),'storage_pct':val(row,7),
        'generation_capability_mu':val(row,8),'other_generation_capability_mu':val(row,9),
        'rainfall_mm':val(row,10),'inflow_mcm_day':val(row,12),'month_inflow_mu':val(row,13),'previous_day_storage_pct':val(row,14),
        'source_sha256':reported})
     for row in rows:
      if len(row)>5 and row[2].strip()=='TOTAL':
       daily['reservoir_total_storage_pct']=val(row,4);daily['reservoir_total_storage_mu']=val(row,5)
    elif sec=='availability':
     for idx,row in enumerate(rows):
      if idx==0:continue
      label=(row[1] if len(row)>1 and row[1] else row[0] if row else '').strip().replace('\x00','')
      if not label or label=='0' and not any(dec(t) not in (None,0) for t in row):continue
      results['availability_rows.csv'].append({'date':iso,'source_row':idx,'source_label':label,'source_columns_json':json.dumps(row,ensure_ascii=False,separators=(',',':')),'source_sha256':reported})
    elif sec=='other_extrema':
     mode='';period=''
     for idx,row in enumerate(rows):
      if not row:continue
      key=row[0].strip()
      if key.startswith('Maximum Demand'):mode='maximum';period='';continue
      if key=='Minimum Demand':mode='minimum';period='';continue
      if key in ('Morning Peak','Evening Peak'):
       mode='morning_peak' if key=='Morning Peak' else 'evening_peak';period='';continue
      if key=='FREQUENCY':mode='frequency';period='';continue
      if key=='R E C O R D S':mode='records';continue
      if key=='Bus Voltage':mode='voltage';continue
      if mode in ('maximum','minimum') and len(row)>=8 and row[1] in ('Generation','Consumption') and val(row,2) is not None:
       if key:period=key.lower()
       results['extrema_rows.csv'].append({'date':iso,'event':mode,'period':period,'quantity':row[1].lower(),'mw':val(row,2),
         'time_from_ist':row[3],'time_to_ist':row[5],'frequency_hz':val(row,7),'source_sha256':reported})
      if mode=='frequency' and key in ('Maximum','Minimum','Average'):
       if val(row,2) is not None:daily['frequency_'+{'Maximum':'max','Minimum':'min','Average':'avg'}[key]+'_hz']=val(row,2)
      if mode in ('morning_peak','evening_peak') and key=='MW' and val(row,1) is not None:
       daily[mode+'_mw']=val(row,1)
      if mode in ('morning_peak','evening_peak') and key=='Time' and len(row)>1:
       daily[mode+'_time_ist']=row[1]
   a,b,c=[daily.get(k) for k in ('internal_generation_mu','net_import_interface_mu','consumption_mu')]
   if all(x is not None for x in (a,b,c)):
    daily['balance_error_mu']=round(a+b-c,7)
    daily['energy_balance_qualified']=abs(daily['balance_error_mu'])<=0.02
    if daily['energy_balance_qualified']:daily['consumption_qualified_mu']=c
   q=daily.get('imports_section_net_import_mu')
   if b is not None and q is not None:daily['import_section_difference_mu']=round(b-q,7)
   results['daily_system.csv'].append(daily)
   day+=datetime.timedelta(days=1)
 for name,rows in results.items():write_csv(args.out/name,rows,COLUMNS[name])
 dailyrows=results['daily_system.csv'];summaries=[]
 for year in sorted(set(r['fy'] for r in dailyrows)):
  rr=[r for r in dailyrows if r['fy']==year];withc=[r for r in rr if r.get('consumption_qualified_mu') is not None]
  withb=[r for r in rr if r.get('balance_error_mu') is not None];withe=[r for r in rr if r.get('evening_peak_mw') is not None]
  s={'fy':year,'calendar_dates_in_archive':len(rr),'consumption_observed_days':len(withc),
    'observed_consumption_sum_mu':round(sum(r['consumption_qualified_mu'] for r in withc),6),
    'consumption_median_mu_per_reported_day':round(sorted(r['consumption_qualified_mu'] for r in withc)[len(withc)//2],5) if withc else None,
    'balance_days':len(withb),'max_abs_energy_balance_error_mu':max((abs(r['balance_error_mu']) for r in withb),default=None),
    'max_reported_evening_peak_mw':max((r['evening_peak_mw'] for r in withe),default=None),
    'missing_consumption_dates':[r['date'] for r in rr if r.get('consumption_qualified_mu') is None]}
  summaries.append(s)
 with (args.out/'financial_year_summary.csv').open('w',encoding='utf-8',newline='') as f:
  fields=['fy','calendar_dates_in_archive','consumption_observed_days','observed_consumption_sum_mu','consumption_median_mu_per_reported_day','balance_days','max_abs_energy_balance_error_mu','max_reported_evening_peak_mw','missing_consumption_dates']
  w=csv.DictWriter(f,fields);w.writeheader();w.writerows({**s,'missing_consumption_dates':';'.join(s['missing_consumption_dates'])} for s in summaries)
 monthly_summary=[]
 for month in sorted(set(r['date'][:7] for r in dailyrows)):
  rr=[r for r in dailyrows if r['date'].startswith(month)]
  good=[r for r in rr if r.get('consumption_qualified_mu') is not None]
  fractions=[r['net_import_interface_mu']/r['consumption_qualified_mu'] for r in good
    if r.get('net_import_interface_mu') is not None and r['consumption_qualified_mu']>0]
  evening=[r['evening_peak_mw'] for r in rr if r.get('evening_peak_mw') is not None]
  monthly_summary.append({'month':month,'calendar_days_in_archive':len(rr),'qualified_days':len(good),
    'observed_consumption_sum_mu':round(sum(r['consumption_qualified_mu'] for r in good),5),
    'mean_daily_consumption_mu':round(sum(r['consumption_qualified_mu'] for r in good)/len(good),5) if good else None,
    'median_daily_import_share':sorted(fractions)[len(fractions)//2] if fractions else None,
    'maximum_reported_evening_peak_mw':max(evening,default=None)})
 with (args.out/'monthly_summary.csv').open('w',encoding='utf-8',newline='') as f:
  fields=['month','calendar_days_in_archive','qualified_days','observed_consumption_sum_mu','mean_daily_consumption_mu','median_daily_import_share','maximum_reported_evening_peak_mw']
  w=csv.DictWriter(f,fields);w.writeheader();w.writerows(monthly_summary)
 missing_by_section={sec:[r['date'] for r in dailyrows if r.get(sec+'_status')!='accepted'] for sec in SECTIONS}
 fields={'classification':'SLDC_REPORTED_DAILY_OBSERVATIONS_NOT_CONTINUOUS_INTERVAL','source_url':'https://sldckerala.com/index.php',
 'raw_archive_sha256':rawhash,'raw_archive_bytes':args.archive.stat().st_size,'start':str(start),'end':str(end),
 'calendar_days':len(dailyrows),'section_status_counts':{sec:{status:section_counts[(sec,status)] for status in ['accepted','rejected','uncollected','checksum_or_date_rejected']} for sec in SECTIONS},
 'schema_by_section':{'%s:%s'%k:v for k,v in sorted(versions.items())},'normalized_table_rows':{k:len(v) for k,v in results.items()},
 'invalid_accepted_metadata_or_raw_html_sha256':errors,
 'reported_energy_balance_anomalies':[{'date':r['date'],'generation_mu':r.get('internal_generation_mu'),'net_import_mu':r.get('net_import_interface_mu'),'reported_consumption_mu':r.get('consumption_mu'),'balance_error_mu':r.get('balance_error_mu')} for r in dailyrows if r.get('energy_balance_qualified') is False],
 'missing_dates_by_section':missing_by_section,
 'financial_year_summary':summaries,'monthly_summary':{'months':len(monthly_summary),'file':'monthly_summary.csv'},'source_units':{'mu':'million kilowatt-hours','mw':'megawatts','mcm':'million cubic metres','frequency_hz':'hertz'},
 'key_caveats':['Historical 2019–2021 44-row Statistics pages label aggregate Generation, not Internal Generation; do not treat schema gaps as zero.',
 'Imports 2022+ repeats station generation under Imports; never add imported station totals to Statistics station totals.',
 'Reservoir short reports contain first reservoirs only; missing reservoirs and TOTAL are null, not zero.',
 'Availability/Schedule are source-reported ENERGY in MU, not installed or operational MW; rows vary in width and context.',
 'Evening Peak is minute-timed separate statistic from half-hour Evening Maximum Demand.',
 '2019-08-06 is archive chosen start, not verified earliest SLDC date; 2026-09-23 rejected incomplete day.',
 'Daily accepted dated report does not imply each expected subsection is complete; validate field-level coverage.',
 'Qualified consumption excludes reported balance discrepancy >0.02 MU; underlying reported values remain in daily_system.csv.',
 'No actual continuous hourly or 15-minute electricity chronology is in these records.']}
 (args.out/'qa_manifest.json').write_text(json.dumps(fields,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
 print(json.dumps({'raw_archive_sha256':rawhash,'counts':fields['section_status_counts'],'table_rows':fields['normalized_table_rows'],
 'invalid_accepted':len(errors),'fy':[{k:v for k,v in x.items() if k!='missing_consumption_dates'} for x in summaries]},indent=2))
 return 0 if not errors else 2
if __name__=='__main__':raise SystemExit(main())
