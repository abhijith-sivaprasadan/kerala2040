"""Explicit reconciliation of Kerala electricity accounting boundaries."""

from __future__ import annotations

from typing import Any


def build_energy_reconciliation(
    observed: dict[str, Any],
    baseline_summary: dict[str, Any],
    *,
    proxy_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return sourced and derived metrics without silently equating accounting scopes."""
    electricity = observed["electricity"]
    sources = observed.get("sources", {})
    rows: list[dict[str, Any]] = []

    def add(
        metric: str,
        value_mu: float,
        classification: str,
        boundary: str,
        source: str,
        comparable_group: str | None = None,
        note: str | None = None,
    ) -> None:
        rows.append(
            {
                "metric": metric,
                "value_mu": float(value_mu),
                "classification": classification,
                "boundary": boundary,
                "source": source,
                "comparable_group": comparable_group,
                "note": note,
            }
        )

    add(
        "sldc_consumption_observed_days",
        baseline_summary["consumption_twh"] * 1000.0,
        "derived_from_measured_daily",
        "SLDC system consumption; observed archive days only",
        "Kerala SLDC",
        "daily_system_balance",
    )
    add(
        "sldc_internal_generation_observed_days",
        baseline_summary["internal_generation_twh"] * 1000.0,
        "derived_from_measured_daily",
        "SLDC internal generation; observed archive days only",
        "Kerala SLDC",
        "daily_system_balance",
    )
    add(
        "sldc_net_import_observed_days",
        baseline_summary["net_import_twh"] * 1000.0,
        "derived_from_measured_daily",
        "SLDC net interface import; observed archive days only",
        "Kerala SLDC",
        "daily_system_balance",
    )

    cea = observed.get("cea_actual_2024_25")
    if cea:
        add(
            "cea_electrical_energy_requirement",
            cea["electrical_energy_requirement_mu"],
            "official_observed_reference",
            "CEA resource-adequacy electrical energy requirement",
            cea["source"],
            "annual_requirement",
        )

    add(
        "ksebl_sales_with_open_access",
        electricity["annual_sales_within_state_and_open_access_mu"],
        "official_observed_reference",
        "Annual sales within state including open access",
        "Kerala Economic Review 2025 / KSEBL",
        "retail_sales",
    )
    add(
        "economic_review_gross_import",
        electricity["gross_import_per_annum_mu"],
        "official_observed_reference",
        "Gross import per annum as reported",
        "Kerala Economic Review 2025 / KSEBL",
        "external_energy",
    )
    add(
        "economic_review_export",
        electricity["export_per_annum_mu"],
        "official_observed_reference",
        "Export per annum as reported",
        "Kerala Economic Review 2025 / KSEBL",
        "external_energy",
    )

    energy = electricity["energy_sources_2024_25_mu"]
    add(
        "economic_review_total_energy_input_state_consumption",
        energy["total_energy_input_state_consumption"],
        "official_observed_reference",
        "Total energy input for state consumption",
        "Kerala Economic Review 2025 / KSEBL",
        "state_energy_input",
    )
    add(
        "economic_review_gross_generation_ksebl",
        energy["gross_generation_ksebl"],
        "official_observed_reference",
        "KSEBL gross generation",
        "Kerala Economic Review 2025 / KSEBL",
        "generation",
    )
    add(
        "economic_review_total_power_purchase",
        energy["total_power_purchase"],
        "official_observed_reference",
        "Total power purchase under Economic Review accounting",
        "Kerala Economic Review 2025 / KSEBL",
        "power_purchase",
    )
    add(
        "economic_review_auxiliary_consumption",
        energy["auxiliary_consumption"],
        "official_observed_reference",
        "Auxiliary consumption",
        "Kerala Economic Review 2025 / KSEBL",
        "auxiliary",
    )
    add(
        "economic_review_exports_sales_swap_return_open_access",
        energy["exports_sales_swap_return_open_access"],
        "official_observed_reference",
        "Exports/sales/swap return/open access as reported",
        "Kerala Economic Review 2025 / KSEBL",
        "external_energy",
    )

    energy_input = float(energy["total_energy_input_state_consumption"])
    sales = float(electricity["annual_sales_within_state_and_open_access_mu"])
    implied_loss_mu = energy_input - sales
    implied_loss_pct = 100.0 * implied_loss_mu / energy_input
    add(
        "implied_energy_input_minus_sales",
        implied_loss_mu,
        "derived_accounting_check",
        "Total energy input minus annual sales/open access",
        "Derived from Kerala Economic Review 2025 values",
        "loss_reconciliation",
        "Arithmetic check; not a separately reported energy-flow component.",
    )

    gross_minus_exports = (
        float(electricity["gross_import_per_annum_mu"])
        - float(electricity["export_per_annum_mu"])
    )
    add(
        "gross_import_minus_exports_arithmetic",
        gross_minus_exports,
        "derived_noncanonical_cross_check",
        "Gross import minus reported exports",
        "Derived from Kerala Economic Review 2025 values",
        "external_energy",
        "Not treated as canonical net imports because the source accounting scopes can differ.",
    )

    if proxy_summary is not None:
        add(
            "hourly_proxy_annual_energy",
            proxy_summary["annual_energy_mu"],
            "proxy_reconstruction",
            "354 measured daily totals plus explicitly interpolated missing days",
            "Kerala 2040 proxy reconstruction",
            "annual_requirement",
            "Not measured hourly telemetry and excluded from observed-only calibration.",
        )

    return {
        "classification": "derived",
        "source_type": "accounting_reconciliation",
        "source": "Kerala SLDC + Kerala State Planning Board/KSEBL Economic Review 2025 + CEA Resource Adequacy Plan",
        "period": observed.get("period", "FY2024-25"),
        "rows": rows,
        "checks": {
            "reported_td_loss_pct": float(electricity["td_loss_pct"]),
            "implied_energy_input_minus_sales_pct": implied_loss_pct,
            "difference_percentage_points": implied_loss_pct
            - float(electricity["td_loss_pct"]),
            "baseline_coverage_fraction": float(baseline_summary["coverage_fraction"]),
            "baseline_missing_days": int(baseline_summary["missing_days_count"]),
        },
        "source_registry": sources,
        "rules": [
            "Do not equate annual sales, electrical energy requirement, and system consumption.",
            "Do not use gross imports minus exports as canonical net imports without scope validation.",
            "Observed-day SLDC sums remain partial-year observations when archive dates are missing.",
            "Proxy/interpolated quantities remain separately classified and are never promoted to observed.",
        ],
    }
