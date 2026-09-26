# Idukki v1.5 — official KSEB Dam Safety extractor boundary

v1.5 changes the source strategy.

The project will no longer treat the third-party KSEB historical mirror as a
general numerical input. It remains useful for locating dates and preserving
scrape history, but a date is admitted into the physical reservoir evidence
layer only after it is extracted from an **official KSEB Dam Safety page** with
the table interpreted from its headers and units.

## Why this change was necessary

The mirror historically used fixed column positions. KSEB's daily reservoir
table has changed over time. Several retained 2024 mirror rows contain values
that are visibly impossible for the stored field:

- 2024-06-02: `inflow = "2313.56ft"`
- 2024-10-15: `inflow = "44.85%"`
- 2024-11-25: `inflow = "55.87%"`

Those are schema/column-shift artefacts, not hydrological observations.

The mirror is therefore **secondary evidence only** unless a specific date is
cross-checked against the official page.

## Header-driven parser

`src/kerala2040/kseb_dam_safety_official_v1_5.py` identifies fields by:

1. header meaning;
2. the unit stated in the header;
3. the target dam name;
4. row-level consistency checks.

It never assumes that column 11 or column 13 has a fixed meaning.

If a historical layout exposes both `Inflow (MCM)` and
`Average Inflow (Cumecs)`, both are preserved separately. No conversion is
performed merely to make schemas look uniform.

A percentage or feet value under an inflow header causes a hard failure.

## Idukki level-unit exception

The generic KSEB header currently labels water level in metres, while the
Idukki row itself identifies MWL/FRL in feet. When the Idukki MWL source cell
contains `ft`, the parser records the dynamic Idukki water level using a
row-level feet override and keeps that override in the provenance record.

## Direct official validation

The following official pages are used as the first live validation set:

- 17 March 2025 — https://dams.kseb.in/?p=5176
- 18 March 2025 — https://dams.kseb.in/?p=5178
- 19 March 2025 — https://dams.kseb.in/?p=5180

For Idukki they expose live storage in MCM plus inflow, powerhouse discharge,
spillway release and total outflow in cumecs.

Using the report-date flow as the preceding 24-hour average is only a
diagnostic convention. Under that convention, the storage-balance residuals
for 18 and 19 March are about -0.245 and -0.243 MCM respectively. The residual
is not assigned to evaporation, diversion, rounding or any other physical term
without documentation from KSEB.

## Relationship to v1.4

Nothing here weakens the strict v1.4 SLDC gate.

The SHA-verified SLDC evidence remains:

- 325/364 directly reported daily inflows;
- 29 additional uniquely source-derived cumulative-accounting values;
- 354/364 direct + source-derived coverage.

v1.5 is a separate attempt to build a stronger reservoir-operations source from
official KSEB pages. Once the historical official pages are collected and
schema-audited, the next decision is whether KSEB's own storage/inflow/release
series can replace the reconstructed v1.3 water term for a physical sensitivity.

## Run

For known official pages:

```bash
python scripts/extract_kseb_idukki_official_v1_5.py \
  --url 'https://dams.kseb.in/?p=5176' \
  --url 'https://dams.kseb.in/?p=5178' \
  --url 'https://dams.kseb.in/?p=5180' \
  --out-json results/hydro/kseb_idukki_official_v1_5.json \
  --out-csv results/hydro/kseb_idukki_official_v1_5.csv
```

The CLI can also discover dated links from an archive/index page, but it does
not invent URLs for dates that are not exposed by the source.
