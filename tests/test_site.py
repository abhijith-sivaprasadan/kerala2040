import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_site", ROOT / "scripts/build_site.py")
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


def test_published_bundle_is_consistent():
    site.validate_bundle(ROOT / "public")


def test_scope_is_statewide_and_primary_case_is_kmml():
    data = site.validate_bundle(ROOT / "public")
    assert data["scope"]["scope"] == "statewide"
    assert len(set(data["scope"]["districts"])) == 14
    assert data["circular_industry"]["primary_case"] == "kmml"
    assert all(node["kind"] != "grid" for node in data["screening_nodes"])


def test_rejects_mixed_snapshots(tmp_path):
    shutil.copytree(ROOT / "public", tmp_path / "public")
    manifest = tmp_path / "public/site-data.json"
    data = json.loads(manifest.read_text())
    data["baseline"]["rows"] += 1
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="different snapshots"):
        site.validate_bundle(tmp_path / "public")


def test_packaged_site_has_every_advertised_download(tmp_path):
    site.build_site(ROOT, tmp_path)
    data = site.validate_bundle(tmp_path / "data")
    assert (tmp_path / "assets/app.js").exists()
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert 'src="assets/app.js"' not in html
    assert any(p.name in html for p in (tmp_path / "assets").glob("app.*.js"))
    assert all((tmp_path / "data" / name).exists() for name in data["metadata"]["files"].values())


def test_live_website_includes_source_checked_audit_without_promoting_2040(tmp_path):
    site.build_site(ROOT, tmp_path)
    data = site.validate_bundle(tmp_path / "data")
    name = data["metadata"]["files"]["audit_readiness"]
    audit = json.loads((tmp_path / "data" / name).read_text(encoding="utf-8"))
    assert audit["classification"] == (
        "repository_evidence_audit_not_external_source_validation"
    )
    assert audit["finding_count"] == 17 and audit["open_findings"] == 17
    assert audit["checks"]["sldc_accounting_integrity"]["status"] == (
        "verified_in_committed_evidence"
    )
    assert audit["checks"]["sldc_daily_coverage"]["status"] == "partial_or_provisional"
    assert not audit["release_gates"]["techno_economic_2040"]["passed"]
    assert not audit["release_gates"]["observed_full_year"]["passed"]
    station = json.loads((tmp_path / "data/sldc-station-evidence.json").read_text())
    assert audit["source_qa_sha256"] == station["source_archive_sha256"]
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert 'data-view="audit"' in html and 'data-route="audit"' in html
    assert not list((tmp_path / "data").glob("*proxy*"))


def test_packaged_audit_rejects_tampered_finding_totals(tmp_path):
    site.build_site(ROOT, tmp_path)
    path = tmp_path / "data/audit-readiness.json"
    audit = json.loads(path.read_text())
    audit["closed_findings"] = 17
    path.write_text(json.dumps(audit))
    with pytest.raises(ValueError, match="totals disagree"):
        site.validate_bundle(tmp_path / "data")


def test_config_only_rebuild_preserves_acquired_evidence(tmp_path):
    shutil.copytree(ROOT / "public", tmp_path / "public")
    shutil.copytree(ROOT / "configs", tmp_path / "configs")
    before = site.validate_bundle(tmp_path / "public")
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    subprocess.run([sys.executable, str(ROOT / "scripts/build_web_bundle.py"),
                    "--root", str(tmp_path)], check=True, capture_output=True, env=env)
    after = site.validate_bundle(tmp_path / "public")
    assert after["baseline"]["rows"] == before["baseline"]["rows"]
    assert after["research_results"] == before["research_results"]
    assert after["metadata"]["layer_provenance"]["sldc_daily"]["preserved"]
    assert after["metadata"]["status"]["sldc_daily"]["available"]
    for layer, field in (("kseb_historical_export", "kseb_history"),
                         ("energyproject_context", "energyproject_context")):
        assert after[field] == before[field]
        assert after["metadata"]["status"][layer] == before["metadata"]["status"][layer]


@pytest.mark.parametrize("corruption", ["timestamp", "load_mw"])
def test_rejects_corrupt_hourly_chronology(tmp_path, corruption):
    shutil.copytree(ROOT / "public", tmp_path / "public")
    path = tmp_path / "public/hourly-load-proxy.json"
    data = json.loads(path.read_text())
    if corruption == "timestamp":
        data["records"][1]["timestamp"] = data["records"][0]["timestamp"]
    else:
        data["records"][1]["load_mw"] += 100
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="timestamps|energy"):
        site.validate_bundle(tmp_path / "public")


def test_live_site_excludes_synthetic_downloads_even_after_rebuild(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "hourly-load-proxy.json").write_text("{}")
    site.build_site(ROOT, tmp_path)
    live = site.validate_bundle(data)
    assert "hourly_load_proxy" not in live
    assert live["screening_nodes"] == []
    assert not list(data.glob("*proxy*"))
    assert "hourly_load_proxy" not in live["metadata"]["files"]
    products = live["research_results"]["products"]
    assert not {"renewables", "replay", "scenario_dimensions", "techno_economics"} & products.keys()
    assert products["cstep"]["classification"] == "published_external_scenario"
    assert (ROOT / "public/hourly-load-proxy.json").exists()


