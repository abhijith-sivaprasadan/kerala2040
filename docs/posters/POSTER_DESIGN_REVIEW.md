# Scientific poster design review - draft 05

Rebuilt 27 September 2026 following the user's rejection of draft 04's decorative direction. Primary visual reference: the supplied **Polygeneration System for Cyclone Haiyan (Philippines)** A0 poster. This redesign follows its academic structure without copying its institutional emblem, authors or scientific claims.

## Applied structure

- Centered title, subtitle, author and affiliation in a single navy header.
- White, outlined heading boxes with large centered navy text.
- Top row: project context and objective with the observed electricity balance; beside it, solar and vehicle-charging figures.
- Middle: a full-width system schematic with functional equipment symbols and conservation equations.
- Analysis: three aligned columns for import-price sensitivity, stateful reservoir modelling and hydro timing windows.
- Separate conclusions, limitations and references, with compact captions and rounded displayed values.
- Removed the roof, palm, locator decoration, coloured number badges and navigation pictograms. The demand component uses an electrical load symbol rather than a house.

## Scientific continuity

All plotted coordinates and colour values use the existing source data. Figure lettering changes with the reading order: A observed balance, B solar, C charging, D economics, E reservoir, F timing windows. The economic scope, reconstructed water balance, observed-data gaps and different study horizons remain explicit. No model run, source gate or catchment admission changes in this visual revision.

The source status is still the previously reviewed 27 September snapshot, not a new repository assessment. The archived locator resource is unused by draft 05.

## Production

A0 portrait, native vector charts and selectable Arial text. Header title approximately 76 pt; section headings approximately 54 pt; primary explanatory text approximately 28-32 pt at print size. Source references and axis labels use smaller supporting text. Build the PDF with `scripts/build_cet_poster.py`; visually inspect a rendered page before delivery. QR integration and final printer specifications remain pending.

Verified output: one A0 page, 594 extracted words (down from 667), six native vector figures, zero raster images, three correctly positioned PDF links, no off-page words. Rendered and visually checked at 2,200 px height; Python formatting and lint checks pass.
