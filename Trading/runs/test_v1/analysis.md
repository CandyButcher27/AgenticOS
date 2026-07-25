# test_v1 — SPY Weekly Short Strangle, 2020-2025

314 weekly trades. Full config: see `../../docs/superpowers/specs/2026-07-26-spy-strangle-backtest-design.md`.

## Headline numbers

| metric | value |
|---|---|
| total P&L | $4,521.70 |
| win rate | 80.3% |
| avg trade return | 0.028% of capital_proxy |
| Sharpe (annualized) | 0.23 |
| max drawdown | -$6,663.89 |
| worst trade | -$3,868.36 |
| tail loss (5th pct) | -$567.66 |
| return on capital | 0.032% |

## Per-year P&L

| year | trades | pnl | win rate | avg iv_proxy |
|---|---|---|---|---|
| 2020 | 53 | $1,676.99 | 86.8% | 0.291 |
| 2021 | 52 | $4,380.75 | 88.5% | 0.198 |
| 2022 | 52 | -$2,111.90 | 71.2% | 0.260 |
| 2023 | 52 | -$801.36 | 75.0% | 0.170 |
| 2024 | 53 | $1,671.54 | 79.2% | 0.158 |
| 2025 | 52 | -$294.33 | 80.8% | 0.191 |

2021 (low-vol grind-up) is the entire strategy's edge. 2022-2023 and 2025
are net losers despite win rates ≥71% — a handful of large tail losses
outweigh a long run of small wins.

## What's actually going on

**Payoff shape is short-vol, not directional edge.** Median trade pnl is
+$119, mean is +$14. The gap between those two numbers is the tell:
a few outsized losses drag the mean far below the typical outcome
(skew = -5.5). This strategy structurally collects small, frequent
premiums and is exposed to rare, large payouts when SPY's realized weekly
move exceeds the expected move implied by VIX.

**The single worst trade erases most of five years of gains.** Week of
2025-03-31 (SPY tariff-shock selloff): spot fell from $559.39 to $505.28,
blowing through the 546 put strike by $40.72. That one week: -$3,868,
and it single-handedly sets both `worst_trade_pnl` and (combined with the
following week's -$1,485) `max_drawdown`. Remove that one week and total
P&L would be roughly $8,390 instead of $4,522 — the entire 6-year result
is not much more than one bad week away from negative.

**IV proxy is a weak predictor of which weeks blow up.** Correlation
between `iv_proxy` and `pnl` across all 314 trades is -0.05 — essentially
zero. The COVID week (2020-03-23, iv_proxy 0.616) was a big loss under
high implied vol, as expected. But the worst trade of the whole backtest
(2025-03-31, iv_proxy 0.223) had *unremarkable* implied vol going in —
VIX simply didn't price the tariff-shock move. Sizing or filtering by
VIX level alone would not have avoided the biggest loss in this run.

**2022 is a cautionary case, not just "high vol is bad."** Average
iv_proxy in 2022 (0.260) was the second-highest of any year, yet 2022
was the second-worst year (-$2,112). Elevated *and rising* vol regimes
(rate-hike-driven grinding declines) hurt this strategy on both sides:
premiums collected didn't compensate for the sustained realized moves.

## Caveats (carried from the design spec)

`iv_proxy` = VIX/100, not SPY's own historical option IV. Premiums are
theoretical Black-Scholes prices, not real fills — no bid/ask, no
commissions, no slippage, no early assignment. `capital_proxy` is a sizing
approximation, not real margin. Real short-strangle P&L in 2020 and 2025
would likely be worse than shown here once slippage on a fast-moving
underlying is accounted for — theoretical BS prices don't capture the
wide bid/ask spreads that show up exactly during the weeks this strategy
loses money.

## Read

The strategy has positive expectancy over this sample, but nearly all of
it comes from one favorable year (2021) and it is one tail week away from
being a net loser over 6 years. Sharpe of 0.23 reflects that: high win
rate is not the same as good risk-adjusted return when the loss
distribution is this fat-tailed. Before trusting this further: test
whether a defined-risk version (buying further OTM wings) or a volatility
filter (skip weeks where realized vol has been rising, not just IV level)
changes the tail-loss profile.
