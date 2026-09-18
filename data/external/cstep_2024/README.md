# CSTEP 2024 external benchmark extraction

Source: Center for Study of Science, Technology and Policy (CSTEP), *Kerala Energy Transition Roadmap 2040*, February 2024, report CSTEP-RR-2024-01.

Primary publication page: https://cstep.in/publication/kerala-energy-transition-roadmap-2040/

## Provenance classification

Every file in this directory is classified as `published_external_scenario` or
`official_observed_reference_as_republished_by_cstep`. None of these values is a
Kerala 2040 model result produced by this repository.

Where the report reproduces historical KSEB/CEA/Vahan values, the immediate source
for this extraction is still the CSTEP report and the upstream source named by CSTEP
is preserved in metadata. The project should prefer the original upstream dataset
when it is independently acquired.

## Files

- `historical_category_consumption_fy2016_fy2022.csv`: CSTEP Table 4, historical KSEB category sales/consumption.
- `demand_projection_fy2023_fy2040.csv`: CSTEP Appendix Table 1, annual demand pathway by category plus EV, induction cooking and T&D losses.
- `ev_projection_milestones.csv`: CSTEP Tables 8 and 10, EV stock and annual energy-demand milestones.
- `peak_demand_projection_milestones.csv`: CSTEP Table 13 peak/off-peak demand milestones.
- `capacity_additions_bau_fy2023_fy2040.csv`: CSTEP Appendix Table 4.
- `capacity_additions_high_re_fy2023_fy2040.csv`: CSTEP Appendix Table 6.
- `renewable_potential_benchmarks.csv`: CSTEP GIS/resource-potential results.
- `storage_benchmarks.csv`: values read from CSTEP Figure 14 and accompanying text.
- `metadata.yaml`: report metadata, modelling assumptions, page provenance and warnings.

## Important limitations

CSTEP states that its FY2022 load curve was **derived from observed FY2016 15-minute Kerala data** and that future load curves were extrapolated assuming a similar shape. The report does not provide the raw FY2016 15-minute series. This is therefore an acquisition lead, not a substitute for measured telemetry.

The storage-energy values reported in Figure 14 are preserved exactly as published. Their very long implied durations should not be silently reinterpreted or unit-corrected; the underlying calculation must be traced before those values are used as a modelling target.

Small 1-2 MU discrepancies exist between some published component rows and published totals in the appendix. The extraction preserves the report values exactly rather than forcing arithmetic closure.
