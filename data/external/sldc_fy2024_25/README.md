# SLDC FY2024–25 first-pass processed evidence

This package is a **derived extraction of the uploaded sldc_archive.zip**, not new measurements. Keep the original user archive and its raw HTML. The source SHA-256 is recorded in `qa_report.json`; individual response SHA-256 is retained in every row and may be matched to the original `index.csv` and manifest.

Every recorded number is sourced from a dated public SLDC report; no missing dates, empty fields or other values have been inferred, filled or converted to zero. The FY2024–25 totals are sums **only over observed days**. Import-interface sums are descriptive checks, not physical import capacity.

`daily_balance.csv`: one row per FY day, including 11 missing-date markers. Units MU (million kWh), i.e. 1 MU = 1 GWh.

`hydro_station_daily.csv`: names exactly as printed, including the date's reported maximum MW. This is not a commissioned-capacity register. A blank reported generation is unknown, not zero.

`import_interface_daily.csv`: reported import energy by named 400/220/110 kV grouped interface, not individual physical line ratings.

`reservoir_daily.csv`: reported levels, volumes, storage %, and gross/station generation capability. These source headings are retained as separate fields; do **not** sum station capability across reservoirs or impose cascade topology without independent review.

`selected_intraday_extrema.csv`: only published morning/day/evening/night selected extrema, not a complete measured load curve.

`qa_report.json`: date/section coverage, cryptographic integrity, accounting checks and documented limitations. Raw archive has redundant table_01 and table_03 extracts; table_03 is used for normalization, preventing double-counting.

This dataset can feed observational plots and validate a historical **daily energy** representation. A calibrated hourly PyPSA model still requires actual 8,760/35,040 time-block load and interchange observations, independently sourced cost/asset constraints and hydro physical mapping.