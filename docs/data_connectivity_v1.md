# Data connectivity — v1.0

Version 1.0 is the first operational data-connectivity release. It is **not** a
validated 2040 scenario release.

## Connected sources

| Source | v1 mode | What is connected | Status rule |
|---|---|---|---|
| Kerala SLDC | public HTML + date form | daily system statistics; historical date requests | core |
| NASA POWER | public JSON API | hourly temperature, RH, irradiance, 10 m wind, precipitation | core |
| data.gov.in OGD | authenticated JSON API | generic paginated resource client | optional until key/resource configured |
| NITI ICED | web discovery/download | page availability and visible downloadable links | discovery only |

The source-health workflow exercises the two core live sources independently of
deterministic unit tests. This means a temporary external outage can be seen
without making the normal code test suite non-deterministic.

## Kerala SLDC semantics

The public page exposes several different concepts that contain the words
"import" or "net import". v1.0 deliberately keeps them separate:

- `net_import_interface_mu`: interface energy contributing to the state balance;
- `ui_import_mu`, `ui_export_mu`, `ui_net_import_mu`: separate UI/deviation-account rows;
- `interstate_purchase_sale_mu`: interstate purchase/sale accounting row;
- `net_schedule_mu`: scheduled external energy.

No downstream model may merge these merely because their labels sound similar.
The first validation identity is:

`internal_generation_mu + net_import_interface_mu ≈ consumption_mu`

with the residual retained explicitly as `balance_error_mu`.

Historical requests are rate limited (0.8 s by default) and raw-response SHA-256
hashes are recorded. Large raw HTML responses are not committed.

## NASA POWER semantics

Every request explicitly asks for `time-standard=UTC`. The connector writes both
UTC and `Asia/Kolkata` timestamps. The API-provided fill value (commonly `-999`)
is converted to missing data, never to zero. Units returned by the API remain in
the run manifest.

Five Kerala city points are configured only as a first weather sampling frame.
They are **not** treated as an area-weighted statewide renewable resource model.

## Credentials

`DATA_GOV_API_KEY` is read only from the environment/GitHub secret store.
A resource must also be explicitly identified (`DATA_GOV_RESOURCE_ID` for the
health probe or an ID supplied to the client). No API keys or guessed resource
IDs belong in git.

## What v1.0 does not claim

- ICED does not have a fabricated "API" in this project.
- SLDC daily statistics are not an 8,760-hour load curve.
- NASA POWER city points are not statewide renewable potential.
- No 2040 scenario result is validated yet.

The next hard gate remains the historical electricity baseline and 8,760-hour
calibration dataset.
