# Request for underlying CSTEP Kerala 15-minute load data

## Purpose

The Kerala 2040 research project is independently reconstructing and validating Kerala's
historical electricity system before running 2040 capacity-expansion scenarios.

CSTEP's *Kerala Energy Transition Roadmap 2040* (CSTEP-RR-2024-01, February 2024)
states on page 33 that the study analysed 15-minute block-wise Kerala data observed in FY2016,
derived an extrapolated FY2022 load curve, and then extrapolated that shape to future years.

The published report contains the plotted curve but not the underlying block-wise series.

## Suggested request

Subject: Request for underlying FY2016 15-minute Kerala load series used in CSTEP-RR-2024-01

Dear CSTEP / EMC Kerala / KSEBL / Kerala SLDC team,

I am conducting an open, reproducible research study of Kerala's electricity system and its
2040 transition pathways. I am using CSTEP's *Kerala Energy Transition Roadmap 2040*
(CSTEP-RR-2024-01) as an external benchmark.

On page 33, the report states that 15-minute block-wise Kerala data observed in FY2016 were
analysed to derive the FY2022 load curve. I would like to request the underlying FY2016
15-minute demand/load series used for that analysis, if it can be shared for academic research.

Ideally, the dataset would include:

- timestamp or date plus 15-minute block number;
- Kerala state demand/load in MW;
- timezone and block convention;
- any missing, estimated or revised-data flags;
- the source system or original data custodian;
- units and any transformations applied before use;
- revision/version information, if applicable.

If the exact raw series cannot be shared, a machine-readable version of the series used to
produce Figure 12, with its provenance and any preprocessing notes, would still be valuable.
If available, I would also appreciate the corresponding FY2022 extrapolated series used by
the study so that the published methodology can be reproduced.

I would use the data only with explicit provenance and would clearly distinguish measured
observations from reconstructed or modelled series. Please also let me know any attribution,
licensing or publication restrictions that apply.

A separate methodological clarification would also be useful. Figure 14 reports storage
requirements such as 3.8 GW / 7,163 GWh for BAU FY2040 and 4.1 GW / 8,108 GWh for
High-RE FY2040. Could you clarify the definition of the reported GWh quantity (for example,
whether it is instantaneous energy capacity, cumulative shifted energy, or another metric) and,
if possible, the storage calculation method used?

Thank you.

## Routing

Potential custodians/contacts, in order:

1. CSTEP authors / CSTEP energy team — immediate study authorship.
2. Energy Management Centre Kerala — acknowledged study support and likely state-side context.
3. KSEBL — historical system data custodian.
4. Kerala SLDC — operational demand and interchange data custodian.

The report lists CSTEP's general energy contact as `cpe@cstep.in`. Verify the current contact
before sending.

## Provenance rule

Do not convert Figure 12 into "measured FY2016 data" by digitising it. If figure digitisation is
ever used as a temporary comparison, classify it explicitly as a figure-derived proxy and retain
the report/page reference.
