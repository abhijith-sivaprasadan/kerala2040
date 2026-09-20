"""No live endpoint or synthetic fixture can self-certify a legal wetland mask."""
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
m = importlib.import_module("audit_swak_wetland_sources")


def test_draft_classification_never_final():
    item = m.classify_link(
        "Gazette Notification PDF", "https://www.swak.kerala.gov.in/draft.pdf",
        "swak_draft_briefs",
    )
    assert item == "draft_or_draft_page_NOT_FINAL"
    assert m.classify_link(
        "Vembanad", "https://www.swak.kerala.gov.in/brief.pdf",
        "swak_draft_briefs",
    ) == "draft_or_draft_page_NOT_FINAL"


def test_url_constraints():
    assert m.official_url("https://wiams.kerala.gov.in/")
    assert not m.official_url("http://www.swak.kerala.gov.in/")
    assert not m.official_url("https://swak.kerala.gov.in.attacker.test/a")


def test_candidates_are_unverified_even_when_vector():
    assert m.classify_link(
        "final boundary", "https://www.swak.kerala.gov.in/layer.gpkg",
        "swak_home",
    ) == "machine_readable_candidate_UNINSPECTED"


class Response:
    status_code = 200
    url = "https://www.swak.kerala.gov.in/index.php"
    content = b'<a href="/wetland.pdf">Wetland Notification</a>'
    headers = {"content-type": "text/html"}

    def raise_for_status(self):
        pass


class Session:
    def get(self, url, timeout):
        return Response()


def test_mock_pages_cannot_become_legal_geometry(tmp_path):
    report = m.audit(tmp_path / "swak.json", Session())
    assert report["reachable_html_pages"] == len(m.PAGES)
    assert not report["notification_linked_original_vector_verified"]
    assert not report["zone_of_influence_original_vector_verified"]
    assert not report["legal_wetland_exclusion_ready"]
    assert report["eligible_area_sq_km"] is None
    assert report["capacity_ceiling_mw"] is None
    assert report["official_candidate_links_unverified"]
