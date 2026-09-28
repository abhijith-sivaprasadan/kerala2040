# ERA5 weather-sensitive hourly Kerala load proxy — 27 September 2026

**Classification: proxy reconstruction, not measured telemetry.**

The FY2024–25 hourly demand proxy now uses the full state-area ERA5-Land chronology together with the published Kerala SLDC intraday extrema. Every one of the **354 observed SLDC daily consumption totals is conserved**; the existing **11 missing daily totals remain model-only interpolations and are flagged**.

## What changed

The earlier proxy applied the same two-peak shape to every day. The new proxy fits a smooth clock-time shape from April–December 2024 selected SLDC consumption extrema, adds weekend shape terms, and then lets hourly ERA5 cooling, humid heat, solar radiation, rainfall and wind perturb the within-day shape. Each day's 24 values are renormalized back to its daily energy total. CEA's FY peak and load-duration distribution are retained as aggregate calibration constraints.

## Held-out shape test

January–March 2025 SLDC extrema were withheld from the fit. On **430 held-out reported extrema**:

| Proxy | MAE MW | RMSE MW | Correlation |
|---|---:|---:|---:|
| Released fixed two-peak proxy | 367.9 | 477.9 | 0.659 |
| Sparse-extrema static shape | 132.8 | 162.0 | 0.966 |
| **ERA5 weather-sensitive shape** | **124.9** | **155.2** | **0.968** |

Relative to the released fixed shape, held-out RMSE falls by **67.5%**. Against the already much stronger sparse-extrema static model, ERA5 still reduces held-out RMSE by **4.2%**. This is evidence that weather adds useful *shape* information; it is not evidence of measured hourly accuracy.

The reconstructed FY peak is **5923.3 MW**, versus the **5904 MW CEA generation-resource-adequacy planning reference** used by this proxy (+0.33%). This must not be confused with the separate **5797 MW FY2024–25 recorded peak** reported in the newer CEA Kerala transmission-resource-adequacy plan. The two CEA products use different planning/reporting contexts, and Kerala2040 does not force them into one value. The 5904 MW figure is therefore a calibration/consistency anchor, not independent proof of the true continuous-hour annual maximum. CEA load-duration bins remain approximate secondary constraints; the model prioritizes the timestamped SLDC extrema and exact daily-energy conservation.

Held-out error by published extrema category for the ERA5-sensitive shape:

| Category | MAE MW | RMSE MW |
|---|---:|---:|
| Day maximum | 84.8 | 104.3 |
| Evening maximum | 123.6 | 154.0 |
| Morning maximum | 135.0 | 152.3 |
| Day minimum | 136.7 | 172.1 |
| Night minimum | 134.5 | 171.3 |

## Weather terms

The fitted weather coefficients are associations inside a daily-normalized proxy:

- cooling above 24 °C: +0.0094
- 3-hour trailing cooling: +0.0318
- humid heat / dew point above 20 °C: +0.0709
- downward shortwave radiation: −0.0605
- rainfall: −0.0377
- 10 m wind speed: −0.0105

They must **not** be interpreted as causal demand elasticities. ERA5-Land is reanalysis weather and the target is a reconstructed within-day load shape, not measured hourly demand.

## PyPSA use

This profile replaces the generic fixed-shape proxy as the default input to the **experimental chronological PyPSA screening**. It does not change the model's other physical gates:

- existing hydro and non-hydro generation remain daily-average replays;
- hourly imports remain model outcomes under an explicit screening bound;
- reservoir/cascade operation is not inferred;
- the 11 missing SLDC dates remain model-only interpolations;
- no 2040 investment result is claimed from this historical screening.

Before the solver is run, the derived chronology is cryptographically checked and expanded from a compact 8,760-value payload. The no-additions accounting check still requires modelled imports to reproduce each observed day's SLDC import energy to within 0.001 MU.

A local pre-solve compatibility check gives a reconstructed load range of **2318.6–5923.3 MW**. With the current daily-average generation replay, residual hourly import requirement stays positive and below the deliberately illustrative 6500 MW import bound. This is only a consistency check; the actual PyPSA solve is performed in CI with HiGHS.

## Storage and provenance

The public repository contains only the derived hourly load chronology as a checksummed split base64/zlib payload plus fit metadata. It does **not** commit the raw ERA5 GRIB or detailed ERA5 hourly weather rows.

Source fingerprints:

- ERA5 user archive SHA-256: `6bfbebd47ddf6c53a71b683956731ead4214495c8403d56799da7e3cf14f6d0d`
- SLDC five-section archive SHA-256: `2d55fefdcbfcacf7f753cebb0c429479abb6ea5eedb2533297a455735b6bfc3f`
- NWIC/SOI state-boundary original SHA-256: `a932ea29e7afd0fea1e1068f3beeeadb760e6b2baae9783f5822bbefd4224ebd`
- derived compact proxy JSON SHA-256: `ff6cbccddd099ee1002001c33bc6f154e4abbd680d4e3c107eea67bc4db3d1f0`

## Remaining gate

This is a better *reconstruction*, not a replacement for actual state 15-minute/hourly telemetry. Planning-grade chronology still requires the underlying measured load and interchange series, plus physical hydro and transfer constraints.
