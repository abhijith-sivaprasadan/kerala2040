from __future__ import annotations
import argparse,csv,json,math,re
from difflib import SequenceMatcher
from pathlib import Path
from shapely.geometry import shape

ALIASES=dict(x.split('=') for x in """ksebl-hydro-panniar=PNYR-H
ksebl-hydro-poringalkuthu-lbe=PRBE
ksebl-hydro-chembukadavu-1=CMKV-I
ksebl-hydro-chembukadavu-2=CMKV-II
ksebl-hydro-urumi-1=URMI-H-I
ksebl-hydro-urumi-2=URMI-H-II
ksebl-hydro-kuttiyadi-tailrace=KUTR
ksebl-hydro-perunthenaruvi=PMTV-H
ksebl-hydro-peruvannamuzhy=PVMZ
ksebl-solar-kanjikode-ss=KJKD-S
ksebl-solar-kollengode-ss=KEKD-S
ksebl-solar-edayar-ss=EDYR-S
ksebl-solar-pezhekkappally=MVPA-S
ksebl-solar-pothencode=PCOD-S
ksebl-solar-agali=AGLI-S
ksebl-solar-kanjikkode-gm=KJKD-S
thermal-cpp-phillips-carbon-black=PCBL
thermal-central-ntpc-kayamkulam=KYKM
wind-cpp-malayala-manorama=MMWM-W
wind-ipp-inox=INOX-W
solar-other-hindalco=HDIL
solar-other-cial-prosumer=CIAL
solar-other-kmrl=KMRL
solar-other-saint-gobain=STGB
solar-ipp-anert-kuzhalmandam=KZMN
solar-ipp-rpckl-ambalathara=ABTA-S
solar-ipp-thdcil-paivalike=PVLK
solar-ipp-ntpc-kayamkulam-floating=KYLM-S
solar-ipp-cial-ettukudikka=ETKD""".splitlines())
DIRECT={'ksebl-thermal-bdpp':'BRPM','ksebl-solar-brahmapuram':'BRPM'}
PHYSICAL={'station','farm','station_or_farm','station_precise_unit_sum'}
GENERIC={'hep','shep','hydel','power','project','plant','station','substation','solar','spp','wind','farm','gm','scheme','prosumer','ltd','limited','co','generation'}

def write_csv(p,rows):
    fields=[]
    for r in rows:
        for k in r:
            if k not in fields:fields.append(k)
    with Path(p).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def hav(a,b):
    lon1,lat1=a;lon2,lat2=b;R=6371.0088;p1,p2=math.radians(lat1),math.radians(lat2);dp=math.radians(lat2-lat1);dl=math.radians(lon2-lon1);h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2;return 2*R*math.atan2(math.sqrt(h),math.sqrt(1-h))
def norm(s):
    t=str(s or '').lower().replace('&',' and ')
    for a,b in [('kuttiady','kuttiyadi'),('madupetty','mattupetty'),('kollemcode','kollengode'),('perumthenaruvi','perunthenaruvi'),('peruvannamozhi','peruvannamuzhy'),('pathamkayam','pathankayam'),('meenvallam','meenvallom'),('irutukanam','iruttukkanam')]:t=t.replace(a,b)
    return ' '.join(re.sub(r'[^a-z0-9]+',' ',t).split())
def signal(s):return ' '.join(x for x in norm(s).split() if x not in GENERIC)
def qual(s):
    n=norm(s);return {q for q in ['extension','additional','tailrace','micro','new','stage i','stage ii','left bank'] if q in n}
def score(a,b):
    aa,bb=signal(a),signal(b)
    if not aa or not bb:return 0.0
    sm=SequenceMatcher(None,aa,bb).ratio();ta,tb=set(aa.split()),set(bb.split());j=len(ta&tb)/len(ta|tb) if ta|tb else 0
    if aa==bb:sm=1.0
    if aa in bb or bb in aa:sm=max(sm,.92)
    if qual(a)!=qual(b) and (qual(a) or qual(b)):sm-=.28
    return max(0,.65*sm+.35*j)
def compatible(a,s):
    t=str(a.get('technology') or '').lower();typ=str(s.get('type') or '').lower()
    if t=='hydro' and not any(x in typ for x in ['hydel','ipp','cpp']):return False
    if t=='thermal' and 'thermal' not in typ and 'cpp' not in typ:return False
    if t=='wind' and 'wind' not in typ:return False
    if t=='solar' and 'solar' not in typ and s.get('code') not in {'CIAL','KMRL','HDIL','STGB','PCBL','KYKM'}:return False
    if str(a.get('owner') or '').upper()=='KSEBL' and str(s.get('owner') or '').upper() not in {'KSEBL',''}:return False
    return True
