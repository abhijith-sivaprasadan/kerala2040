from kerala2040.reconciliation import build_energy_reconciliation


def test_reconciliation_keeps_boundaries_explicit():
    observed = {
        "period": "FY2024-25",
        "sources": {},
        "electricity": {
            "annual_sales_within_state_and_open_access_mu": 90.0,
            "gross_import_per_annum_mu": 70.0,
            "export_per_annum_mu": 5.0,
            "td_loss_pct": 10.0,
            "energy_sources_2024_25_mu": {
                "total_energy_input_state_consumption": 100.0,
                "gross_generation_ksebl": 25.0,
                "total_power_purchase": 75.0,
                "auxiliary_consumption": 1.0,
                "exports_sales_swap_return_open_access": 5.0,
            },
        },
        "cea_actual_2024_25": {
            "electrical_energy_requirement_mu": 98.0,
            "source": "CEA",
        },
    }
    baseline = {
        "consumption_twh": 0.08,
        "internal_generation_twh": 0.02,
        "net_import_twh": 0.06,
        "coverage_fraction": 0.8,
        "missing_days_count": 2,
    }
    result = build_energy_reconciliation(observed, baseline)
    rows = {row["metric"]: row for row in result["rows"]}

    assert rows["implied_energy_input_minus_sales"]["value_mu"] == 10.0
    assert result["checks"]["implied_energy_input_minus_sales_pct"] == 10.0
    assert rows["gross_import_minus_exports_arithmetic"]["classification"] == (
        "derived_from_measured"
    )
    assert "Not treated as canonical net imports" in (
        rows["gross_import_minus_exports_arithmetic"]["note"]
    )
