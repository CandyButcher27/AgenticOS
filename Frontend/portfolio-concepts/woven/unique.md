# Why Woven is unique

**Core mechanic:** the only concept where the entire visual structure (hero background, section dividers, and layout metaphor) is generated from one procedural SVG-drawing function — nothing else in this set reuses a single animation technique across that many surfaces.

**Not shared with any other concept in this set:**
- Only build using `stroke-dasharray`/`stroke-dashoffset` "draw-in" animation — Blueprint/Physics/Mixdown/Starchart all animate via transform/opacity or canvas redraw, never path-drawing.
- Only build with a scroll-triggered *structural* animation (section-divider weaves) as opposed to scroll-triggered *content* reveals (Blueprint's panel fade-in) — the divider itself is the animated element, not a wrapper around static content.
- Palette (indigo + rust + linen/walnut) is drawn from dyed textile, sharing no hues with any other concept — including avoiding the cream/terracotta combination common to generic AI-generated design.
- Display typeface (warm rounded sans) is deliberately distinct from Starchart's serif and Blueprint/Terminal's monospace — no two concepts in this set share a display face.

**Bug this design fixed:** the hero weave (`#heroWeave`) was missing the CSS class that applies `stroke`/`fill: none` to its generated paths, so its threads rendered with the SVG default black fill — a solid black shape behind the hero text instead of faint lines. Fixed by extending the shared selector to cover `#heroWeave path` explicitly.