def blank_bus(r,status):
    r.update({'bus_attachment_status':status,'network_node_id':'','network_node_location':'','network_node_code':'','network_node_kind':'','network_node_voltage_class_kv':'','network_node_district':'','site_to_bus_distance_km':''})

def main():
    p=argparse.ArgumentParser();p.add_argument('--census',type=Path,default=Path('results/inventory/fy2024_25_generator_census/generator_census.csv'));p.add_argument('--acquisition',type=Path,default=Path('results/acquisition/network_public_v0_1'));p.add_argument('--topology',type=Path,default=Path('results/network/public_grid_topology_v0_2/network_topology_110plus.json'));p.add_argument('--out',type=Path,default=Path('results/network/generator_bus_crosswalk_v0_1'));a=p.parse_args()
    with a.census.open(encoding='utf-8') as f:assets=list(csv.DictReader(f))
    gj=json.loads((a.acquisition/'geojson/GeneratingStations_17.geojson').read_text(encoding='utf-8'));sites=[]
    for f in gj['features']:
        q=f.get('properties') or {};g=shape(f['geometry']);sites.append({'location':str(q.get('Location') or ''),'code':str(q.get('Code') or ''),'status':str(q.get('Status') or ''),'owner':str(q.get('Owner') or ''),'type':str(q.get('Type') or ''),'lon':float(g.x),'lat':float(g.y)})
    site_by_code={s['code']:s for s in sites};topo=json.loads(a.topology.read_text(encoding='utf-8'));nodes=topo['nodes'];node_by_code={}
    for n in nodes:
        if n.get('code'):node_by_code.setdefault(str(n['code']),[]).append(n)
    out=[]
    for x in assets:
        cap=float(x['capacity_mw']);r={k:x.get(k,'') for k in ['asset_id','plant','technology','owner','commercial_class','capacity_basis']};r['capacity_mw']=cap;basis=x.get('capacity_basis','')
        if basis not in PHYSICAL:
            r.update({'site_match_status':'AGGREGATE_NOT_PUBLIC_SITE_MAPPABLE','site_match_method':'','site_match_score':'','site_match_margin':'','public_generation_location':'','public_generation_code':'','public_generation_status':'','public_generation_type':'','public_generation_owner':'','public_generation_lon':'','public_generation_lat':'','review_candidate_location':'','review_candidate_code':''});blank_bus(r,'NOT_ATTEMPTED_AGGREGATE');out.append(r);continue
        aid=x['asset_id']
        if aid in DIRECT:
            ns=node_by_code.get(DIRECT[aid],[]);n=max(ns,key=lambda z:z.get('voltage_class_kv') or 0) if ns else None;r.update({'site_match_status':'DIRECT_PUBLIC_SUBSTATION_ALIAS','site_match_method':'EXPLICIT_NAMED_SITE_ALIAS','site_match_score':'','site_match_margin':'','public_generation_location':'','public_generation_code':'','public_generation_status':'','public_generation_type':'','public_generation_owner':'','public_generation_lon':'','public_generation_lat':'','review_candidate_location':'','review_candidate_code':''})
            if n:r.update({'bus_attachment_status':'DIRECT_NAMED_SUBSTATION','network_node_id':n['node_id'],'network_node_location':n.get('location',''),'network_node_code':n.get('code',''),'network_node_kind':n.get('kind',''),'network_node_voltage_class_kv':n.get('voltage_class_kv',''),'network_node_district':n.get('district',''),'site_to_bus_distance_km':0})
            else:blank_bus(r,'NO_PUBLIC_SITE')
            out.append(r);continue
        chosen=None;method='';best=margin=0;review=None
        if ALIASES.get(aid) in site_by_code:chosen=site_by_code[ALIASES[aid]];method='EXPLICIT_PUBLIC_CODE_ALIAS';best=margin=1.0
        else:
            ranked=sorted(((score(x.get('plant'),s['location']),s) for s in sites if compatible(x,s)),key=lambda z:(-z[0],z[1]['code']))
            if ranked:
                best,review=ranked[0];margin=best-(ranked[1][0] if len(ranked)>1 else 0)
                if best>=.68 and margin>=.12:chosen=review;method='STRICT_NAME_MATCH'
        if not chosen:
            r.update({'site_match_status':'NO_ADMITTED_PUBLIC_GENERATION_MATCH','site_match_method':'REVIEW_ONLY_NAME_CANDIDATE','site_match_score':best,'site_match_margin':margin,'public_generation_location':'','public_generation_code':'','public_generation_status':'','public_generation_type':'','public_generation_owner':'','public_generation_lon':'','public_generation_lat':'','review_candidate_location':review['location'] if review else '','review_candidate_code':review['code'] if review else ''});blank_bus(r,'NO_PUBLIC_SITE');out.append(r);continue
        conflict='proposed' in chosen['status'].lower();r.update({'site_match_status':'PUBLIC_STATUS_CONFLICT' if conflict else 'PUBLIC_GENERATION_SITE_MATCHED','site_match_method':method,'site_match_score':best,'site_match_margin':margin,'public_generation_location':chosen['location'],'public_generation_code':chosen['code'],'public_generation_status':chosen['status'],'public_generation_type':chosen['type'],'public_generation_owner':chosen['owner'],'public_generation_lon':chosen['lon'],'public_generation_lat':chosen['lat'],'review_candidate_location':'','review_candidate_code':''})
        if conflict:blank_bus(r,'BLOCKED_BY_STATUS_CONFLICT');out.append(r);continue
        candidates=[]
        for n in node_by_code.get(chosen['code'],[]):candidates.append((hav((chosen['lon'],chosen['lat']),(n['lon'],n['lat'])),'EXACT_PUBLIC_CODE_WITHIN_2KM',n))
        root=re.split(r'[-_]',chosen['code'])[0]
        if not candidates:
            for n in node_by_code.get(root,[]):candidates.append((hav((chosen['lon'],chosen['lat']),(n['lon'],n['lat'])),'DERIVED_PUBLIC_CODE_ROOT_WITHIN_2KM',n))
        candidates.sort(key=lambda z:z[0]);picked=candidates[0] if candidates and candidates[0][0]<=2 else None
        if not picked:
            near=min(((hav((chosen['lon'],chosen['lat']),(n['lon'],n['lat'])),n) for n in nodes),key=lambda z:z[0])
            if near[0]<=.25:picked=(near[0],'COLOCATED_WITHIN_250M',near[1])
        if not picked:blank_bus(r,'PUBLIC_SITE_NOT_ON_110PLUS_GRAPH')
        else:
            d,how,n=picked;r.update({'bus_attachment_status':how,'network_node_id':n['node_id'],'network_node_location':n.get('location',''),'network_node_code':n.get('code',''),'network_node_kind':n.get('kind',''),'network_node_voltage_class_kv':n.get('voltage_class_kv',''),'network_node_district':n.get('district',''),'site_to_bus_distance_km':d})
        out.append(r)
    a.out.mkdir(parents=True,exist_ok=True);write_csv(a.out/'generator_bus_crosswalk.csv',out)
    physical=[r for r in out if r['capacity_basis'] in PHYSICAL];aggregate=[r for r in out if r['capacity_basis'] not in PHYSICAL];matched=[r for r in out if r['site_match_status']=='PUBLIC_GENERATION_SITE_MATCHED'];attached=[r for r in out if r.get('network_node_id')]
    qa={'classification':'FY2024_25_GENERATOR_TO_KSEBL_PUBLIC_GRID_V0_1_QA','census_rows':len(out),'census_capacity_mw':sum(r['capacity_mw'] for r in out),'physical_asset_rows':len(physical),'public_generation_site_matches':len(matched),'public_generation_site_matched_capacity_mw':sum(r['capacity_mw'] for r in matched),'bus_attached_assets':len(attached),'bus_attached_capacity_mw':sum(r['capacity_mw'] for r in attached),'aggregate_unallocated_rows':len(aggregate),'aggregate_unallocated_capacity_mw':sum(r['capacity_mw'] for r in aggregate),'aggregate_rows_attached_to_bus':sum(bool(r.get('network_node_id')) for r in aggregate),'status_conflict_rows':sum(r['site_match_status']=='PUBLIC_STATUS_CONFLICT' for r in out),'model_ready':False}
    (a.out/'generator_bus_crosswalk_qa.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8');print(json.dumps(qa,indent=2))
if __name__=='__main__':main()
