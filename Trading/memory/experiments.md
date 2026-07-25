# Experiments log

Chronological. Each entry: what changed, headline result, where the full
detail lives. See `architecture.md` for the mechanics referenced here.

## test_v1 — baseline, no stop-loss

`runs/test_v1/`. Plain weekly short strangle, 2020-2025, held to expiry
every week, no risk management. 314 trades, win rate 80.3%, total P&L
$4,521.70, Sharpe 0.23, max drawdown -$6,663.89, worst trade -$3,868.36
(2025-04-04, tariff-shock week). Finding: nearly all the P&L comes from
one good year (2021); the strategy is one bad week away from a net loss
over 6 years. Fat left tail (skew -5.5) — frequent small wins, rare large
losses.

## test_v2 — add stop-loss, factor=0.95

`runs/test_v2/`. Stop triggers at 0.95× expected move, buys back both
legs via Black-Scholes mark instead of holding to expiry. Total P&L
$6,094.96 (+35%), Sharpe 0.48 (~2x), max drawdown and worst trade both cut
~60%. Not a uniform win: helps 2022/2023/2025 (real drawdown years),
hurts 2020/2021/2024 (calm/choppy years where the stop cuts otherwise-fine
trades short).

## sweep_stop_loss — 1D sweep, stop_loss_factor 0.10-2.00

`runs/sweep_stop_loss/`. Naive Sharpe-maximizing factor (0.10) is a trap:
99% stop rate, means exiting almost every trade immediately — not really
running the strategy. Excluding that degenerate region (stop-rate ≥ 50%),
practical sweet spot is **factor=0.85**: $7,080.09 P&L, Sharpe 0.68 — beats
`test_v2`'s 0.95 on every headline number except drawdown.

## sweep_stop_loss_by_year — same sweep, per calendar year

`runs/sweep_stop_loss_by_year/`. Each year's own P&L-maximizing factor is
wildly different: 2020=0.90, 2021=1.60, 2022=0.95, 2023=0.85, 2024=1.35,
2025=1.10. **2021's "best" factor has a 0% stop rate — it's really "turn
the stop off,"** not a tuned value; 2021 had no drawdown for a stop to
protect against. Flagged explicitly: fitting a free parameter to ~52
trades per year is close to textbook overfitting, and these per-year
values are diagnostic, not usable trading parameters (using them would
require knowing the year in advance — lookahead bias).

## walk_forward — fixed k vs. prior-year k

`runs/walk_forward/`. Tests whether a "walk-forward" heuristic (trade
year Y using year Y-1's own best factor, no lookahead) beats the static
0.85 constant from `sweep_stop_loss`. **Fixed k wins decisively**:
$5,230.09 P&L / Sharpe 0.67 vs. prior-year k's $2,984.93 / 0.21, over
2021-2025. Root cause: 2022 inherits 2021's "no stop" factor
(1.60) right as a real bear market starts — the walk-forward approach
reacts to last year's regime one year too late.

## four_way_comparison — no-stop / fixed / prior-year / expanding-window

`runs/four_way_comparison/`. Adds a 4th approach: expanding-window k
(train on all years up to Y-1, re-optimize each year). Test period
2022-2025 (expanding window needs ≥2 prior years, unavailable for
2020/2021). **Fixed k=0.85 wins again** ($2,485.93 P&L, Sharpe 0.30).
Expanding-window is the *worst* of all four (-$1,608.45) — worse than no
stop at all. Cause: the combined-window optimum gets dominated by
whichever single year has the largest P&L swing (2021), not a balanced
read across years; adding more history didn't fix this. 2024 stands out
across every approach: no-stop makes $1,671.54 that year while every stop
variant is flat/negative — 2024's chop just whipsaws any version of the
stop mechanism.

## sweep_2d — strike distance (sd_multiplier) × stop_loss_factor

`runs/sweep_2d/`. First test of a second free parameter: how far strikes
sit from spot (previously hardcoded to exactly 1× expected move). Grid:
`sd_multiplier` 0.1-2.0 (step 0.2) × `stop_loss_factor` 0.5-2.0 (step
0.1), combined 2020-2025 period. **Best practical cell: sd=0.5,
stop=1.7 → $13,690.33 P&L, Sharpe 0.81** — roughly double the best 1D
result. Caveat: `sd=0.5` means selling much closer to the money than
anything tested before (win rate drops to 58%, stop-rate 24-93%) — real
execution risk (slippage, gaps, assignment) is understated here more than
elsewhere. Extended the sweep down to `sd_multiplier=0.1` to check for
further improvement: **it doesn't improve, it collapses into the same
degenerate trap** found on the stop-factor axis originally — below 0.5,
every cell has stop-rate 90-99% (near-immediate exit regardless of stop
factor), so 0.5 is a genuine edge of the meaningful region, not an
arbitrary cutoff.

## Recurring theme across every validation test

Re-optimizing any free parameter (stop-loss factor, whether by prior-year
or expanding-window) has not yet beaten simply picking one constant from
the full combined history and leaving it alone. Every adaptive approach
tested underperformed the static baseline. This has held up across two
separate validation designs (walk-forward, 4-way comparison) — worth
treating as a real finding, not a fluke, though still only tested on ~5
years of weekly data.
