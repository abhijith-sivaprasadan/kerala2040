"""Static evidence-ledger unit tests; no network or nonstandard dependencies."""
import csv
import tempfile
import unittest
from pathlib import Path

import validate


class LiteratureLedgerTest(unittest.TestCase):
    def test_current_curated_matrix_and_source_links(self):
        result = validate.validate()
        self.assertGreaterEqual(result["curated_entries"], 40)
        self.assertGreaterEqual(result["peer_reviewed_type_entries"], 30)
        self.assertEqual(result["curated_entries"], len(
            {row["id"] for row in self.read_rows()}
        ))

    @staticmethod
    def read_rows():
        with validate.CSV_PATH.open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def test_duplicate_reference_id_rejected(self):
        rows = self.read_rows()
        rows[1]["id"] = rows[0]["id"]
        self.assert_invalid(rows, "duplicate identifier")

    def test_missing_scholarly_doi_rejected(self):
        rows = self.read_rows()
        target = next(row for row in rows if row["source_type"].startswith("peer_reviewed"))
        target["doi"] = ""
        self.assert_invalid(rows, "missing DOI")

    def test_invalid_doi_rejected(self):
        rows = self.read_rows()
        target = next(row for row in rows if row["doi"])
        target["doi"] = "not-a-valid-doi"
        self.assert_invalid(rows, "malformed DOI")

    def assert_invalid(self, rows, message):
        with tempfile.TemporaryDirectory() as temporary:
            p = Path(temporary) / "matrix.csv"
            with p.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=validate.REQUIRED)
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, message):
                validate.validate(path=p)


if __name__ == "__main__":
    unittest.main()
