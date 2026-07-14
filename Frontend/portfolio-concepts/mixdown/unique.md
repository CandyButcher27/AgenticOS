# Why Mixdown is unique

**Core mechanic:** the only concept with continuous ambient animation (VU meter) driven by real user-adjustable input (the Energy fader) — the page has a "live" quality even when the user isn't interacting.

**Not shared with any other concept in this set:**
- Only build with rotary controls (knobs) — Physics has drag, Terminal has typing, Starchart has click, but only Mixdown has drag-to-rotate.
- Only build where one control (Hue Shift knob) directly rewrites the page's own CSS custom property live — the UI edits itself as a feature, not just a display.
- Tracklist-as-navigation (rows that "play" and stay highlighted) is a distinct selection model from Woven's patches or Starchart's stars — it has explicit state (which track is "playing") that persists after interaction.
- Palette fingerprint (charcoal + rust-copper + teal) is unique in this set — no overlap with any other build's hues.

**Bug this design avoided:** the initial knob build computed rotation from absolute cursor angle, which wraps unpredictably near the bottom of the control. Rebuilt to use vertical-drag-distance instead — the same model real mixer hardware and DAW plugins use.
