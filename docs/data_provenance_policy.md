# Data provenance and synthetic-data policy

This project must never allow a convenient reconstruction, assumption or model output to
masquerade as observed evidence.

## Mandatory classifications

Every dataset, model input, chart, table and published metric must be classified as one of:

- `measured`: directly observed operational or metered data from an identified source.
- `official_observed_reference`: an observed value published by an official authority,
  but not necessarily supplied as raw operational telemetry.
- `derived_from_measured`: arithmetic transformation or aggregation of measured data.
- `reanalysis`: meteorological/climate reanalysis such as ERA5.
- `remote_sensing_or_reanalysis`: products such as NASA POWER used as environmental input.
- `modelled_resource_profile`: a calculated renewable-resource availability profile derived
  from weather/reanalysis. This is not measured plant generation.
- `proxy_reconstruction`: a synthetic chronology reconstructed from incomplete observed data.
- `scenario_assumption`: a user/model assumption introduced for a future or stress scenario.
- `published_external_scenario`: a result from another study retained only as a benchmark.
- `illustrative`: a marker, example or screening construct with no claim of observational truth.
- `unresolved`: required data that have not yet been secured or selected.

## Mandatory source fields

Organic/observed/reanalysis data must retain, where applicable:

- source organisation;
- source dataset/report title;
- source URL or file identity;
- source period/vintage;
- retrieval date;
- raw or source hash where available;
- units;
- transformation steps;
- licence/access restrictions.

## Synthetic-data rule

Synthetic or reconstructed data may be created only when:

1. the original data gap is explicitly recorded;
2. the method is documented;
3. the output is labelled `proxy_reconstruction`, `modelled_resource_profile`,
   `scenario_assumption` or another clearly non-observed classification;
4. the synthetic layer is kept separate from observed evidence;
5. charts and tables visibly identify it as synthetic/modelled;
6. it is not used to claim historical observations;
7. it is excluded from a calibration gate that is described as observed-only unless the gate
   explicitly states otherwise.

## No silent substitution

The project must not silently:

- interpolate missing observations;
- substitute one accounting definition for another;
- replace missing plant generation with weather-derived output;
- treat published study scenarios as Kerala 2040 model results;
- infer ownership, capacity, generation or costs from names or contextual clues;
- fill missing techno-economic inputs with generic defaults;
- convert a source catalogue into a claim that the underlying dataset has been acquired.

If a required value is unavailable, it remains null/unresolved.

## Current known non-observed layers

- FY2024-25 hourly load proxy: `proxy_reconstruction`; not measured hourly telemetry.
- Missing 11 SLDC daily consumption totals inside that proxy: interpolated and flagged.
- Weather-derived solar/wind availability: `modelled_resource_profile`; not measured generation.
- Drought multipliers in the CET stress config: `scenario_assumption`; provisional.
- Screening nodes: `illustrative`; not validated grid nodes or siting decisions.
- CI PyPSA smoke-test load/generators: synthetic software test fixtures only.

This policy applies to repository code, generated artifacts, website copy and research outputs.
