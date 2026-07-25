# test_v3 — SPY Weekly Short Strangle + Stop-Loss (factor=0.85), 2020-2025

Same mechanics as `test_v1`/`test_v2` (see `test_v1/analysis.md` for the
full walkthrough), stop-loss factor changed from `test_v2`'s 0.95 to
**0.85** — the practical Sharpe/P&L sweet spot identified in
`runs/sweep_stop_loss/` (0.10-2.00 sweep, 0.05 steps; the naive global-max
factor of 0.10 was excluded as a 99%-stop-rate degenerate case).

## vs. test_v2

| metric | test_v2 (0.95) | test_v3 (0.85) |
|---|---|---|
| total P&L | $6,094.96 | $7,080.09 |
| Sharpe (annualized, full period) | 0.48 | 0.68 |
| win rate | 69.4% | 68.5% |
| max drawdown | -$3,247.35 | -$3,525.77 |
| worst trade | -$1,531.65 | -$1,531.65 |
| stop rate | 27.7% | 34.1% |

## Per-year Sharpe ratio breakdown

Full data: `yearly_sharpe.csv`. Each year computed independently — same
`metrics.compute()` on that year's ~52 trades, Sharpe annualized ×√52.

| year | trades | total P&L | win rate | **Sharpe** | max drawdown | worst trade |
|---|---|---|---|---|---|---|
| 2020 | 53 | $1,849.99 | 77.4% | 0.81 | -$1,650.17 | -$1,206.51 |
| 2021 | 52 | $2,744.16 | 80.8% | **3.01** | -$412.06 | -$412.06 |
| 2022 | 52 | $326.25 | 59.6% | 0.21 | -$1,121.36 | -$672.59 |
| 2023 | 52 | $750.38 | 63.5% | 0.89 | -$369.08 | -$369.08 |
| 2024 | 53 | $101.20 | 54.7% | **0.10** | -$1,399.81 | -$1,052.32 |
| 2025 | 52 | $1,308.09 | 75.0% | 0.26 | -$3,233.16 | -$1,531.65 |

The blended full-period Sharpe (0.68) is an average over years that swing
from 0.10 to 3.01 — a 30x range. Reading it as one stable number hides
that this strategy's risk-adjusted performance is heavily regime-dependent:

- **2021** (Sharpe 3.01): calm grind-up market, tiny drawdown, low
  week-to-week variance in returns. Best year by a wide margin.
- **2024** (Sharpe 0.10): choppy/range-bound conditions kept whipsawing
  the stop-loss (35.8% stop rate that year per `test_v2`'s analysis),
  total P&L barely above zero.
- **2025** (Sharpe 0.26 despite $1,308 total P&L): the tariff-shock
  drawdown (-$3,233) dominates the volatility term even though the year
  closed positive — a reminder that Sharpe penalizes the path, not just
  the endpoint.

## Caveats

Same as `test_v1`/`test_v2`: synthetic Black-Scholes pricing (both entry
premiums and stop-loss buybacks), `iv_proxy` = VIX/100 not real historical
option IV, daily-close-only stop checks, no slippage/commissions.
Per-year Sharpe numbers are each computed on a small sample (~52 trades) —
noisy by construction, not something to over-read year to year.
