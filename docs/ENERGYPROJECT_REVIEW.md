# Energy Project review — 18 September 2026

Inspected: [home](https://www.energyproject.in/),
[electricity](https://www.energyproject.in/grid),
[petroleum](https://www.energyproject.in/petroleum).

The site combines EV registrations, electricity and petroleum. Its electricity
page presents national average intraday generation/demand, day-ahead prices,
monthly trends and storage charging/discharging, citing NLDC, IEX and CEA.
The home page identifies VAHAN for EV statistics. The grid page clearly labels
its current-month figures as incomplete and gives a data date.

## Relevance to Kerala 2040

- Useful presentation reference: begin with measured charts, then allow period,
  unit and subject comparisons; keep sources and freshness visible.
- Useful national context for generation timing, market prices, EV adoption and fuels.
- A national average day is not Kerala's chronological hourly demand or actual
  interchange series. Never label an extrapolated average profile as an observed year.
- No public Kerala-specific raw demand/interchange download was established from
  the inspected pages. This does not establish that the operator lacks other data.
- Some historical navigation carries lock icons. Public chart visibility does not
  establish raw-data access or reuse permission.
- Their clean-generation share includes storage discharge. Our model must track
  charging source, losses and discharge separately: storage shifts energy and is
  not a primary energy source or automatically zero-carbon.

Their published contact is hello@energyproject.in. A useful question is whether
their NLDC workflow includes historical state-level time-block demand/interchange,
which primary archive it uses, and what reuse terms apply. No outreach was sent
and no message has been sent.

## Public chart inputs verified during this review

The public grid page's client JavaScript fetches JSON under `/data`. Verified
endpoints are `/data/grid/monthly_summary.json`, `/data/grid/daily_summary.json`,
`/data/capacity.json`, `/data/grid/timeseries/2026-09.json` and
`/data/dam/2026-09.json`. The first three provide national summaries; the latter
two are the default month's generation and market interval products. This
establishes how the browser receives data, not how the publisher extracts its
upstream NLDC/IEX/CEA records. No upstream ETL implementation was established.

The September snapshot contains 17 complete generation days (1–17 September)
and 18 market days (1–18 September), with 96 quarter-hour observations per day.
The JSON does not declare its timezone. Market clearing prices are divided by
1,000 from rupees/MWh to rupees/kWh, matching the site's client conversion.
Historical interval navigation marked as requiring sign-in was not traversed.

`scripts/ingest_energyproject.py` reproducibly fetches the public summary and
latest month's two interval products. It retains raw responses and SHA-256
hashes locally and publishes limited derived average-day profiles with source
attribution, per-field sample counts, date coverage and explicit limitations.
No redistribution licence was established; the raw archive is not republished.
Run it manually, then `scripts/build_web_bundle.py` and `scripts/build_site.py`
to update the snapshot. No credentials or live third-party requests are needed
by visitors to the published dashboard.

These profiles support national context charts only. They must not fill the
Kerala hourly demand/interchange gap, become a Kerala tariff, or be treated as
a full-year model input. A missing field remains missing in the averages.
