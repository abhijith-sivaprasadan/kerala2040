from __future__ import annotations
import argparse, csv, hashlib, json, math, re
from collections import Counter, defaultdict, deque
from pathlib import Path
from shapely.geometry import Point, shape
from shapely.ops import nearest_points

FEEDER_FILES={110:'110kVFeederInservice_11.geojson',220:'220kVFeederInservice_13.geojson',320:'320kVFeederInservice_14.geojson',400:'400kVFeederInservice_16.geojson'}

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def norm(v):
    t=str(v or '').lower().replace('&',' and '); t=re.sub(r'\b(?:no\.?|number)\b',' ',t); t=re.sub(r'\b(?:i|ii|iii|iv|v)\b',' ',t); t=re.sub(r'[^a-z0-9]+',' ',t); return ' '.join(t.split())
def tokens(v):
    stop={'to','kv','sub','station','gs','hep','shep','no','pgcil','ksebl','line','feeder'}
    return {x for x in norm(v).split() if x not in stop and len(x)>2}
def overlap(a,b):
    aa,bb=tokens(a),tokens(b); return len(aa&bb)/len(aa|bb) if aa and bb else 0.0
def hav(a,b):
    lon1,lat1=a; lon2,lat2=b; R=6371.0088; p1,p2=map(math.radians,[lat1,lat2]); dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1); h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2; return 2*R*math.atan2(math.sqrt(h),math.sqrt(1-h))
def parts(g):
    if g.is_empty:return []
    if g.geom_type=='LineString':return [list(g.coords)]
    if g.geom_type=='MultiLineString':return [list(x.coords) for x in g.geoms if not x.is_empty]
    return []
def endpoints(g):
    ps=parts(g); return [tuple(ps[0][0]),tuple(ps[-1][-1])] if ps and ps[0] and ps[-1] else []
def glen(g):
    return sum(hav(tuple(a),tuple(b)) for ps in parts(g) for a,b in zip(ps,ps[1:]))
def write_csv(p,rows):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
def match_endpoint(pt,name,kv,nodes):
    ranked=[]
    for n in nodes:
        d=hav(pt,(float(n['lon']),float(n['lat']))); ranked.append((d,-overlap(name,n.get('location')), -(n.get('voltage_class_kv')==kv),n))
    ranked.sort(key=lambda x:(round(x[0],6),x[1],x[2],x[3]['node_id']))
    best=ranked[0]; window=[x for x in ranked if x[0]<=best[0]+0.20]
    window.sort(key=lambda x:(-overlap(name,x[3].get('location')),-(x[3].get('voltage_class_kv')==kv),x[0],x[3]['node_id']))
    chosen=window[0]; th=0.25 if kv>=220 else 1.0
    return {'node_id':chosen[3]['node_id'] if chosen[0]<=th else None,'distance_km':chosen[0],'nearest_location':chosen[3].get('location',''),'name_overlap':overlap(name,chosen[3].get('location')),'method':'PUBLIC_NODE_SNAP' if chosen[0]<=th else 'UNRESOLVED'}
def jid(pt):
    raw=f'{pt.x:.6f},{pt.y:.6f}'.encode(); return 'J110:'+hashlib.sha1(raw).hexdigest()[:10]
