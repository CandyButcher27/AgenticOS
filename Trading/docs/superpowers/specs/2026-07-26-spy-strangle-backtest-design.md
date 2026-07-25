# SPY Weekly Short Strangle Backtest — Design

## Purpose

Backtest a weekly short strangle strategy on SPY, 2020-01-01 to 2025-12-31, using
`yfinance` for underlying price data and a volatility-index proxy for implied
volatility (since `yfinance` does not provide historical options chains).

## Strategy

Each week:
1. Entry day = first trading day of the week (normally Monday; shifts to Tuesday
   if Monday is a market holiday). Record `spot_entry` = that day's close.
2. Expiry day = last trading day of the same week (normally Friday; shifts to
   Thursday if Friday is a market holiday). Record `spot_expiry` = that day's close.
3. `days_to_expiry` = calendar days between entry day and expiry day.
4. `iv_proxy` = that entry day's `^VIX` close / 100. **This is a volatility-index
   proxy, not the underlying's actual historical option-implied volatility** —
   named `iv_proxy` throughout code and treated as an approximation.
5. `rate` = that entry day's `^IRX` close / 100 (13-week T-bill, used as
   risk-free rate `r` in Black-Scholes).
6. `T` = `days_to_expiry / 365`.
7. `expected_move` = `spot_entry * iv_proxy * sqrt(T)`.
8. `L = spot_entry - expected_move`, `U = spot_entry + expected_move`.
9. `strike_put` = `L` rounded down to nearest `strike_increment` (default `1`,
   configurable — not hardcoded).
   `strike_call` = `U` rounded up to nearest `strike_increment`.
10. `premium_put`, `premium_call` = Black-Scholes put/call price using
    `S=spot_entry, K=strike_put/strike_call, T, r=rate, sigma=iv_proxy`.
    **These are theoretical/synthetic premiums from Black-Scholes, not market-quoted
    option prices** — there is no historical options chain to source real fills from.
11. Position: sell 1 put contract (100 shares) + 1 call contract (100 shares).
    Held to expiry, no early close, no stop-loss, no mid-week mark-to-market.
12. `payout` at expiry = `max(0, strike_put - spot_expiry) * 100 + max(0, spot_expiry - strike_call) * 100`
    (intrinsic value owed on whichever leg finished ITM).
13. `pnl` = `(premium_put + premium_call) * 100 - payout`.
14. `capital_proxy` = `strike_put * 100`. **This is a capital-at-risk approximation
    (cash-secured-put-style sizing), not a real margin/buying-power calculation.**
15. `return_pct` = `pnl / capital_proxy`.

Weeks where SPY, VIX, or IRX data is missing for the entry or expiry day (e.g. a
holiday-shortened week with no trading days, or a data gap) are skipped and logged.

## Data

- `SPY` daily OHLC, `^VIX` daily close, `^IRX` daily close, via `yfinance`,
  2020-01-01 to 2025-12-31.
- Cached to `data/*.parquet` on first pull; subsequent runs reuse the cache
  unless the date range changes.

## Modules

- `data.py` — yfinance pull + parquet cache for SPY/^VIX/^IRX.
- `blackscholes.py` — European put/call pricing (`scipy.stats.norm` for CDF).
- `strategy.py` — per-week signal generation (steps 1-14 above), takes
  `strike_increment` as a parameter.
- `backtest.py` — loop over all weeks in range, build trade log DataFrame.
- `metrics.py` — from the trade log + equity curve, compute:
  total P&L, average trade return, win rate, max drawdown, Sharpe ratio
  (weekly returns annualized ×√52), worst trade, tail loss (5th percentile
  return), return on capital.
- `main.py` — orchestrates pull → backtest → metrics → prints summary,
  saves `results/trades.csv`.

## Trade log columns

`entry_date, expiry_date, spot_entry, spot_expiry, iv_proxy, rate,
days_to_expiry, expected_move, L, U, strike_put, strike_call,
premium_put, premium_call, premium_total, payout, pnl, capital_proxy,
return_pct`

## Out of scope

Commissions/slippage, early close/stop-loss rules, multiple contracts,
non-SPY tickers, live trading, real historical options chain data.

## Testing

`test_backtest.py`:
- Black-Scholes price vs. a known textbook value.
- Strike rounding on a synthetic spot/IV pair, including a non-default
  `strike_increment`.
- Payoff math on a synthetic ITM/OTM week (both legs, one leg, neither leg).

## Environment

`.venv` (Python 3.11+), `requirements.txt`: `yfinance, pandas, numpy, scipy`.
