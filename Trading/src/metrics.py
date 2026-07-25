import numpy as np


def compute(trades_df):
    pnl = trades_df["pnl"]
    ret = trades_df["return_pct"]
    equity = pnl.cumsum()
    running_max = equity.cummax()
    drawdown = equity - running_max

    ret_std = ret.std()
    sharpe = (ret.mean() / ret_std * np.sqrt(52)) if ret_std else float("nan")

    return {
        "total_pnl": pnl.sum(),
        "avg_trade_return_pct": ret.mean(),
        "win_rate": (pnl > 0).mean(),
        "max_drawdown": drawdown.min(),
        "sharpe_ratio": sharpe,
        "worst_trade_pnl": pnl.min(),
        "tail_loss_5pct": pnl.quantile(0.05),
        "return_on_capital": pnl.sum() / trades_df["capital_proxy"].sum(),
        "num_trades": len(trades_df),
    }
