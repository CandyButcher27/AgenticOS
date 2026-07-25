# Stop-loss factor sweep, per calendar year

Same sweep as `runs/sweep_stop_loss/` (`stop_loss_factor` 0.10-2.00, step
0.05), run separately on each calendar year's ~52 trades instead of the
combined 2020-2025 sample. "Best" = highest total P&L among factors with
stop-trigger rate < 50% (same practical filter as the combined sweep).
User's stated goal here was maximizing profit per year, so P&L (not
Sharpe) is the selection criterion — Sharpe is reported alongside for
context.

Full per-year sweep tables: `sweep_<year>.csv`. Summary: `best_factor_by_year.csv`.
Chart: `best_factor_by_year.png`.

| year | trades | best factor | P&L at best | Sharpe at best | stop rate at best |
|---|---|---|---|---|---|
| 2020 | 53 | 0.90 | $2,139.05 | 0.95 | 18.9% |
| 2021 | 52 | 1.60 | $4,380.75 | 4.80 | **0.0%** |
| 2022 | 52 | 0.95 | $501.68 | 0.32 | 38.5% |
| 2023 | 52 | 0.85 | $750.38 | 0.89 | **46.2%** |
| 2024 | 53 | 1.35 | $1,378.88 | 0.88 | 9.4% |
| 2025 | 52 | 1.10 | $2,469.02 | 0.69 | 7.7% |

## Read this carefully before using these numbers

**This is 6 separate 52-trade optimizations, and it shows.** Fitting a
free parameter on ~52 data points and picking whichever value happened to
maximize that year's P&L is close to the textbook definition of
overfitting a backtest. Two results make that concrete:

- **2021's "best" factor (1.60) is really "turn the stop off."** Stop
  rate at that factor is 0% — no trade was ever stopped. Look at the
  2021 panel in the chart: P&L rises monotonically and then goes flat
  once the stop stops triggering at all. The optimizer isn't finding a
  smart stop-loss level for 2021, it's finding the loosest factor in the
  search range and stopping there because 2021 had no real drawdown
  events for a stop to protect against (matches `test_v1`'s finding:
  2021 was the strategy's best year and stop-loss only ever hurt it).
- **2023's "best" factor (0.85) sits right at the edge of the degenerate
  zone** (46.2% stop rate, just under the 50% cutoff). Small sample, high
  stop-rate pick — this is fragile, not a confident optimum.

**These per-year factors are not a recommendation to use a different
stop-loss each year.** A real trading system doesn't get to know in
advance which year it's in and pick accordingly — that's look-ahead bias.
What this sweep is actually useful for is diagnosing *why* the combined
2020-2025 sweep (`runs/sweep_stop_loss/`) landed where it did: the
combined optimum (0.85, from Sharpe/P&L agreement across the full period)
is a compromise across years that individually want very different
things — 2021 wants no stop at all, 2023 wants an aggressive one, 2024
wants something loose (1.35). The single-factor combined result is
necessarily a average-case answer, not the best case for any one year.

## Caveats

Same synthetic-pricing caveats as every other run here. Additionally:
52-trade single-year samples are noisy — a couple of weeks landing
differently could shift a year's "best factor" meaningfully. Treat this
table as a diagnostic of year-to-year regime dependence, not as tunable
parameters.
