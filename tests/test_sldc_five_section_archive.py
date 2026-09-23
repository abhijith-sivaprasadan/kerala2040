"""Offline regression for hash-pinned SLDC source-date and balance handling."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'process_sldc_five_section_archive.py'
spec = importlib.util.spec_from_file_location('sldc_archive_offline', SCRIPT)
assert spec is not None and spec.loader is not None
sldc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sldc)


def test_numbers_and_financial_year():
    assert sldc.dec('') is None
    assert sldc.dec('1,234.500') == 1234.5
    assert sldc.dec('NaN') is None
    assert sldc.fy('2019-08-06') == '2019-20'
    assert sldc.fy('2024-03-31') == '2023-24'
    assert sldc.fy('2024-04-01') == '2024-25'
    assert sldc.status_json({'accepted': True, 'requested_date': '2024-04-01',
                             'section': 'statistics', 'source_report_dates': ['2024-04-01']},
                            '2024-04-01', 'statistics')
    assert not sldc.status_json({'accepted': True, 'requested_date': '2024-04-01',
                                 'section': 'statistics', 'source_report_dates': ['2024-04-02']},
                                '2024-04-01', 'statistics')


def _mini_zip(path: Path, corrupt: bool = False):
    root = 'MiniSLDC/'
    day = '2024-04-01'
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr(root + 'archive_qa.json', json.dumps({'requested_start': day,
                                                        'requested_end': day}))
        for sec in sldc.SECTIONS:
            rows = [['Day'], ['Header'], ['Generation', '10'], ['Net Import', '25'],
                    ['Consumption', '35']] if sec == 'statistics' else [
                        ['Day'], ['Header'], ['Other'], ['Third'], ['Fourth']]
            if sec == 'imports':
                rows = [['Day'], ['Header'], ['Net Import', '25'], ['Other'], ['Fourth']]
            if sec == 'other_extrema':
                rows = [['Day'], ['Maximum Demand - 01.04.2024'], ['Morning Peak'],
                        ['MW', '3000'], ['Time', '06:10'], ['Evening Peak'],
                        ['MW', '4000'], ['Time', '19:15']]
            html = f'{day}:{sec}'.encode()
            sha = hashlib.sha256(html).hexdigest()
            if corrupt and sec == 'imports':
                sha = '0' * 64
            rec = {'accepted': True, 'requested_date': day, 'section': sec,
                   'source_report_dates': [day], 'rows': rows, 'response_sha256': sha}
            z.writestr(f'{root}accepted/{sec}/{day}.html', html)
            z.writestr(f'{root}accepted/{sec}/{day}.json', json.dumps(rec))


def test_offline_archive_source_hash_and_balance(tmp_path: Path, monkeypatch):
    inp = tmp_path / 'mini.zip'
    dest = tmp_path / 'normalised'
    _mini_zip(inp)
    monkeypatch.setattr(sys, 'argv', ['offline', str(inp), '--out', str(dest)])
    assert sldc.main() == 0
    qa = json.loads((dest / 'qa_manifest.json').read_text())
    assert len(qa['invalid_accepted_metadata_or_raw_html_sha256']) == 0
    assert all(v['accepted'] == 1 for v in qa['section_status_counts'].values())
    with (dest / 'daily_system.csv').open() as file:
        day = next(csv.DictReader(file))
    assert day['balance_error_mu'] == '0.0'
    assert day['energy_balance_qualified'] == 'True'
    assert day['consumption_qualified_mu'] == '35.0'
    _mini_zip(inp, corrupt=True)
    monkeypatch.setattr(sys, 'argv', ['offline', str(inp), '--out', str(dest)])
    assert sldc.main() == 2
    qa = json.loads((dest / 'qa_manifest.json').read_text())
    assert len(qa['invalid_accepted_metadata_or_raw_html_sha256']) == 1
    assert qa['invalid_accepted_metadata_or_raw_html_sha256'][0]['section'] == 'imports'
