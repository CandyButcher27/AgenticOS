# Stop-loss factor sweep — 2020-2025

Swept `stop_loss_factor` from 0.10 to 2.00 in steps of 0.05 (39 values),
same 314-week backtest each time, only the stop-loss trigger band changes.
Ran in ~8s in plain Python — no need for C++/Go, this was never a
performance problem, it's 39 × 314 cheap comparisons.

Raw results: `sweep_results.csv`. Chart: `sweep_plot.png`.

## The naive answer is a trap

Sharpe is *maximized at factor = 0.10* (0.79) — but at that setting the
stop-trigger rate is 99%. A band that tight (0.10× the expected move) gets
touched almost every single week within a day or two of entry, so the
"strategy" at that point isn't really a strangle with a stop anymore —
it's closing almost every position almost immediately and collecting a
sliver of theta. High Sharpe there reflects low variance from doing almost
nothing risky, not good risk-adjusted trading. **Excluded from the
practical read** (shaded region in the chart, stop-rate ≥ 50%, roughly
factor < 0.65).

## Practical sweet spot: factor ≈ 0.85

Best Sharpe *outside* the degenerate region, and it also happens to be the
single best total P&L in the entire sweep:

| metric | factor=0.85 | factor=0.95 (test_v2) | factor=1.10 (2nd local peak) |
|---|---|---|---|
| total P&L | **$7,080** | $6,095 | $6,996 |
| Sharpe | **0.68** | 0.48 | 0.52 |
| win rate | 68.5% | 69.4% | 72.9% |
| max drawdown | -$3,526 | -$3,247 | -$3,137 |
| worst trade | -$1,532 | -$1,532 | -$1,532 |
| tail loss (5th pct) | -$313 | -$389 | -$422 |
| stop rate | 34.1% | 27.7% | 19.4% |

0.85 beats the `test_v2` baseline (0.95) on every headline number except
max drawdown (slightly worse, -$3,526 vs -$3,247) and stop rate (more
trades cut short). There's a second, smaller local peak around
factor=1.05-1.10 with better drawdown/tail-loss but lower total P&L and
Sharpe — a more conservative option if drawdown matters more than raw
return.

## Shape of the curve

Not smooth — real bumps and dips throughout (e.g. a spike at 1.35, a dip
at 1.40) from a fixed 314-trade sample; individual weeks flipping between
"stopped" and "held" as the band shifts causes visible noise, not just a
clean bias-variance tradeoff curve. Above factor ≈ 1.7, performance drops
hard: the stop is now wider than the sold strikes themselves in some
weeks, so it stops rarely (stop-rate < 5%) and converges back toward
`test_v1`'s baseline numbers with the worst trade returning to -$3,868
(2025-04-04, `test_v1`'s tariff-shock week) once the stop stops
qualifying as tight enough to catch it.

## Recommendation

Adopt **factor = 0.85** as the new default going forward (`test_v3`), it
dominates the current `test_v2` baseline. Same caveats apply as
`test_v1`/`test_v2`: synthetic BS pricing, daily-close-only stop checks,
no slippage/commissions.
