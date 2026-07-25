# Walk-forward: fixed k=0.85 vs. prior-year-optimal k

Two approaches, tested out-of-sample on 2021-2025 (2020 excluded — no
prior year exists in this dataset to derive a "previous k" from):

- **A: k = 0.85 fixed.** The combined 2020-2025 sweep's practical
  Sharpe/P&L optimum (`runs/sweep_stop_loss/`), held constant, never
  re-tuned.
- **B: k = previous year's own optimal factor.** For year Y, k is
  whatever factor maximized P&L when swept on year Y-1 alone (from
  `runs/sweep_stop_loss_by_year/best_factor_by_year.csv`). Trained only
  on the past, applied to the future — no lookahead, unlike the per-year
  sweep itself (which picked each year's factor using that same year's
  results).

Full numbers: `walk_forward_by_year.csv`, `walk_forward_combined.csv`.
Chart: `walk_forward_plot.png`.

## Year by year

| year | k_A | P&L A | Sharpe A | k_B (from prior year) | P&L B | Sharpe B |
|---|---|---|---|---|---|---|
| 2021 | 0.85 | $2,744.16 | 3.01 | 0.90 (from 2020) | $2,906.56 | 2.92 |
| 2022 | 0.85 | $326.25 | 0.21 | 1.60 (from 2021) | **-$1,554.06** | **-0.65** |
| 2023 | 0.85 | $750.38 | 0.89 | 0.95 (from 2022) | -$112.08 | -0.09 |
| 2024 | 0.85 | $101.20 | 0.10 | 0.85 (from 2023) | $101.20 | 0.10 |
| 2025 | 0.85 | $1,308.09 | 0.26 | 1.35 (from 2024) | $1,643.31 | 0.27 |

**Combined 2021-2025: A wins decisively.**

| approach | total P&L | Sharpe |
|---|---|---|
| A (k=0.85 fixed) | **$5,230.09** | **0.67** |
| B (prior-year k) | $2,984.93 | 0.21 |

## Why B loses: it's chasing last year's regime, one year late

B wins 2 of 5 years (2021, 2025) and loses 3, but the losses are much
larger than the wins. The clearest case is **2022**: B enters the year
using k=1.60, which is 2021's optimum — and 2021's optimum was
essentially "turn the stop off" (0% stop rate that year, see
`runs/sweep_stop_loss_by_year/analysis.md`), because 2021 had no real
drawdown for a stop to protect against. Carrying that loose setting into
2022 — a genuine grinding bear market, exactly the kind of year a
stop-loss is supposed to help with (`test_v2`'s finding) — meant B
entered 2022 with effectively no protection. Result: -$1,554 in a year A
made +$326, a $1,880 swing from one parameter choice.

2023 repeats the pattern at smaller scale: B inherits 2022's factor
(0.95, chosen for a rough year) and it's slightly worse than A that year.
2024 ties exactly by coincidence (2023's optimal factor happened to equal
0.85). 2025 is B's one clear win — 2024's optimal factor (1.35) happened
to also suit 2025.

The pattern: **a single year's "optimal" parameter reflects that year's
specific regime, and market regimes don't persist reliably enough for
"last year's answer" to be a good guess at next year's regime.** A static
parameter chosen from a longer combined window is more robust than
chasing the most recent year's fit — the opposite of what "walk-forward
optimization" is usually assumed to buy you, but consistent with this
being a small-sample (52 trades/year), single-factor optimization rather
than a real multi-factor walk-forward system with proper train/test
windows.

## Caveats

Same synthetic-pricing caveats as every other run here, plus: this is a
minimal/naive walk-forward (1-year lookback, re-optimize annually, single
free parameter) — not a rigorous walk-forward framework (no rolling
multi-year training window, no out-of-sample buffer, no parameter
stability check). Five test years is also a very small sample to declare
"A beats B" with confidence; treat this as a first look, not a settled
result.
