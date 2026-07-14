# Why Terminal OS is unique

**Core mechanic:** the *only* concept navigated by typing — real keyboard input, command history, Tab-complete. Every other concept is navigated by mouse/touch (drag, click, scroll, hover).

**Not shared with any other concept in this set:**
- Only build with a scripted boot sequence (timed fake system checks) gating the interactive part of the page.
- Only build where "wrong input" is a real state the user can hit (`command not found`) — every other concept has no invalid-input path.
- Amber-phosphor palette is its own fingerprint — no other concept uses warm near-black + amber.
- Content is retrieved on demand (`cat`, `ls`, `open`) rather than laid out up front — the page is mostly empty scrollback until you ask it for something, the opposite of Starchart/Woven/Mixdown which show everything immediately.

**Risk it deliberately avoids:** the obvious version of "developer terminal portfolio" is matrix-green-on-black. This uses amber phosphor instead, which reads as a specific real hardware reference (vintage terminal) rather than a movie prop.