def test_expanded_sldc_archive_is_published_without_synthetic_hourly_telemetry(tmp_path):
    full = ROOT / "public/sldc-station-evidence.json"
    if not full.exists():
        pytest.skip("Optional local archive not staged")
    layer = json.loads(full.read_text(encoding="utf-8"))
    assert layer["classification"] == "derived_from_measured"
    assert layer["observed_days"] == 354
    assert len(layer["missing_dates"]) == 11
    assert layer["reported_row_counts"]["hydro_station"] == 5779
    assert layer["reported_row_counts"]["reservoir"] == 5664
    assert layer["observed_totals_mu"]["consumption_mu"] == 30666.2569
    site.build_site(ROOT, tmp_path)
    published = json.loads((tmp_path / "data/site-data.json").read_text(encoding="utf-8"))
    assert published["metadata"]["files"]["sldc_station_evidence"] == "sldc-station-evidence.json"
    assert (tmp_path / "data/sldc-processed-evidence.zip").exists()
    assert not list((tmp_path / "data").glob("*proxy*"))

def test_packaged_research_workbench_uses_same_audited_snapshot(tmp_path):
    site.build_site(ROOT, tmp_path)
    payload = site.validate_bundle(tmp_path / "data")
    ledger_name = payload["metadata"]["files"]["research_ledger"]
    assert ledger_name == "research-ledger.json"
    ledger = json.loads((tmp_path / "data" / ledger_name).read_text())
    audit = json.loads((tmp_path / "data/audit-readiness.json").read_text())
    assert payload["research_ledger"] == ledger
    assert ledger["audit_open_findings"] == audit["open_findings"]
    assert len(ledger["workstreams"]) == 11
    assert ledger["eligible_area_sq_km"] is None
    assert ledger["potential_mw"] is None
    assert ledger["release_gates"]["techno_economic_2040"]["passed"] is False
    html = (tmp_path / "index.html").read_text()
    assert 'data-view="workbench"' in html
    assert 'data-route="workbench"' in html
    assert 'href="data/research-ledger.json"' in html
    assert 'href="assets/kerala.css"' not in html
    assert any(x.name in html for x in (tmp_path / "assets").glob("kerala.*.css"))


def test_packaged_workbench_rejects_forged_gis_admission(tmp_path):
    site.build_site(ROOT, tmp_path)
    path = tmp_path / "data/research-ledger.json"
    ledger = json.loads(path.read_text())
    ledger["potential_mw"] = 999
    path.write_text(json.dumps(ledger))
    with pytest.raises(ValueError, match="ledger and site manifest disagree"):
        site.validate_bundle(tmp_path / "data")


def test_packaged_workbench_rejects_cross_snapshot_findings(tmp_path):
    site.build_site(ROOT, tmp_path)
    path = tmp_path / "data/research-ledger.json"
    ledger = json.loads(path.read_text())
    ledger["audit_open_findings"] = 0
    manifest = tmp_path / "data/site-data.json"
    payload = json.loads(manifest.read_text())
    payload["research_ledger"] = ledger
    path.write_text(json.dumps(ledger))
    manifest.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="audited finding counts disagree"):
        site.validate_bundle(tmp_path / "data")


def test_kerala_coded_site_packages_fresh_app_and_distinct_audit_clocks(tmp_path):
    site.build_site(ROOT, tmp_path)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert 'lang="ml"' in html and "കേരളത്തിന്റെ ഊർജഭാവി" in html
    assert 'id="homeTitle"' in html and "A stronger" in html
    assert 'id="spatialPipeline"' in html
    assert 'id="headlineMetrics"' in html
    assert 'data-view="workbench"' in html
    assert 'data-view="audit"' in html
    assert 'data-view="pathways"' in html
    assert 'href="assets/kerala.css"' not in html
    assert 'src="assets/app.js"' not in html
    assert any(x.name in html for x in (tmp_path / "assets").glob("kerala.*.css"))
    assert not any(x.name in html for x in (tmp_path / "assets").glob("experience.*.css"))
    payload = site.validate_bundle(tmp_path / "data")
    assert payload["research_ledger"]["eligible_area_sq_km"] is None
    assert payload["research_ledger"]["potential_mw"] is None
    assert payload["metadata"]["research_source_commit"] == site.source_revision(ROOT)
    assert payload["metadata"]["generated_at_utc"] == json.loads(
        (ROOT / "public/metadata.json").read_text(encoding="utf-8")
    )["generated_at_utc"]
    assert payload["research_ledger"]["reviewed_date"] != payload["metadata"][
        "generated_at_utc"
    ][:10]


def test_source_revision_refuses_unrelated_parent_git_checkout(tmp_path):
    assert site.source_revision(tmp_path) is None
