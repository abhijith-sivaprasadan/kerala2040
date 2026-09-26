# Kerala2040: website edition 2

The visitor journey follows one question: how can Kerala meet future demand reliably while respecting its land and water? The five chapters are observed electricity, land and seasons, future choices, industrial energy, and evidence. Research detail belongs behind deliberate disclosure, not ahead of the story.

## Visual and interaction contract

- Kasavu ivory, forest green and brass carry the existing Kerala identity. Monsoon offers a dark backwater theme; Laterite brings red earth and palm. Malayalam is used as supporting typography.
- Retain the original Kerala landscape, illustrated chapter artwork and icon sprite as decorative identity. These are conceptual depictions, never maps or research results. The user clarified that images/SVG are welcome for webpage components; only data charts must remain live. Charts use first-party Canvas; controls, tables and sensitivity cells use semantic HTML.
- One sticky navigation becomes an expandable in-flow menu on small screens. Existing section hashes remain valid, including workbench and audit disclosures.
- Charts support pointer and keyboard inspection. Source data is downloadable. Observation and pilot tables give exact values without interpreting pixel positions.
- Subtle water, palm and boat motion respects reduced-motion preferences. No forced introduction. Reduced motion disables smooth scrolling and transitions.

## Evidence contract

- FY2024-25 remains 354 observed days, with 11 unfilled missing reports. Monthly energy is an observed-day mean; import share is the ratio of recorded energy totals.
- Hydro is a component of in-state generation. Reservoir energy storage is not water volume.
- Source-grid solar and wind describe resources, not eligible land or permitted MW. Thresholds count source centres, not sites.
- WP6 experiments use fictional inputs. All six published families remain available: EV, industrial scheduling, BESS, pumped-storage analogue, cooling/TES and integrated dispatch.
- The v1.0 economic and v1.1/v1.2 hydro-timing and v1.3 Idukki PyPSA results are separately labelled partial economic sensitivities. The selected 2030 comparisons are not a 2040 forecast or a recommended capacity plan. V1.2 timing windows are synthetic bounds, never reservoir storage durations. V1.3 uses a separate 364-day horizon with model-only gap interpolation and reconstructed net water balance; comparisons use its own same-horizon results. V1.4–v1.5 source audits are published separately from solved model results.
- The observed-bundle timestamp, resource-audit date, model-result date and publication commit remain separate. Build metadata records the source path and SHA-256 of each new model evidence file.
- Original source products stay in the searchable evidence library. A visual release never promotes scientific gates.

## Build and verification

Source files: `docs/index.html`, `docs/assets/app.js`, `docs/assets/kerala.css`.

Build with `PYTHONPATH=src python scripts/build_site.py --output _site`. Assets receive content hashes. The builder retains the scientific bundle validation and checks static references.

Run `node --test tests/web.test.cjs`, `pytest tests/test_site.py`, and the CI browser suite `node tests/site.browser.cjs _site`. Browser checks cover chart controls, keyboard reading, all source downloads, responsive widths, deep links, themes and a failed data request.

The separate Pages repository continues to pin an immutable research commit in `SOURCE_COMMIT`.

## CET 2026 poster

`docs/posters/Kerala2040_CET2026_Poster_Draft.pdf` is an early A1 portrait draft. Its charts use the same source evidence. The source builder is `scripts/build_cet_poster.py` (ReportLab and Arial/Georgia fonts). Final author/institution credits, conference specifications and QR integration remain editorial steps for the final poster.

The composition borrows the supplied Polygeneration poster's results hierarchy and the plain-language finding emphasis described in the [BetterPoster design discussion](https://blog.nrca.uconn.edu/2019/12/12/better-poster/). It does not reproduce that poster's project claims, branding or artwork.
