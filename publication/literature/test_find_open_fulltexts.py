"""Offline unit tests: discovery statuses, DOI handling, and PDF verification.

Run: python -m unittest discover -s publication/literature -p 'test_find_open_fulltexts.py'
No public network or API key required.
"""
import hashlib
import importlib.util
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE = Path(__file__).with_name("find_open_fulltexts.py")
spec = importlib.util.spec_from_file_location("find_open_fulltexts", MODULE)
oa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oa)


class FakeResponse:
    def __init__(self, payload, url="https://university.example.org/file.pdf"):
        self.source = BytesIO(payload)
        self.url = url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.source.close()

    def read(self, size=-1):
        return self.source.read(size)

    def geturl(self):
        return self.url


class FullTextDiscoveryTests(unittest.TestCase):
    def test_matrix_has_unique_doi_ids(self):
        records = oa.read_matrix(MODULE.with_name("EVIDENCE_MATRIX.csv"))
        self.assertGreaterEqual(len(records), 30)
        self.assertEqual(len(set(x["doi"].lower() for x in records)), len(records))
        self.assertEqual(len(set(x["id"] for x in records)), len(records))

    def test_require_https_and_reject_embedded_credentials(self):
        self.assertTrue(oa.is_https_url("https://university.example.org/public.pdf"))
        self.assertFalse(oa.is_https_url("http://university.example.org/public.pdf"))
        self.assertFalse(oa.is_https_url("https://user:pass@university.example.org/public.pdf"))
        self.assertFalse(oa.is_https_url("file:///etc/passwd"))
        self.assertFalse(oa.is_https_url("javascript:evil()"))

    def test_openalex_oa_pdf_candidate_and_publisher_landing(self):
        fake = {
            "open_access": {"is_oa": True, "oa_status": "green"},
            "best_oa_location": {"pdf_url": "https://repo.example.org/full.pdf",
                                 "landing_page_url": "https://repo.example.org/article",
                                 "source": {"type": "repository"}},
        }
        with patch.object(oa, "request_json", return_value=fake) as req:
            data = oa.openalex_lookup("10.1111/ecog.02881", "")
            self.assertEqual(data["oa_status"], "green")
            self.assertEqual(data["source_host_type"], "repository")
            self.assertEqual(data["candidate_pdf_url"], "https://repo.example.org/full.pdf")
            self.assertIn("api.openalex.org/works/", req.call_args.args[0])

    def test_openalex_no_oa_does_not_claim_pdf(self):
        fake = {
            "open_access": {"is_oa": False, "oa_status": "closed"},
            "best_oa_location": {"pdf_url": "https://publisher.example.org/full.pdf",
                                 "landing_page_url": "https://publisher.example.org/article"}
        }
        with patch.object(oa, "request_json", return_value=fake):
            data = oa.openalex_lookup("10.1038/example", "")
            self.assertEqual(data["candidate_pdf_url"], "")

    def test_unpaywall_email_required(self):
        with self.assertRaises(ValueError):
            oa.unpaywall_lookup("10.1111/ecog.02881", "")

    def test_openalex_falls_back_to_unpaywall_with_no_pdf(self):
        with patch.object(oa, "openalex_lookup", return_value={
            "provider": "openalex", "is_oa": "true",
            "oa_status": "bronze", "candidate_pdf_url": "",
            "landing_page_url": "https://publisher.example.org"
        }), patch.object(oa, "unpaywall_lookup", return_value={
            "provider": "unpaywall", "is_oa": "true",
            "oa_status": "green", "candidate_pdf_url": "https://archive.example.org/a.pdf"
        }):
            data = oa.resolve("10.1111/ecog.02881", "both", "", "scientist@example.org")
        self.assertEqual(data["query_status"], "oa_pdf_candidate")
        self.assertEqual(data["provider"], "unpaywall")

    def test_download_verifies_signature_hash(self):
        payload = b"%PDF-1.7\nhello research\n%%EOF"
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "paper.pdf"
            with patch.object(oa, "urlopen", return_value=FakeResponse(payload)):
                status, sha, count, error = oa.save_pdf(
                    "https://university.example.org/full.pdf", target, 2048)
            self.assertEqual(status, "saved_pdf_signature_verified")
            self.assertEqual(sha, hashlib.sha256(payload).hexdigest())
            self.assertEqual(count, len(payload))
            self.assertEqual(target.read_bytes(), payload)
            self.assertFalse(error)

    def test_download_rejects_html_login_page(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "paper.pdf"
            with patch.object(oa, "urlopen", return_value=FakeResponse(b"<html>Login</html>")):
                status, *_ = oa.save_pdf(
                    "https://university.example.org/possibly.pdf", target, 2048)
            self.assertEqual(status, "download_failed")
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
