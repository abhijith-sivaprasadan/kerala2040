# Kerala2040 — an independent research story rooted in Kerala

## What the website says

Kerala2040 investigates how Kerala could become more energy-resilient by 2040,
while staying connected to India, respecting land and ecological limits,
and accounting for the real cost of each option. It is neither an official
government plan, a zero-imports campaign nor a completed 2040 model.

The public reading order: why the question matters; Kerala's measured
electricity system; what land and water permit; which future scenarios need
testing; industrial value; and finally the research ledger, scientific release
gates, original sources and public downloads. The homepage must tell this
story, not duplicate the research log as a wall of cards.

## Kerala-coded design

Use Malayalam titles with legible English science, culturally grounded
backwater/Ghats/paddy/palm/vallam illustration, kasavu edging, antique gold
and laterite accents. This is *art*, not GIS data. Themes are independently
composed: Kasavu (ivory, brass, forest), Monsoon (deep blue-green, sand) and
Laterite (clay earth, cream, leaf green). The Malayalam ക wordmark is
typographic and not an official seal. No arbitrary stock tourism imagery,
party symbols or fabricated geographic outlines.

Site sources: docs/index.html, docs/assets/app.js and docs/assets/kerala.css.
Static packaging serves only cache-busted versions of this app and stylesheet
and the mark icon, not old Plotly/Leaflet or orphaned previous theme assets.
Font services may fall back gracefully to local system fonts.

## Scientific and UX contracts

- All headline figures, GIS milestones, 2040 release gates and workstream
  statuses derive from the single publication-time audited research ledger
  plus the pinned observed-data manifest, not client-side claims.
- The observed FY2024–25 sample has 354/365 days; 11 missing original reports
  are not interpolated and breaks remain visible in the hand-built SVG chart.
  Observed-day energy is not hourly MW, transfer capacity, tariff or a full-year
  calibrated dispatch model.
- The research-audit date, original observed-data bundle timestamp and pinned
  checkout SHA remain distinct. Website deployment alone is not new evidence.
- Raw GIS downloads, candidate geometry repairs, point records, draft notices,
  or a successful CI build never establish legal exclusions, eligible km² or
  buildable MW; these remain false/null unless source admission gates pass.
- Keep development-only synthetic hourly loads, illustrative map points and
  unreleased model outputs outside the public website.
- Escape all source-fed HTML; allow only safe HTTPS external links and
  repository-scoped evidence links. Use readable labels, keyboard-operable
  controls, responsive layout, and reduced-motion handling.
- A source repo merge does not automatically publish. The independent
  website repo pins an immutable research commit in SOURCE_COMMIT. A visual
  release is not a new scientific model version.

## Updating the site

New research evidence updates committed QA and the research-ledger builder.
The field-note, land, research and audit views then update together through
a pinned build. Do not manually change a card to green after obtaining a ZIP
or running a model. The reader should always be able to distinguish what was
measured, what was audited, what is provisional and what remains unknown.

## Illustrated visual layer (September 2026)

- Original chapter SVGs: Ghats hydropower, wetlands/paddy/egret, tiled rooftop solar and grid, and material circularity. A same-origin SVG sprite supplies semantic icons. They illustrate concepts, never source GIS or measured physical energy flows.
- The favicon combines monsoon sun, coconut frond and backwater waves; its authored SVG also generates a 180x180 PNG touch icon.
- The separately authored 1200x630 social composition is rasterised as a genuine PNG in CI/Pages. Absolute Open Graph/Twitter metadata references the PNG. Build tests inspect its actual binary dimensions; SVG-only previews are inadequate.
- The small bottom-corner welcome card is dismissible, session-scoped and auto-dismisses. It never blocks the interface, focuses itself, changes body overflow, or delays evidence loading. Deep links and reduced-motion visitors skip it.
- Editorial movement is gentle sun/rain, chapter-art appearance and an explicitly conceptual current between research themes. It is disabled for prefers-reduced-motion; without IntersectionObserver the content remains fully visible.
- CairoSVG is a build-time-only dependency of research CI and pinned Pages. Public visitors do not run an image converter or retrieve remote art. No artwork or social thumbnail changes the scientific release classification.
