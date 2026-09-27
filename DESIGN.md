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

`docs/posters/Kerala2040_CET2026_Poster_Draft.pdf` is scientific draft 05, an A0 portrait poster. Its builder is `scripts/build_cet_poster.py` (ReportLab and Arial); the review output is `output/pdf/Kerala2040_CET2026_Scientific_Poster_v5.pdf`. The author is Abhijith Sivaprasadan, independent study, with KTH Royal Institute of Technology as the CET 2026 affiliation. No supervisor is listed.

The user rejected draft 04's house/palm motif and decorative navigation, requesting a complete return to the supplied Polygeneration example. Draft 05 uses its conventional academic hierarchy: a centered navy title band, separate outlined white section headings, project description beside technology figures, a full-width system framework and a three-column analysis section. There are no cultural motifs, locator decoration, numbered badges or navigation icons. Small equipment symbols in the technical schematic represent functional components; demand uses an electrical load symbol.

The six scientific figures are reorganized into A: observed balance; B: solar resource; C: EV charging; D: economic sensitivity; E: stateful Idukki; F: hydro timing windows. The observed balance now establishes the research problem before the model results. Display values remain rounded; source values and model calculations are unchanged. The 364-day and 365-day experiments have distinct chart forms and explicit horizons. Conclusions, limitations and references remain separate. The PDF contains selectable text and native vector graphics; no institutional logo or reference-poster research claim is copied.

Source status remains the reviewed 27 September snapshot at main commit `49acde2`, with PR105 explicitly under review. See `docs/posters/SCIENTIFIC_POSTER_EVIDENCE_NOTES.md`. QR integration and conference print specifications remain for a later pass.

## Phone-first edition 2 update, 27 September

QR visitors receive a compact opening with the existing fonts, Kerala illustrations and themes. A safe-area-aware bottom chapter bar keeps the four main destinations reachable. Themes live in the expanded header menu on small screens. All Canvas figures have touch-range controls with accessible selected values; chart, readout and slider occupy separate document-flow space. Chart labels and primary phone controls are larger, native form text avoids iOS focus zoom, and ornamental motion stops on small screens.

The published OSeMOSYS evidence is a frozen result artifact from workflow 36303344671 / PR106 head 9ba2688, explicitly under review. Two 168-hour cases and one 8,760-hour case pass their predeclared tolerance checks. The chart shows absolute differences divided by each metric's own tolerance, on a 0–100% scale. Raw result files and their hashes are retained. This is independent framework implementation evidence (both use HiGHS), never physical validation. KSEB acquisition and LRIS catchment status are updated separately.

The user is now composing the poster in Gamma. The approved draft05 remains the local PDF; `output/gamma` contains the self-contained prompt and real observation/charging CSVs. No unfinished poster06 replaces the approved poster.
