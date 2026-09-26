"""Audit a local bundle of the twelve official KSEB FY2024-25 monthly files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.kseb_monthly_bundle_v1_5 import audit_bundle


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    result = audit_bundle(args.bundle_dir, manifest=args.manifest)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if not result["ready_for_content_schema_audit"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
