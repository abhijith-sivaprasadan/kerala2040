"""Produce an audit report and fail closed when a requested release gate is not met."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.audit_readiness import build_audit, markdown_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output", type=Path, default=Path("results/audit/"),
    )
    parser.add_argument(
        "--require-gate", default=None,
        help="Optional gate to require. Exit 2 if not fully verified.",
    )
    args = parser.parse_args()
    audit = build_audit(args.root)
    if args.require_gate and args.require_gate not in audit["release_gates"]:
        parser.error(f"Unknown gate {args.require_gate}")
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    (output / "readiness.json").write_text(
        json.dumps(audit, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (output / "readiness.md").write_text(
        markdown_report(audit), encoding="utf-8"
    )
    blocked = [
        name for name, gate in audit["release_gates"].items() if not gate["passed"]
    ]
    print(json.dumps({
        "evidence_scope": audit["evidence_limit"],
        "open_findings": audit["open_findings"],
        "closed_findings": audit["closed_findings"],
        "blocked_release_gates": blocked,
        "output": str(output),
    }, indent=2))
    if args.require_gate:
        return 0 if audit["release_gates"][args.require_gate]["passed"] else 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
