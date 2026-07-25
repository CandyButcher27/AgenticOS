# Four-way comparison: no stop / fixed k / prior-year k / expanding-window k

Test period: **2022-2025** (4 years). Not 2020-2021 — approach D needs at
least 2 prior years of in-sample data (per the spec: train on 2020-2021 to
trade 2022, 2020-2022 to trade 2023, etc.), which doesn't exist for 2020 or
2021 within this 6-year dataset.

- **A: no stop.** `strategy.disable_stop()` — L_stop/U_stop set to
  ±infinity, so the mid-week check never fires. Equivalent to `test_v1`.
- **B: fixed k=0.85.** The combined 2020-2025 sweep's practical optimum,
  held constant, never re-tuned. Same as the walk-forward test's "A".
- **C: prior-year k.** Year Y trades with whatever factor maximized P&L
  when swept on year Y-1 alone. Same as the walk-forward test's "B".
- **D: expanding-window k.** Year Y trades with whatever factor maximized
  P&L when swept on all of 2020..Y-1 combined. Training window grows by a
  year each time: 2020-2021 → trade 2022, 2020-2022 → trade 2023,
  2020-2023 → trade 2024, 2020-2024 → trade 2025.

Full numbers: `four_way_by_year.csv`, `four_way_combined.csv`. Chart:
`four_way_plot.png`.

## Combined 2022-2025

| approach | total P&L | Sharpe | max drawdown | win rate |
|---|---|---|---|---|
| A: no stop | -$1,536.04 | -0.24 | -$6,663.89 | 76.6% |
| **B: fixed k=0.85** | **$2,485.93** | **0.30** | -$3,525.77 | 63.2% |
| C: prior-year k | $78.37 | -0.15 | -$5,304.75 | 67.5% |
| D: expanding-window k | -$1,608.45 | -0.32 | -$5,758.14 | 64.6% |

**B wins outright.** Both adaptive approaches (C, D) landed close to
break-even-or-worse over this period, and D is the single worst performer
of all four — slightly worse than not having a stop at all.

## Year by year

| year | k_C (from) | pnl_C | k_D (window) | pnl_D | pnl_A | pnl_B |
|---|---|---|---|---|---|---|
| 2022 | 1.60 (2021) | -$1,554.06 | 1.65 (2020-21) | -$1,554.06 | -$2,111.90 | $326.25 |
| 2023 | 0.95 (2022) | -$112.08 | 0.90 (2020-22) | -$526.10 | -$801.36 | $750.38 |
| 2024 | 0.85 (2023) | $101.20 | 0.80 (2020-23) | -$83.98 | **$1,671.54** | $101.20 |
| 2025 | 1.35 (2024) | $1,643.31 | 0.80 (2020-24) | $555.68 | -$294.33 | $1,308.09 |

## Why D underperforms even C

D's failure isn't "not enough history" — more history should, in theory,
give a more stable estimate. What actually happens: **the combined-window
optimum is dominated by whichever single year in the window has the
largest P&L swing, not a balanced read across years.** 2021 alone wants
essentially no stop (0% stop rate at its own optimum, k=1.60 — see
`runs/sweep_stop_loss_by_year/analysis.md`) and its P&L curve has by far
the largest amplitude of any year (~$1,500 to ~$4,400 across factors).
Blend it with 2020 (which wants a real stop, own-year optimum k=0.90) and
the *combined* 2020-2021 optimum comes out at k=1.65 — even looser than
2021's own individual optimum. 2020's preference gets swamped.

The result: for the 2022 test, C and D land on nearly identical factors
(1.60 vs 1.65) and produce the **exact same P&L** (-$1,554.06) — both
loose enough that the stop never triggers that year, so the specific
value stopped mattering. Adding 2020 to the training window didn't
correct for 2021's outsized influence; it barely moved the answer.

## The recurring pattern

**2024 is the clearest single data point in this whole series of tests.**
No-stop (A) made $1,671.54 that year — dramatically better than every
stop variant (B/C/D all near flat or negative). 2024 was calm/choppy
without a real crash, so every version of the stop-loss mechanism just
got whipsawed out of otherwise-fine trades. No parameter-selection method
tested so far (fixed, prior-year, expanding-window) avoids this — it's a
property of *having a stop at all* in a regime like 2024's, not a
tuning problem.

Combined with the walk-forward result: **re-optimizing the stop-loss
factor — whether on the prior year alone or an expanding window — has not
beaten simply picking one constant from the full combined history and
leaving it alone**, across every test run so far.

## Caveats

Same synthetic-pricing caveats as every other run here. Four test years
is a small sample to rank four approaches confidently — this is a first
look, not a settled conclusion. The `C`/`D` factor-selection criterion
(P&L-argmax among practical-stop-rate factors) is unchanged from prior
runs and inherits the same small-sample fragility discussed in
`runs/sweep_stop_loss_by_year/analysis.md`.
