# Trading

Backtest engine for a SPY weekly short strangle strategy, 2020-2025.

## Strategy

Every week: read Monday's (first trading day's) close, VIX, and 13-week
T-bill rate. Compute an expected move via `EM = spot * IV * sqrt(days/365)`,
sell a put below `spot - EM` and a call above `spot + EM`, hold to Friday
(last trading day's) expiry. See
`docs/superpowers/specs/2026-07-26-spy-strangle-backtest-design.md` for the
full design, including the assumptions this makes (VIX as an IV proxy,
Black-Scholes for theoretical premiums, no historical options data).

## Setup

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

## Run

```
.venv\Scripts\python src\main.py
```

Prints summary metrics, writes the full trade log to `results/trades.csv`.
Price/VIX/rate data is cached to `data/*.parquet` after the first pull.

## Test

```
.venv\Scripts\python -m pytest tests/ -v
```

## Layout

```
src/           pipeline modules (data, blackscholes, strategy, backtest, metrics, main)
tests/         pytest suite
data/          cached yfinance pulls (gitignored)
results/       backtest output (gitignored)
docs/          design specs
```
