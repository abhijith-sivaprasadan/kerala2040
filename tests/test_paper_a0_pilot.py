"""Unit and source-file regression tests for A0's preliminary accounting pilot.

These confirm processed CSV arithmetic and conservative validation logic.
They do NOT authenticate third-party source HTML or source-report definitions.
"""
import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_paper_a0_pilot.py"
SPEC = importlib.util.spec_from_file_location("run_paper_a0_pilot", SCRIPT)
assert SPEC and SPEC.loader
a0 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(a0)


class A0PilotRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = a0.read_rows(a0.INPUT)

    def test_full_source_day_count_and_observed_sums(self):
        out = a0.audit_daily(self.rows)
        self.assertEqual(out["calendar_rows"], 365)
        self.assertEqual(out["observed_days"], 354)
        self.assertEqual(out["missing_report_days"], 11)
        self.assertEqual(out["observed_day_totals_mu"]["consumption_mu"],
                         "30666.2569")
        self.assertEqual(out["observed_day_totals_mu"]["net_import_mu"],
                         "22635.0183")
        self.assertEqual(out["observed_day_totals_mu"]["internal_generation_mu"],
                         "8031.2393")
        self.assertEqual(out["observed_day_totals_mu"]["hydro_mu"],
                         "7214.4710")

    def test_calendar_and_missing_days_are_explicit(self):
        result = a0.audit_daily(self.rows)
        self.assertEqual(len(result["missing_dates"]), 11)
        self.assertEqual(result["missing_dates"][0], "2024-08-12")
        self.assertIn("2025-03-17", result["missing_dates"])
        months = {r["month"]: r for r in result["monthly"]}
        self.assertEqual(months["2025-03"]["missing_report_days"], 3)
        self.assertEqual(months["2024-07"]["missing_report_days"], 0)
        self.assertEqual(months["2024-04"]["observed_report_days"], 30)
        self.assertEqual(months["2024-04"]["observed_day_consumption_sum_mu"],
                         "3191.0264")

    def test_original_source_hash_is_not_claimed_verified(self):
        # Digest is for a *processed input CSV* only.
        out = a0.run(output_dir=ROOT / "studies" / "paper-a-2027"
                     / "a0-pilot" / "reproduced")
        self.assertFalse(out["original_html_bytes_reverified_by_this_script"])
        self.assertFalse(
            out["original_economic_review_pdf_reinspected_by_this_script"]
        )
        self.assertEqual(len(out["processed_daily_csv_sha256"]), 64)

    def test_missing_day_cannot_have_fabricated_zero(self):
        rows = copy.deepcopy(self.rows)
        missing = next(x for x in rows if x["status"] == "missing")
        missing["consumption_mu"] = "0"
        with self.assertRaisesRegex(ValueError, "missing-date"):
            a0.audit_daily(rows)

    def test_duplicate_date_fails(self):
        rows = copy.deepcopy(self.rows)
        rows[1]["date"] = rows[0]["date"]
        with self.assertRaisesRegex(ValueError, "Duplicate date"):
            a0.audit_daily(rows)

    def test_absent_calendar_row_fails(self):
        rows = copy.deepcopy(self.rows[:-1])
        with self.assertRaisesRegex(ValueError, "Missing calendar rows"):
            a0.audit_daily(rows)

    def test_tampered_daily_accounting_fails(self):
        rows = copy.deepcopy(self.rows)
        observed = next(x for x in rows if x["status"] == "observed")
        observed["consumption_mu"] = "1.0000"
        with self.assertRaisesRegex(ValueError, "daily|residual"):
            a0.audit_daily(rows)

    def test_non_numeric_values_fail(self):
        rows = copy.deepcopy(self.rows)
        observed = next(x for x in rows if x["status"] == "observed")
        observed["net_import_mu"] = "nan"
        with self.assertRaisesRegex(ValueError, "non-finite"):
            a0.audit_daily(rows)

    def test_source_ontology_forbids_direct_differences(self):
        ledger = a0.validate_ledger(a0.read_rows(a0.LEDGER))
        matches = a0.crosswalk(ledger)
        self.assertEqual(len(matches), 4)
        self.assertTrue(all(
            r["admissibility"] == "BLOCKED_AS_DIRECT_SUBTRACTION" for r in matches
        ))
        self.assertTrue(all(r["difference_mu"] == "" for r in matches))


if __name__ == "__main__":
    unittest.main()
