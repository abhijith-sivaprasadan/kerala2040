#!/usr/bin/env python
"""Capture the public KSEB project-management generation-project inventory."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

TRACKER = "https://pms.kseb.in/tracker"
EXPLORER = "https://pms.kseb.in/explore-projects"


def _get(url: str) -> str:
    response = requests.get(
        url,
        timeout=45,
        headers={"User-Agent": "Kerala2040Research/1.0 (+https://github.com/abhijith-sivaprasadan/kerala2040)"},
    )
    response.raise_for_status()
    return response.text


def _lines(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    return [" ".join(x.split()) for x in soup.stripped_strings if " ".join(x.split())]


def parse_tracker(html: str) -> dict[str, Any]:
    text = "\n".join(_lines(html))
    data_as_of = None
    match = re.search(r"Data as of\s+([^\n]+)", text, re.I)
    if match:
        data_as_of = match.group(1).strip()
    ongoing = re.search(r"(\d+)\s+Ongoing Projects", text, re.I)
    completed = re.search(r"(\d+)\s+Completed Projects", text, re.I)
    added = re.search(r"Capacity Being Added\s+([\d.]+)\s*MW", text, re.I)
    installed = re.search(r"Installed Capacity\s+([\d.]+)\s*MW", text, re.I)
    return {
        "data_as_of_label": data_as_of,
        "ongoing_projects": int(ongoing.group(1)) if ongoing else None,
        "completed_projects": int(completed.group(1)) if completed else None,
        "capacity_being_added_mw": float(added.group(1)) if added else None,
        "installed_capacity_mw": float(installed.group(1)) if installed else None,
    }


def parse_projects(html: str) -> list[dict[str, Any]]:
    lines = _lines(html)
    projects: list[dict[str, Any]] = []
    seen: set[str] = set()
    state_re = re.compile(r"^(Hydro|Solar|Wind|Thermal)\s+(Ongoing|Completed)$", re.I)
    cap_re = re.compile(r"^([\d.]+)\s*MW$", re.I)

    for i, line in enumerate(lines):
        state = state_re.match(line)
        if not state or i == 0:
            continue
        name = lines[i - 1]
        if name in seen or name.lower() in {"generation projects", "project explorer"}:
            continue
        block = lines[i + 1 : i + 18]
        capacity = None
        district = None
        milestone = None
        milestone_date = None

        for j, value in enumerate(block):
            cap = cap_re.match(value)
            if cap:
                capacity = float(cap.group(1))
                for candidate in block[j + 1 : j + 5]:
                    if (
                        candidate
                        and "assy constituency" not in candidate.lower()
                        and "capacity" not in candidate.lower()
                        and not cap_re.match(candidate)
                    ):
                        district = candidate
                        break
                break

        for j, value in enumerate(block):
            low = value.lower()
            if low.startswith("planned commissioning") or low.startswith("commissioned on"):
                milestone = "planned_commissioning" if low.startswith("planned") else "commissioned_on"
                suffix = value.split(" ", 2)
                if len(suffix) >= 3 and any(ch.isdigit() for ch in suffix[-1]):
                    milestone_date = suffix[-1]
                elif j + 1 < len(block):
                    milestone_date = block[j + 1]
                break

        projects.append(
            {
                "name": name,
                "technology": state.group(1).title(),
                "status": state.group(2).title(),
                "capacity_mw": capacity,
                "district": district,
                "milestone": milestone,
                "milestone_date_label": milestone_date,
            }
        )
        seen.add(name)
    return projects


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/processed/kseb_pms_projects.json"))
    args = parser.parse_args()

    tracker_html = _get(TRACKER)
    explorer_html = _get(EXPLORER)
    payload = {
        "retrieved_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "classification": "official_project_portal_record",
        "tracker_url": TRACKER,
        "explorer_url": EXPLORER,
        "tracker": parse_tracker(tracker_html),
        "projects": parse_projects(explorer_html),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"tracker": payload["tracker"], "projects_parsed": len(payload["projects"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
