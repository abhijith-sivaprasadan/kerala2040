# 2040 published-demand PyPSA sensitivity (not a 2040 optimisation)

This workflow builds on the existing FY2024-25 observed SLDC evidence and the
8760-hour, explicitly *reconstructed* historical load chronology. It changes no
daily observations, fills none of the 11 missing source dates in the public archive,
and does not publish screening figures as validated CET results.

## What is new

- Read CSTEP 2024's FY2040 reported final electricity demand *including its
  reported losses*: 45,519 MU, from the committed source-transcribed CSV.
- Keep separately the 2026 CN50 study's 2040 BAU and transition net-grid-demand
  reference cases: 65.98 TWh and 88.56 TWh. These have DIFFERENT study scopes
  from CSTEP's final demand; they must not be averaged, ranked as equivalent
  forecasts, or fitted as though they had identical accounting boundaries.
- Scale all 8760 hours of the FY2024-25 load *proxy* by a single factor so the
  chosen reported annual energy is conserved exactly. Then sample 24..8760 hours.
- Reuse the existing PyPSA/HiGHS operational sensitivity with FY2024-25 daily
  hydro and other in-state energy frozen at daily-average MW, and with explicitly
  assumed import/PV/BESS values. These are illustrative future-demand experiments
  **not** a forecast of 2040 plant operation, import adequacy or investment.
- Produce labelled PNG figures, dispatch CSV, full assumption and provenance
  summary, and a separate published-reference CSV. Nothing is sent to Pages.

The underlying source dates remain April 2024 to March 2025, because they are
the representative *shape/weather year*. They are NOT 2040 timestamps. This
avoids treating a 8760-hour shape as a 2040 leap-year calendar.

## Run

Install project development dependencies, then:

    python scripts/run_2040_proxy_screening.py --acknowledge-proxy

Full-year sensitivity, if resources permit:

    python scripts/run_2040_proxy_screening.py --acknowledge-proxy --hours 8760

Use one separate published reference case:

    python scripts/run_2040_proxy_screening.py --acknowledge-proxy --hours 168 --benchmark cn50_2026_bau

For optional *additional* PV and fixed battery sensitivity, edit
configs/pypsa_screening_example.yaml. Additional PV needs the existing
data/processed/renewable_availability_proxy.parquet resource-availability
data. That is MODELLED RESOURCE, not measured generation. Existing reported
nonhydro generation remains in the fixed 2024-25 baseline; do not count the
same PV twice.

Outputs are placed in results/models/2040_proxy_screening/ by default.
A 48-hour smoke run produces **48-hour outcomes only**; the summary separately
records the full-year external demand target and whether all 8760 hours were
solved. Do not multiply a short-window import or reliability result to a year.

## Hard boundary on conclusions

- FY2024-25 installed capacity and energy are deliberately retained as a
  *frozen historical counterfactual*, not 2040 commissioned assets.
- 6500 MW is an example import bound, NOT Kerala's documented transfer rating.
- Screening objective units are abstract weights, NOT INR/MWh.
- There is no measured interval demand, measured interval imports, physical
  reservoir cascade, verified 2040 asset register, or model-ready regional GIS
  ceiling in this experiment.
- The technology cost grid at configs/techno_economics.yaml still contains null
  Kerala 2040 inputs. Do not silently inherit CEA external benchmarks.
- This pipeline does NOT optimise capacity, value a project, or establish
  electricity sovereignty or reliability under real 2040 conditions.

The next scientific release gate is harmonised dated 2040 costs, candidate
capacities/resource profiles, hydro energy and operating constraints, transfer
limits, and calibrated measured intervals. Only then move from an illustrative
operational sensitivity to a defensible capacity-expansion and stress-test model.
