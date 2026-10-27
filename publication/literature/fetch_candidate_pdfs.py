#!/usr/bin/env python3
"""Fetch candidates listed by prior OA metadata lookups, with no API credentials.

This script runs only when the research owner authorizes PDF acquisition.
It never adds downloaded article files to any GitHub commit or artifact.
"""
import argparse
import csv
from pathlib import Path
import re
from find_open_fulltexts import save_pdf

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    root=Path(__file__).resolve().parent
    ap.add_argument("--manifest",type=Path,default=root/"oa_discovery_results.csv")
    ap.add_argument("--out",type=Path,default=root/"oa_discovery_results.csv")
    ap.add_argument("--pdf-dir",type=Path,default=root/"downloaded")
    ap.add_argument("--max-mb",type=int,default=35)
    options=ap.parse_args()
    with options.manifest.open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        fields=reader.fieldnames
        rows=list(reader)
    if options.max_mb<=0:
        ap.error("--max-mb must be positive")
    for row in rows:
        if not row.get("candidate_pdf_url"):
            row["pdf_status"]="no_oa_pdf_candidate"
            continue
        filename=f"{row['id']}_{re.sub(r'[^a-zA-Z0-9._-]+','_',row['doi'])[:90]}.pdf"
        status,sha,size,error=save_pdf(
            row["candidate_pdf_url"],options.pdf_dir/filename,options.max_mb*1024*1024)
        row["pdf_status"]=status
        row["pdf_sha256"]=sha
        row["pdf_bytes"]=str(size or "")
        row["detail"]=(row.get("detail","") + ("; "+error if error else "")).strip("; ")
        print(f"{row['id']}: {status}")
    with options.out.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print("Saved metadata/checksums only; article PDFs stay in excluded local directory.")

if __name__=="__main__":
    main()
