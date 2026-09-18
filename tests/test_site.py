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


def test_config_only_rebuild_preserves_acquired_evidence(tmp_path):
    shutil.copytree(ROOT / "public", tmp_path / "public")
    shutil.copytree(ROOT / "configs", tmp_path / "configs")
    before = site.validate_bundle(tmp_path / "public")
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    subprocess.run([sys.executable, str(ROOT / "scripts/build_web_bundle.py"),
                    "--root", str(tmp_path)], check=True, capture_output=True, env=env)
    after = site.validate_bundle(tmp_path / "public")
    assert after["baseline"]["rows"] == before["baseline"]["rows"]
    assert after["metadata"]["layer_provenance"]["sldc_daily"]["preserved"]
    assert after["metadata"]["status"]["sldc_daily"]["available"]
