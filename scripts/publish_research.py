"""Publish completed research artifacts without converting assumptions to observations."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pandas as pd
import yaml


def build_research(root: Path) -> dict:
    prior = root / 'public/research-results.json'
    result = json.loads(prior.read_text(encoding='utf-8')) if prior.exists() else {
        'classification': 'mixed_evidence_see_each_product', 'products': {}
    }
    products = result['products']
    provenance = result.setdefault('artifact_provenance', {})
    receipt = root / 'results/recovered_artifacts.json'
    recovered = json.loads(receipt.read_text()) if receipt.exists() else {}
    paths = {
        'hydro': 'results/hydro/summary.json',
        'renewables': 'results/resources/renewable_availability_summary.json',
        'inventory': 'results/inventory/generator_capacity_summary.json',
        'replay': 'results/models/kerala_fy2024_25_daily_replay_summary.json',
        'reconciliation': 'results/reconciliation/energy_reconciliation.json',
        'gis': 'results/gis/gis_input_manifest.json',
    }
    for key, relative in paths.items():
        path = root / relative
        if path.exists():
            products[key] = json.loads(path.read_text(encoding='utf-8'))
            run_id = os.environ.get('GITHUB_RUN_ID') or recovered.get(key)
            provenance[key] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                               'artifact_path': relative,
                               'run_url': f'https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/{run_id}' if run_id else None}
    inventory = root / 'results/inventory/generator_capacity_database.csv'
    if inventory.exists() and 'inventory' in products:
        products['inventory']['records'] = json.loads(pd.read_csv(inventory).to_json(orient='records'))
    cstep = root / 'data/external/cstep_2024'
    if cstep.exists():
        products['cstep'] = {
            'classification': 'published_external_scenario',
            'metadata': yaml.safe_load((cstep / 'metadata.yaml').read_text(encoding='utf-8')),
            'tables': {p.stem: json.loads(pd.read_csv(p).to_json(orient='records'))
                       for p in sorted(cstep.glob('*.csv'))},
        }
    for key in ('techno_economics', 'scenario_dimensions'):
        path = root / f'configs/{key}.yaml'
        if path.exists():
            products[key] = yaml.safe_load(path.read_text(encoding='utf-8'))
    result['limitations'] = [
        'Daily replay is an accounting check, not chronological dispatch validation or 2040 optimisation.',
        'Renewable profiles cover a UTC year and require explicit alignment to IST model intervals.',
        'GIS raw-file presence is not a processed ecological exclusion map or capacity ceiling.',
        'CSTEP pathways and costs remain external benchmarks; unresolved model inputs stay null.',
    ]
    return result
