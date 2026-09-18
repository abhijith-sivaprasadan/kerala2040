import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "kseb", Path(__file__).resolve().parents[1] / "scripts/ingest_kseb_pms.py"
)
kseb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kseb)


def test_project_spans_are_parsed_without_leaking_next_project():
    html = """<h3>First Hydro</h3><span>Hydro</span><span>Ongoing</span>
    <label>Capacity</label><span>40</span><span>MW</span><div>Idukki</div>
    <h3>Second Hydro</h3><span>Hydro</span><span>Completed</span>
    <label>Installed Capacity</label><span>6.6</span><span>MW</span><div>Kozhikode</div>
    <span>Commissioned On</span><time>31, Mar 2023</time>"""
    rows = kseb.parse_projects(html)
    assert len(rows) == 2
    assert rows[0]["capacity_mw"] == 40
    assert rows[0]["milestone"] is None
    assert rows[1]["capacity_mw"] == 6.6
    assert rows[1]["milestone_date_label"] == "31, Mar 2023"
