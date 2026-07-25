# test_v2 — SPY Weekly Short Strangle + Stop-Loss, 2020-2025

Change from `test_v1`: add a stop-loss. `stop_move = 0.95 × expected_move`,
`L_stop = ceil(spot_entry - stop_move)`, `U_stop = floor(spot_entry + stop_move)`
(rounded toward spot, so the trigger band sits just inside the sold
strikes). Checked once per trading day, mid-week, using daily close (no
intraday data). On breach: buy back both legs same-day via Black-Scholes,
using that day's spot/VIX/rate and remaining time-to-expiry — exits early
instead of holding to Friday. Mechanics/assumptions otherwise unchanged
from `test_v1` (see that file for the full walkthrough).

## vs. baseline (test_v1)

| metric | test_v1 | test_v2 | change |
|---|---|---|---|
| total P&L | $4,521.70 | $6,094.96 | +$1,573.26 (+35%) |
| win rate | 80.3% | 69.4% | -10.9pp |
| Sharpe (annualized) | 0.23 | 0.48 | ~2x |
| max drawdown | -$6,663.89 | -$3,247.35 | -51% |
| worst trade | -$3,868.36 | -$1,531.65 | -60% |
| tail loss (5th pct) | -$567.66 | -$388.60 | -32% |
| return on capital | 0.032% | 0.043% | +34% |

314 trades either way: 227 held to expiry unchanged, 87 (27.7%) stopped
out early.

## Why it works despite a lower win rate

Splitting the 87 stopped trades by counterfactual outcome (what each would
have made holding to expiry instead):

- **51 trades: stopping cost money.** Avg -$282 each (-$14,377 total) —
  these would have recovered by Friday, or lost less than the stop
  realized. This is the win-rate hit: locking in a small loss on a trade
  that was "just" a scare, not a real blowout.
- **36 trades: stopping saved money.** Avg +$443 each (+$15,950 total) —
  these were on their way to a real tail loss, and exiting early caught
  much less of the damage than holding to expiry would have.

Net: +$1,573, exactly the total-P&L gap above. The stop is *individually*
wrong more often than right (51 vs 36), but the wins are large and the
losses small — same asymmetry that made the original strangle's tail risk
dangerous now works in the strategy's favor instead of against it.

## Per-year

| year | v1 pnl | v2 pnl | stop rate | v2 better? |
|---|---|---|---|---|
| 2020 | $1,676.99 | $1,429.95 | 17.0% | no (-$247) |
| 2021 | $4,380.75 | $2,690.32 | 21.2% | no (-$1,690) |
| 2022 | -$2,111.90 | $501.68 | 38.5% | **yes (+$2,614)** |
| 2023 | -$801.36 | -$112.08 | 36.5% | **yes (+$689)** |
| 2024 | $1,671.54 | -$353.70 | 35.8% | no (-$2,025) |
| 2025 | -$294.33 | $1,938.79 | 17.3% | **yes (+$2,233)** |

Not a uniform win. In trending/calm years (2021, 2024) the stop mostly
cuts winners short — 2021 was v1's best year and got worse here. In years
with sharp adverse moves (2022's grind-down, 2025's tariff shock) the stop
earns its keep. **2024 stands out**: highest stop rate of any calmer year
(35.8%) with a net cost of -$2,025 — worth investigating in a future run
whether the 0.95× band is simply too tight for 2024's chop, or whether a
volatility-regime filter should gate when the stop applies at all.

## New worst trade

2025-04-07 week (-$1,531.65, stopped 2 days in) replaces test_v1's
2025-03-31 week (-$3,868.36) as the worst trade — but note the *same*
tariff-shock period produced both: v1's single -$3,868 week is now two
smaller v2 losses (that week stopped at -$780, then the following week
also stopped at -$1,532). The stop reduced the damage per week but didn't
eliminate the underlying event — a sustained multi-week adverse move still
produces sequential losses.

## Open questions for test_v3

- Is 0.95× the right factor, or does a wider/narrower band trade off
  differently (fewer false stops vs. slower to cut real losses)?
- Would a volatility or trend filter (skip the stop, or skip the trade
  entirely, in certain regimes) fix the 2024 problem without giving back
  the 2022/2025 gains?
- Same caveats as `test_v1` apply: synthetic BS pricing/marks, no
  slippage or commissions on the buyback either.
