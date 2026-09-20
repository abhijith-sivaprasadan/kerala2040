"""Diagnose WDPA Kerala polygon/point completeness without downloading geometry."""
from __future__ import annotations

import json
from pathlib import Path

import requests

BASE = ("https://data-gis.unep-wcmc.org/server/rest/services/"
        "ProtectedSites/The_World_Database_of_Protected_Areas")
ENVELOPE = "74.75,8.15,77.55,12.9"

def probe(session, service, layer, where, spatial):
    url = f"{BASE}/{service}/{layer}/query"
    params = {"where": where, "returnIdsOnly": "true", "f": "json"}
    if spatial:
        params.update(geometry=ENVELOPE, geometryType="esriGeometryEnvelope",
                      inSR="4326", spatialRel="esriSpatialRelIntersects")
    try:
        response = session.get(url, params=params, timeout=(15, 90))
        response.raise_for_status()
        result = response.json()
        if "error" in result:
            return {"error": result["error"], "url": url, "where": where,
                    "spatial": spatial}
        ids = result.get("objectIds")
        if not isinstance(ids, list):
            return {"error": "no objectIds", "keys": list(result), "where": where,
                    "spatial": spatial}
        return {"count": len(ids), "preview_ids": ids[:12],
                "duplicates": len(ids)-len(set(ids)), "where": where,
                "spatial": spatial, "service": service, "layer": layer}
    except (requests.RequestException, ValueError) as exc:
        return {"error_type": type(exc).__name__, "details": str(exc)[:250],
                "where": where, "spatial": spatial, "service": service,
                "layer": layer}

def count_query(session, service, layer, spatial):
    params = {"where": "1=1", "returnCountOnly": "true", "f": "json"}
    if spatial:
        params.update(geometry=ENVELOPE, geometryType="esriGeometryEnvelope",
                      inSR="4326", spatialRel="esriSpatialRelIntersects")
    response = session.get(f"{BASE}/{service}/{layer}/query",
                           params=params, timeout=(15,90))
    response.raise_for_status()
    data = response.json()
    return {"service":service, "layer":layer, "spatial":spatial,
            "unfiltered_count":data.get("count"),
            "error":data.get("error")}


def main():
    s = requests.Session()
    s.headers["User-Agent"] = "Kerala2040Research/1.0"
    records = []
    for service in ("MapServer", "FeatureServer"):
        for layer in (0,1):
            for where in ("iso3='IND'", "prnt_iso3='IND'",
                          "name_eng LIKE '%Periyar%'",
                          "name_eng LIKE '%Wayanad%'"):
                records.append(probe(s,service,layer,where,where in
                                     ("iso3='IND'","prnt_iso3='IND'")))
    for service in ("MapServer", "FeatureServer"):
        for layer in (0,1):
            for spatial in (False,True):
                records.append(count_query(s,service,layer,spatial))
    p = Path("results/gis/wdpa_source_diagnostic.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(records,indent=2)+"\n")
    print("WDPA_DIAGNOSTIC="+json.dumps(records, separators=(",",":")),flush=True)

if __name__ == "__main__":
    main()
