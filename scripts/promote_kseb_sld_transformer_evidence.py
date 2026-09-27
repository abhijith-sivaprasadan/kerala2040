from __future__ import annotations
import argparse,csv,json,re
from collections import defaultdict
from pathlib import Path

PAIR=re.compile(r'(?<!\d)(400|320|230|220|110|66|33|22|11)\s*/\s*(400|320|230|220|110|66|33|22|11)\s*k\s*v\b',re.I)
RATING=re.compile(r'(?<![\d.])((?:\d+(?:\.\d+)?\s*/\s*)*\d+(?:\.\d+)?)\s*M\s*V\s*A\b',re.I)
TERM=re.compile(r'\b(?:AUTO\s*TRANSFORMER|POWER\s*TRANSFORMER|TRANSFORMER|TFR\.?|TR\.?)\b',re.I)

def write_csv(path,rows):
    fields=[]
    for row in rows:
        for key in row:
            if key not in fields: fields.append(key)
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def centre(m): return (m.start()+m.end())/2

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--sld-mining',type=Path,default=Path('results/network/public_sld_mining_v0_1/sld_equipment_mining.json'))
    p.add_argument('--out',type=Path,default=Path('results/network/public_transformer_evidence_v0_1'))
    a=p.parse_args()
    data=json.loads(a.sld_mining.read_text(encoding='utf-8'))
    evidence=[]; review=[]; seen=set()
    for rec in data['records']:
        m=rec.get('mining') or {}
        if not m.get('extractable_text'): continue
        for hit in m.get('mva_hits') or []:
            text=str(hit.get('context') or '')
            rms=list(RATING.finditer(text)); pms=list(PAIR.finditer(text)); tms=list(TERM.finditer(text))
            if not rms: continue
            target=float(hit.get('value') or 0)
            rm=min(rms,key=lambda x:(0 if target in [float(v) for v in re.split(r'\s*/\s*',x.group(1))] else 1,abs(centre(x)-len(text)/2)))
            vals=[float(v) for v in re.split(r'\s*/\s*',rm.group(1))]
            pm=min(pms,key=lambda x:abs(centre(x)-centre(rm))) if pms else None
            tm=min(tms,key=lambda x:abs(centre(x)-centre(rm))) if tms else None
            reason=''
            if min(vals)<0.25 or max(vals)>1000: reason='RATING_OUTSIDE_PLAUSIBLE_RANGE'
            elif pm is None or abs(centre(pm)-centre(rm))>105: reason='NO_NEARBY_EXPLICIT_VOLTAGE_PAIR'
            elif tm is None or abs(centre(tm)-centre(rm))>115: reason='NO_NEARBY_TRANSFORMER_TERM'
            if reason:
                review.append({'code':rec.get('code',''),'location':rec.get('location',''),'pdf_filename':rec.get('pdf_filename',''),'mva_value':target,'reason':reason,'context':text})
                continue
            volts=tuple(sorted({int(pm.group(1)),int(pm.group(2))},reverse=True))
            key=(rec.get('code',''),volts,tuple(vals))
            if len(volts)!=2 or key in seen: continue
            seen.add(key)
            evidence.append({'code':rec.get('code',''),'location':rec.get('location',''),'class':rec.get('class',''),'status':rec.get('status',''),'owner':rec.get('owner',''),'type':rec.get('type',''),'pdf_filename':rec.get('pdf_filename',''),'voltage_levels_kv':';'.join(map(str,volts)),'rating_values_mva':';'.join(f'{v:g}' for v in vals),'admission_class':'HIGH_CONFIDENCE_TEXT_TUPLE','context':text})
    by=defaultdict(list)
    for row in evidence: by[(row['code'],row['location'],row['class'],row['status'],row['owner'],row['type'])].append(row)
    stations=[]
    for key,rows in sorted(by.items()):
        volts=[]
        for row in rows:
            for v in row['voltage_levels_kv'].split(';'):
                if v not in volts: volts.append(v)
        stations.append({'code':key[0],'location':key[1],'class':key[2],'status':key[3],'owner':key[4],'type':key[5],'bus_voltage_levels_kv':';'.join(volts),'transformer_evidence_tuples':len(rows),'exact_equipment_count_known':False})
    a.out.mkdir(parents=True,exist_ok=True)
    write_csv(a.out/'transformer_evidence.csv',evidence);write_csv(a.out/'transformer_review_queue.csv',review);write_csv(a.out/'station_bus_inventory.csv',stations)
    qa={'classification':'KSEBL_PUBLIC_SLD_TRANSFORMER_PROMOTION_V0_1_QA','high_confidence_transformer_evidence_records':len(evidence),'stations_with_promoted_transformer_evidence':len(stations),'review_queue_records':len(review),'automatic_ocr_used':False,'equipment_master_ready':False}
    (a.out/'transformer_promotion_qa.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(qa,indent=2))
if __name__=='__main__':main()