def components(node_ids,edges):
    adj=defaultdict(set)
    for e in edges:
        a,b=e['from_node_id'],e['to_node_id']; adj[a].add(b); adj[b].add(a)
    seen=set(); out=[]
    for n in sorted(node_ids):
        if n in seen or n not in adj: continue
        q=deque([n]); seen.add(n); c=[]
        while q:
            x=q.popleft(); c.append(x)
            for y in adj[x]:
                if y not in seen: seen.add(y); q.append(y)
        out.append(sorted(c))
    return sorted(out,key=len,reverse=True)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--acquisition',type=Path,default=Path('results/acquisition/network_public_v0_1')); ap.add_argument('--graph-v01',type=Path,default=Path('results/network/public_grid_graph_v0_1/network_graph_110plus.json')); ap.add_argument('--out',type=Path,default=Path('results/network/public_grid_topology_v0_2')); args=ap.parse_args()
    geo=args.acquisition/'geojson'; g01=load(args.graph_v01); base_nodes=[dict(x) for x in g01['nodes']]
    source=[]; geoms={}; endpoint_pts={}; anomalies=[]
    for kv,fn in FEEDER_FILES.items():
        obj=load(geo/fn)
        for i,feat in enumerate(obj['features']):
            pr=feat.get('properties') or {}; name=str(pr.get('Name') or ''); code=str(pr.get('Feeder') or i).strip(); sid=f'{kv}:{code}:{i:04d}'
            try:g=shape(feat.get('geometry')) if feat.get('geometry') else None
            except Exception:g=None
            valid=bool(g and not g.is_empty and g.geom_type in {'LineString','MultiLineString'} and len(endpoints(g))==2)
            length=glen(g) if valid else 0.0
            sl=pr.get('Length_km'); sl=float(sl) if sl not in (None,'') else None
            row={'source_edge_id':sid,'source_feature_index':i,'name':name,'feeder_code':code,'voltage_kv':kv,'status':str(pr.get('Status') or ''),'owner':str(pr.get('Owner') or ''),'station_code':str(pr.get('Station') or ''),'source_file':fn,'source_length_km':sl,'geometry_length_km':length}
            if not valid:
                row.update({'from_node_id':None,'to_node_id':None,'from_distance_km':None,'to_distance_km':None,'from_nearest_location':None,'to_nearest_location':None,'from_name_overlap':None,'to_name_overlap':None,'from_resolution_method':None,'to_resolution_method':None,'endpoint_resolution':'INVALID_GEOMETRY','topology_admitted':False})
                anomalies.append({'source_edge_id':sid,'anomaly':'INVALID_OR_EMPTY_GEOMETRY','name':name,'voltage_kv':kv,'geometry_length_km':None}); source.append(row); continue
            ep=endpoints(g); a=match_endpoint(ep[0],name,kv,base_nodes); b=match_endpoint(ep[1],name,kv,base_nodes)
            row.update({'from_node_id':a['node_id'],'to_node_id':b['node_id'],'from_distance_km':a['distance_km'],'to_distance_km':b['distance_km'],'from_nearest_location':a['nearest_location'],'to_nearest_location':b['nearest_location'],'from_name_overlap':a['name_overlap'],'to_name_overlap':b['name_overlap'],'from_resolution_method':a['method'],'to_resolution_method':b['method']})
            if length<0.01:
                row.update({'endpoint_resolution':'DEGENERATE_GEOMETRY','topology_admitted':False}); anomalies.append({'source_edge_id':sid,'anomaly':'DEGENERATE_GEOMETRY','name':name,'voltage_kv':kv,'geometry_length_km':length})
            else:
                row.update({'endpoint_resolution':'RESOLVED' if a['node_id'] and b['node_id'] else 'UNRESOLVED','topology_admitted':False})
                geoms[sid]=g; endpoint_pts[(sid,'from')]=Point(ep[0]); endpoint_pts[(sid,'to')]=Point(ep[1])
            source.append(row)
    sby={r['source_edge_id']:r for r in source}
    junction_hits=defaultdict(list)
    for row in source:
        if row['voltage_kv']!=110 or row['endpoint_resolution'] in {'INVALID_GEOMETRY','DEGENERATE_GEOMETRY'}: continue
        sid=row['source_edge_id']
        for side in ('from','to'):
            if row[f'{side}_node_id']: continue
            p=endpoint_pts[(sid,side)]; best=None
            for other,g in geoms.items():
                if other==sid or sby[other]['voltage_kv']!=110: continue
                q=nearest_points(p,g)[1]; d=hav((p.x,p.y),(q.x,q.y))
                if best is None or d<best[0]: best=(d,other,q)
            if best and best[0]<=0.15:
                d,parent,q=best; key=jid(q); row[f'{side}_node_id']=key; row[f'{side}_resolution_method']='FEEDER_GEOMETRY_JUNCTION'; row[f'{side}_junction_parent_edge_id']=parent; row[f'{side}_junction_distance_to_parent_km']=d; junction_hits[key].append((sid,side,p,parent,q,d))
    junction_points={k:h[0][4] for k,h in junction_hits.items()}
    raw_items=list(junction_points.items()); clusters=[]
    for old_id,p in raw_items:
        for cl in clusters:
            cx=sum(x[1].x for x in cl)/len(cl); cy=sum(x[1].y for x in cl)/len(cl)
            if hav((p.x,p.y),(cx,cy))<=0.05:
                cl.append((old_id,p)); break
        else: clusters.append([(old_id,p)])
    remap={}; clustered_points={}; clustered_hits=defaultdict(list)
    for cl in clusters:
        x=sum(p.x for _,p in cl)/len(cl); y=sum(p.y for _,p in cl)/len(cl); cp=Point(x,y); new_id=jid(cp)
        clustered_points[new_id]=cp
        for old_id,_ in cl:
            remap[old_id]=new_id; clustered_hits[new_id].extend(junction_hits[old_id])
    junction_points=clustered_points; junction_hits=clustered_hits
    for r in source:
        for side in ('from','to'):
            if isinstance(r.get(f'{side}_node_id'),str) and r[f'{side}_node_id'].startswith('J110:'):
                r[f'{side}_node_id']=remap[r[f'{side}_node_id']]
    parent_split_points=defaultdict(list)
    for j,p in junction_points.items():
        parents=sorted({hit[3] for hit in junction_hits[j]})
        for sid in parents:
            q=nearest_points(p,geoms[sid])[1]
            parent_split_points[sid].append(q)
    jnodes=[]
    for j,p in sorted(junction_points.items()):
        nearest=min(base_nodes,key=lambda n:hav((p.x,p.y),(float(n['lon']),float(n['lat']))))
        jnodes.append({'node_id':j,'kind':'junction','location':'110 kV feeder geometry junction','code':'','voltage_class_kv':110,'status':'derived from in-service feeder geometry','owner':'KSEBL','type':'geometry junction','group':'110 kV topology','sld_html':'','lon':p.x,'lat':p.y,'district':nearest.get('district'),'synthetic':True,'junction_evidence_endpoint_count':len(junction_hits[j])})
    all_nodes=base_nodes+jnodes
    for r in source:
        if r['endpoint_resolution'] not in {'INVALID_GEOMETRY','DEGENERATE_GEOMETRY'}:
            r['endpoint_resolution']='RESOLVED' if r.get('from_node_id') and r.get('to_node_id') else 'UNRESOLVED'
            r['topology_admitted']=r['endpoint_resolution']=='RESOLVED'
    topo=[]
    for r in source:
        if not r['topology_admitted']: continue
        sid=r['source_edge_id']; g=geoms[sid]; total_geom=r['geometry_length_km'] or 0.0
        if r['voltage_kv']==110:
            seen=[]
            for p in parent_split_points.get(sid,[]):
                pos=g.project(p,normalized=True)
                if pos*total_geom>0.01 and (1-pos)*total_geom>0.01 and all(abs(pos-x)>1e-7 for x in seen): seen.append(pos)
            seen.sort()
        else: seen=[]
        cuts=[0.0]+seen+[1.0]; node_seq=[r['from_node_id']]
        for pos in seen:
            q=g.interpolate(pos,normalized=True)
            j=min(junction_points,key=lambda k:hav((q.x,q.y),(junction_points[k].x,junction_points[k].y)))
            node_seq.append(j)
        node_seq.append(r['to_node_id'])
        for idx,(a,b) in enumerate(zip(cuts,cuts[1:]),1):
            try:
                from shapely.ops import substring
                sg=substring(g,a,b,normalized=True); seglen=glen(sg)
            except Exception:
                seglen=total_geom*(b-a)
            frac=seglen/total_geom if total_geom else (b-a)
            topo.append({'topology_edge_id':f'{sid}:seg{idx:02d}','source_edge_id':sid,'segment_index':idx,'name':r['name'],'feeder_code':r['feeder_code'],'voltage_kv':r['voltage_kv'],'status':r['status'],'owner':r['owner'],'from_node_id':node_seq[idx-1],'to_node_id':node_seq[idx],'geometry_length_km':seglen,'source_length_km_allocated':(r['source_length_km']*frac if r['source_length_km'] is not None else None),'segment_fraction':frac,'split_by_geometry_junction':(len(seen)>0 or str(node_seq[idx-1]).startswith('J110:') or str(node_seq[idx]).startswith('J110:'))})
    deg=Counter()
    for e in topo:deg[e['from_node_id']]+=1;deg[e['to_node_id']]+=1
    nodes=[n for n in all_nodes if n['node_id'] in deg]
    for n in nodes:n['degree']=deg[n['node_id']]
    comps=components(set(deg),topo)
    unresolved=Counter(r['voltage_kv'] for r in source if r['endpoint_resolution']=='UNRESOLVED')
    qa={'classification':'KSEBL_PUBLIC_GRID_TOPOLOGY_V0_2_QA','source_features':len(source),'source_anomalies':len(anomalies),'admitted_source_edges':sum(bool(r['topology_admitted']) for r in source),'topology_segments':len(topo),'synthetic_110kv_junctions':len(jnodes),'unresolved_admissible_edges_by_voltage':dict(sorted(unresolved.items())),'connected_components_with_edges':len(comps),'largest_component_nodes':len(comps[0]) if comps else 0,'active_nodes':len(nodes),'all_admissible_110plus_endpoints_resolved':sum(unresolved.values())==0,'power_flow_ready':False}
    args.out.mkdir(parents=True,exist_ok=True)
    write_csv(args.out/'network_source_edges_110plus.csv',source); write_csv(args.out/'network_topology_edges_110plus.csv',topo); write_csv(args.out/'network_nodes_110plus.csv',nodes); write_csv(args.out/'network_source_anomalies.csv',anomalies)
    (args.out/'network_topology_110plus.json').write_text(json.dumps({'classification':'KSEBL_PUBLIC_GRID_TOPOLOGY_V0_2_PHYSICAL_CONNECTIVITY_NOT_POWER_FLOW_READY','prepared_date':'2026-09-27','nodes':nodes,'source_edges':source,'topology_edges':topo,'source_anomalies':anomalies,'components':comps,'warnings':['Synthetic junctions are derived only where published in-service 110-kV feeder endpoints land on another published 110-kV feeder geometry.','Source anomalies are quarantined rather than repaired by guesswork.','Transformer/bus structure, branch electrical parameters and load chronology remain separate gates.']},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (args.out/'network_topology_qa.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8'); print(json.dumps(qa,indent=2))
if __name__=='__main__': main()
