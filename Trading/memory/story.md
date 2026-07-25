# The story so far

## Where it started

"Let's build a trading bot — start with yfinance, get some data, keep a
venv." That was the whole ask. We scoped it down hard before writing any
code: single ticker (SPY), daily bars, local parquet cache, custom
backtest loop instead of a library. Then the real strategy showed up —
not a generic moving-average thing, but a specific weekly options trade:
every Monday, use the spot price and implied volatility to compute an
expected move, sell a put below it and a call above it (a short
strangle), and hold to Friday.

## The first wall: yfinance doesn't have what we need

First real problem, before writing a line of strategy code: `yfinance`
only returns the *current* options chain. There's no historical options
data — no way to know what a SPY put actually cost in March 2020. That
would normally be a blocker. The workaround: use `^VIX` as a stand-in for
implied volatility, and price everything synthetically with Black-Scholes
instead of real market quotes. Every number this project produces from
here on is downstream of that one substitution, and it gets flagged
explicitly in every result: these are theoretical premiums, not real
fills.

## Getting the mechanics exactly right

A lot of early back-and-forth was just making sure the mechanics were
correct, not the strategy. Several corrections along the way:

- VIX is quoted in percentage points (20.5 means 20.5%), so it has to be
  divided by 100 before it's usable as a decimal in the formulas —
  confirmed explicitly rather than assumed.
- Strikes aren't placed exactly at the calculated boundary — they're
  rounded *outward* to the nearest real strike increment, and the option
  premium is priced at that rounded strike, not at the raw boundary.
- It's a **sale**, not a purchase — this took a correction. Short
  strangle means collecting premium upfront and owing money back only if
  a strike finishes in the money. And it's 1 contract per leg, not "100
  lots" — the ×100 in the math is the per-contract share multiplier, not
  a trade size.
- VIX gets re-read fresh every single week, not held constant for a
  month — an assumption worth checking explicitly rather than letting
  slide.

Getting this right before scaling up mattered: the whole point of running
one week's numbers by hand first was to catch exactly these kinds of
misunderstandings while they were cheap to fix.

## The baseline, and its first real flaw

Once the mechanics were solid, `test_v1` ran the strategy across five
years, 2020-2025, no risk management at all. It made money — but almost
all of it came from a single good year (2021). One bad week (April 2025,
a tariff-shock selloff) wiped out most of five years of gains in a single
trade. That's the moment this stopped being "does the strategy work" and
became "how much of this is real edge versus tail risk waiting to
happen."

## Adding a stop-loss, and immediately asking whether it's real

The obvious fix was a stop-loss: if price moves too far against the
position mid-week, close it early instead of riding it to expiry. First
attempt used a stop at 0.95× the expected move, and it helped — better
P&L, roughly double the Sharpe ratio, smaller worst-case losses. But the
next question mattered more than the first result: *is 0.95 actually the
right number, or just a guess?*

## Sweeping instead of guessing — and finding the first trap

Swept the stop-loss factor across a wide range instead of picking one
number. The naive answer — whichever factor maximized the Sharpe ratio —
turned out to be a trap: the "best" value triggered the stop on 99% of
trades, meaning the strategy was exiting almost immediately every single
week. That's not a tuned strategy, that's barely trading at all. Excluding
that degenerate region, a real sweet spot emerged around 0.85 — better
than the original 0.95 guess on every meaningful number.

## Breaking it down by year — and a near mistake

Curiosity about how that number held up year-by-year led to computing a
separate "best" stop-loss factor for each calendar year. One of those,
factor 0.85 from the combined period, briefly got saved as its own
versioned result (`test_v3`) before catching that this was the wrong
framing — 0.85 was the answer for the *whole* period, not something to
promote to a standalone recommendation. It got deleted, and the actual
useful question got asked instead: does the "best" factor look different
in different years? It does, dramatically — from 0.10 to 3.01 in
per-year Sharpe. But the most important finding wasn't the numbers
themselves, it was recognizing that one of those "optimal" per-year
values (2021's) wasn't actually a tuned stop-loss at all — it was the
loosest setting where the stop simply never triggered, because 2021 never
had a real drawdown to protect against. A parameter that looks optimal
can secretly mean "turn the feature off."

## Testing whether adaptation actually helps

That raised the real question: if a stop-loss's ideal tightness changes
year to year, should the strategy adapt — using last year's best setting
to trade this year? Two separate tests answered this, and both gave the
same answer: no. A simple walk-forward test (use last year's optimal
factor, no lookahead) lost to just keeping the fixed 0.85 constant. A
four-way comparison — no stop at all, the fixed constant, prior-year
adaptation, and an expanding training window — confirmed it again: the
fixed constant won outright, and the *expanding-window* approach, which
should in theory have more data to work with, was the single worst
performer of all four. The mechanism was traceable: one unusually calm
year (2021) skewed the combined optimization so hard that adding more
history didn't correct for it, it just inherited the distortion. Chasing
the most recent regime, or even a growing window of regimes, kept
reacting to conditions that had already changed by the time the model
adapted.

## Opening a second dimension

Every test so far had only tuned the stop-loss, leaving the strikes
themselves fixed at exactly 1 standard deviation from spot — a choice
that had never actually been tested against alternatives. A 2D sweep
varied both the strike distance and the stop-loss factor together, and
found something bigger than anything the 1D sweeps had turned up:
placing strikes much closer to spot (half a standard deviation instead
of one full one), paired with a looser stop, roughly doubled the best P&L
found anywhere in the project so far. But that result came with its own
honest caveat attached immediately — strikes that close to the money mean
much more real-world execution risk than this backtest's assumptions can
capture, so the win is provisional, not a settled upgrade.

## Pushing the edge, and finding where it actually ends

The natural next question was obvious: does going even tighter keep
helping? Extending the strike-distance sweep further down answered it
cleanly — no. Below the point already found, results didn't improve, they
collapsed into the exact same trap discovered earlier on the other axis:
near-100% stop-out rates, meaning the strategy stops being a real
strangle-with-protection and becomes "collect a sliver of premium, exit
almost immediately, every week," dressed up in impressive-looking raw
numbers. Recognizing that pattern the second time, on a completely
different parameter, was only possible because the first trap had already
been named and understood.

## Where this leaves things

Nothing here has been validated as a live-tradeable system — every result
still rests on synthetic Black-Scholes pricing, VIX as an implied-vol
stand-in, and no execution frictions. But the project has built up a real
discipline over the course of this: don't trust a naive optimum without
checking what's driving it, don't mistake "no stop" dressed up as a
tuned parameter for a real edge, and don't assume more adaptivity or more
history automatically means a better answer. Every one of those lessons
showed up as an actual, specific number in this project's history before
becoming a rule to apply going forward.
