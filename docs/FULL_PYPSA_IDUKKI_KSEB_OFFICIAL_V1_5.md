# Full-PyPSA Idukki official-KSEB checkpoint v1.5

v1.5 is the first stateful Idukki checkpoint whose reservoir storage endpoints
and daily water input are gated directly from KSEB Dam Safety monthly workbook
fields rather than a reconstructed residual or the incomplete private SLDC
daily-inflow archive.

## Required source

The runtime source is the twelve official KSEB monthly workbooks for April 2024
through March 2025. Before the model can run, the ingestion chain must prove:

- exactly twelve audited XLS/XLSX files;
- one SHA-256 per source file;
- 365 unique Idukki calendar dates;
- direct `Live Storage (MCM)` on every date;
- direct `Inflow (MCM)` on every date;
- no interpolation;
- reconciliation against the separately recovered official KSEB daily pages.

The optimization uses 364 daily inflow transitions from 1 April 2024 through
30 March 2025 and constrains the terminal state to the direct 31 March 2025
KSEB storage observation.

## Model

The optimization is deliberately inherited from v1.4:

1. minimize total unserved energy;
2. preserve the minimum shortage and minimize annualized candidate investment
   plus import-energy cost;
3. preserve stage-2 cost and minimize endogenous non-turbine water release.

This keeps v1.3/v1.4/v1.5 differences attributable to the reservoir water
source rather than a simultaneous objective change.

## Remaining boundary

The historical diagnostic still uses the existing SLDC Idukki station
generation series divided by 1470 MWh/MCM to estimate turbine-water equivalent.
That generation boundary contains the previously documented imputed days.

It is used for:

- the historical water-balance diagnostic; and
- subtracting historical Idukki generation from admitted total daily hydro to
  define the non-Idukki hydro block.

It is **not** used to manufacture KSEB inflow.

The model's endogenous non-turbine-release variable remains a slack/tie-break
water outflow. It must not be described as observed spill until a unit-explicit
observed spill/release chronology is admitted.

## Run

Gate only:

```bash
python scripts/run_full_pypsa_idukki_kseb_official_v1_5.py \
  --kseb-bundle-dir PRIVATE/kseb_monthly_fy2024_25 \
  --gate-only
```

Full matrix:

```bash
python scripts/run_full_pypsa_idukki_kseb_official_v1_5.py \
  --kseb-bundle-dir PRIVATE/kseb_monthly_fy2024_25
```

The full matrix is 2 demand cases × 3 transfer cases × 2 Idukki powerhouse
availability cases = **12 physical solves**, each with the same three-stage
lexicographic objective as v1.4.
