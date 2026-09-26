from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/discover_kseb_monthly_wpdm_v1_5.py"
SPEC = spec_from_file_location("discover_kseb_monthly_wpdm_v1_5", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot import {SCRIPT}")
M = module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def inventory():
    return {
        "months": [
            {
                "month": f"2024-{month:02d}",
                "title": f"Water Level main reservoirs Month {month}",
            }
            for month in range(1, 13)
        ]
    }


def html_for(kind="href"):
    blocks = []
    for month in range(1, 13):
        title = f"Water Level main reservoirs Month {month}"
        if kind == "href":
            control = f'<a href="/?wpdmdl={1000+month}">Download</a>'
        elif kind == "data":
            control = f'<button data-package-id="{1000+month}">Download</button>'
        else:
            control = f'[wpdm_package id="{1000+month}"]'
        blocks.append(f'<section><h3>{title}</h3>{control}</section>')
    return "<html><body>" + "".join(blocks) + "</body></html>"


@pytest.mark.parametrize("kind", ["href", "data", "shortcode"])
def test_all_12_unique_bindings(kind):
    result = M.discover_bindings(
        html_for(kind),
        inventory=inventory(),
        base_url="https://dams.kseb.in/?p=329",
    )
    assert result["months_uniquely_bound"] == 12
    assert result["all_12_unique_downloads_bound"] is True
    assert len({x["selected"]["package_id"] for x in result["bindings"]}) == 12


def test_ambiguous_month_fails_closed():
    html = html_for("href").replace(
        '<a href="/?wpdmdl=1001">Download</a>',
        '<a href="/?wpdmdl=1001">Download</a>'
        '<a href="/?wpdmdl=9999">Other</a>',
    )
    result = M.discover_bindings(
        html,
        inventory=inventory(),
        base_url="https://dams.kseb.in/?p=329",
    )
    assert result["all_12_unique_downloads_bound"] is False
    assert result["bindings"][0]["status"] == "unresolved_multiple_candidates"


def test_external_download_candidate_ignored():
    html = html_for("href").replace(
        '<a href="/?wpdmdl=1001">Download</a>',
        '<a href="https://example.com/?wpdmdl=1001">Download</a>',
    )
    result = M.discover_bindings(
        html,
        inventory=inventory(),
        base_url="https://dams.kseb.in/?p=329",
    )
    assert result["bindings"][0]["status"] == "unresolved_no_exposed_candidate"


def test_bulk_download_refuses_incomplete(tmp_path: Path):
    with pytest.raises(ValueError, match="all 12"):
        M.download_bound_files(
            {"all_12_unique_downloads_bound": False},
            output_dir=tmp_path,
            timeout=1,
        )
