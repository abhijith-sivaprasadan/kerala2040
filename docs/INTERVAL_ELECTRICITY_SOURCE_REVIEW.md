# FY2024-25 interval demand and interchange: public-source review

Reviewed 19 September 2026. This note records what the public official sources can and cannot currently support for the `measured_interval_demand_interchange` audit item. It is not a substitute for authenticated SLDC/KSEBL telemetry.

## Required dataset

The calibration target remains:

- Kerala state demand/load for 1 April 2024 to 31 March 2025 at 15-minute resolution (35,040 intervals), or hourly if the primary source only exposes hourly averages;
- actual interstate import/export or net interchange on the same clock;
- interval timestamps/block number, timezone, interval semantics, quality/revision flags and a clear system/metering boundary;
- scheduled interchange retained separately from actual interchange.

A published chart, frequency histogram, daily energy total or reconstructed load curve cannot satisfy this gate.

## Official evidence located

### Kerala SLDC

- System statistics: https://sldckerala.com/index.php?id=1
- Contacts: https://sldckerala.com/index.php?id=3

The public system-statistics interface supplies dated daily energy/accounting and selected extrema. It does not expose a continuous 8,760/35,040 state-load download through the interface used by this project.

The current official directory identifies the Chief Engineer, Transmission - System Operation, at `ceso@kseb.in`, Deputy Chief Engineer (Grid) at `dcegrid.sldc@kseb.in`, and Executive Engineer (Tech) at `eetech.sldc@kseb.in`. The request draft deliberately addresses office roles, not an individual officer.

### Central Electricity Authority resource-adequacy study

Landing page:
https://cea.nic.in/resource_adequacy_st/report-on-resource-adequacy-plan-for-kerala-up-to-2035-36/

CEA's Kerala resource-adequacy study uses/analyzes FY2024-25 hourly demand and reports hourly-frequency and seasonal/peak-pattern information. The Kerala 2040 repository preserves those published aggregates in `configs/cea_resource_adequacy_2025.yaml`.

This establishes that an official hourly chronology was available to the study authors. It does **not** provide the underlying raw hourly series as a public machine-readable download in the source material currently secured by this project. The published bins and figures must not be reverse-engineered and relabelled as measured telemetry.

### Southern Regional Power Committee DSM material

Examples:

- https://www.srpc.kar.nic.in/website/2024/commercial/dsm15-21july24.pdf
- https://www.srpc.kar.nic.in/website/2024/commercial/dsm02-08dec24.pdf
- https://www.srpc.kar.nic.in/website/2025/commercial/dsm24-30mar25.pdf

The official SRPC DSM statements include Kerala daily total schedule and actual drawal values. SRPC documentation also describes commercial output data containing day-wise, block-wise schedules/actual/deviation information for regional accounting.

This is useful as an **independent interstate-drawal/accounting source** and should be pursued as a cross-check. It does not by itself establish:

1. Kerala's total state demand/load chronology;
2. the exact correspondence between SRPC actual drawal and the Kerala SLDC aggregate `Net Import` boundary;
3. a complete FY2024-25 blockwise Kerala series in the repository;
4. whether all relevant revisions have been captured.

Do not substitute DSM daily actual drawal for state demand or for verified Kerala interface MW limits.

## Current conclusion

The public-source review improves the evidence map but does **not** close the audit finding.

- **Measured FY2024-25 state demand:** raw continuous chronology not secured.
- **Measured FY2024-25 actual interchange:** official SRPC material demonstrates an independent accounting route and daily actual-drawal values, but the complete reconciled blockwise series is not yet secured in the repository.
- **Audit status:** blocked pending authenticated interval data and reconciliation.

## Acquisition path

1. Send `docs/SLDC_DATA_REQUEST_DRAFT.md` to Kerala SLDC/KSEBL requesting the existing FY2024-25 interval export and data dictionary.
2. In parallel, acquire the SRPC FY2024-25 DSM data files/revisions and extract Kerala blockwise actual drawal/schedule where the source files expose it.
3. Preserve source URLs, published/revision dates, raw hashes and source naming.
4. Validate timezone/block conventions, missing/duplicate intervals and revision precedence.
5. Aggregate the interval series by date and reconcile against:
   - Kerala SLDC observed daily net-import accounting where dates overlap;
   - SRPC published daily totals;
   - CEA FY2024-25 annual/peak reference values where scopes permit.
6. Keep scheduled drawal, actual interchange and Kerala state demand as separate fields.

The gate may move to verified only after the actual interval files are present and these checks pass.
