# 2D sweep: strike SD multiplier x stop-loss factor

Two parameters now vary together, both on the combined 2020-2025 period:

- **`sd_multiplier`**: how far the sold strikes sit from spot, as a
  multiple of the 1-SD expected move. Every prior run in this project used
  `sd_multiplier=1.0` implicitly (strikes at `spot ± 1×EM`) — that number
  was never actually tested against alternatives until now. Swept 0.5 to
  2.0, step 0.2 (8 values: 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 1.9 — note
  1.0 itself isn't a grid point at this step size).
- **`stop_loss_factor`**: unchanged meaning, but now measured as a
  fraction of the *actual* strike distance (`strike_distance =
  expected_move × sd_multiplier`) rather than the raw 1-SD move, so it
  stays comparable across different `sd_multiplier` values. Swept 0.5 to
  2.0, step 0.1 (16 values).

128 combinations, ~26s to run. Full grid: `grid_results.csv`. Heatmap:
`grid_heatmap.png` (P&L and Sharpe side by side; `x` marks degenerate
cells, stop-rate ≥ 50%; `★` marks the best practical cell in each panel).

## Headline result

**Tighter strikes dominate almost the entire grid.** The bottom row
(`sd_multiplier=0.5`, strikes only half an expected-move from spot) beats
every other row on both P&L and Sharpe, for nearly every stop-loss factor
tested. Best practical cell:

| | sd_multiplier | stop_loss_factor | total P&L | Sharpe | win rate | max drawdown | worst trade | stop rate |
|---|---|---|---|---|---|---|---|---|
| **best P&L** | 0.5 | 1.7 | **$13,690.33** | 0.81 | 58.3% | -$5,139.28 | -$2,232.79 | 34.1% |
| best Sharpe | 0.5 | 1.5 | $12,786.55 | **0.88** | — | — | — | 43.3% |

For comparison, the closest points to the old default (`sd≈1.0`, no exact
grid point at this step size):

| sd_multiplier | stop_loss_factor | total P&L | Sharpe | win rate |
|---|---|---|---|---|
| 0.9 | 0.9 | $8,502.32 | 0.79 | 66.6% |
| 1.1 | 0.9 | $4,895.17 | 0.40 | 72.3% |

The best `sd=0.5` cell roughly **doubles** the P&L of anything found in
every prior 1D stop-loss-only sweep (`runs/sweep_stop_loss/`'s best was
$7,080 at sd=1.0, stop=0.85).

## Why this makes sense, and why it's not free

Selling strikes closer to spot (`sd_multiplier=0.5`) collects far more
option premium up front — the strikes are much closer to the money, so
Black-Scholes prices them higher. That's the entire source of the extra
P&L. The tradeoff is that closer strikes are touched far more easily, so
the stop-loss mechanism has to work much harder and much more often: at
`sd=0.5`, stop-rate is 24-93% across the whole stop-factor range (vs.
17-100% at `sd=1.0` in the original 1D sweep) — this row leans on the
stop far more heavily than the strategy has anywhere else in this
project. Win rate at the best cell (58.3%) is also meaningfully lower
than the `sd=1.0` configs explored earlier (typically 65-73%).

**This is a real caveat, not just a note.** `sd_multiplier=0.5` means
selling much closer to at-the-money than anything tested before it in
this project. The backtest's mechanics — synthetic Black-Scholes pricing,
daily-close-only stop checks, no slippage — are already an approximation,
and they get less trustworthy the closer to the money you sell: real
bid/ask spreads widen faster near the money, real gap risk (a stop that
should trigger mid-day but doesn't get checked until close) matters more
when strikes are this close, and assignment/pin risk near expiry is more
realistic a concern than it is for strikes further out. The backtest says
this cell wins; whether it would survive real execution frictions is a
materially open question this backtest cannot answer.

## Reading the heatmap

- The Sharpe panel shows a visible "bad zone" in the upper-middle
  (`sd≈1.1-1.9`, `stop≈0.9-1.4`) — negative Sharpe (orange/red), worse
  than `sd=1.0`'s own single-axis sweep ever showed. Wider strikes with a
  moderately tight stop is the worst combination here: not enough premium
  collected, and the stop still cuts into what would've been fine trades.
- Both panels roughly agree on rewarding the bottom rows and penalizing
  the top-middle — the two metrics aren't fighting each other here the
  way the 1D stop sweep's naive-vs-practical split required untangling.
- Degenerate cells (`x`, stop-rate ≥ 50%) cluster in the bottom-left —
  tight strikes *and* a tight stop compound: a small strike distance
  means even a "loose-sounding" stop factor still corresponds to a small
  absolute dollar band.

## Caveats

Same synthetic-pricing/no-slippage caveats as every other run here, with
the added note above about `sd_multiplier=0.5` specifically. This is a
single combined-period grid — no walk-forward or per-year validation has
been run on the `sd_multiplier` axis yet, so treat this as a first look
at a second free parameter, not a validated recommendation to trade
sd=0.5 strikes.
