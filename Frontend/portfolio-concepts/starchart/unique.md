# Why Starchart is unique

**Core mechanic:** the only concept rendered entirely on `<canvas>` rather than DOM elements — stars, constellation lines, and hit-testing are all pixel-drawn per frame, not styled divs.

**Not shared with any other concept in this set:**
- Only build using an italic serif as the *display* face — every other concept uses sans (Physics, Mixdown, Woven) or monospace (Blueprint, Terminal). No monospace appears anywhere in Starchart at all.
- Only build with two independently-parallaxing depth layers (background stars vs. labeled project stars) driven by a single mouse-position value — a real illusion of depth, not a flat pan.
- Click targets are canvas coordinates cached from the render loop, not real DOM elements — interaction model is closer to a game canvas than a webpage.
- Palette (void navy/black + gold, or parchment + bronze) doesn't overlap with any other concept.

**Risk it deliberately avoids:** "developer portfolio in space" defaults instantly to neon sci-fi. Referencing engraved star atlases instead — italic serif, gold leaf, fabricated RA/Dec coordinates — sidesteps that cliché entirely.
