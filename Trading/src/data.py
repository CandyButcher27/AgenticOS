from pathlib import Path

import pandas as pd
import yfinance as yf

DATA_DIR = Path(__file__).parent.parent / "data"

TICKERS = {
    "spy": "SPY",
    "vix": "^VIX",
    "irx": "^IRX",
}


def _cache_path(name, start, end):
    return DATA_DIR / f"{name}_{start}_{end}.parquet"


def get_daily(name, start, end):
    DATA_DIR.mkdir(exist_ok=True)
    path = _cache_path(name, start, end)
    if path.exists():
        return pd.read_parquet(path)

    symbol = TICKERS[name]
    df = yf.download(symbol, start=start, end=end, auto_adjust=False, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Close"]].rename(columns={"Close": "close"})
    df.index.name = "date"
    df.to_parquet(path)
    return df


def get_all(start, end):
    return {name: get_daily(name, start, end) for name in TICKERS}
