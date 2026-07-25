import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import data
import strategy
import backtest
import metrics

START = "2020-01-01"
END = "2025-12-31"
FACTORS = np.round(np.arange(0.10, 2.0001, 0.05), 2)
OUT_DIR = Path(__file__).parent.parent / "runs" / "sweep_stop_loss"

ACCENT = "#2563eb"
PEAK = "#dc2626"
GRID = "#e5e7eb"


def run_sweep(weeks_base, spy, vix, irx):
    rows = []
    for factor in FACTORS:
        weeks = strategy.add_stop_bounds(weeks_base, stop_loss_factor=factor)
        trades = backtest.run(weeks, spy, vix, irx)
        m = metrics.compute(trades)
        stop_rate = (trades["exit_reason"] == "stop_loss").mean()
        rows.append({"stop_loss_factor": factor, "stop_rate": stop_rate, **m})
    return pd.DataFrame(rows)


DEGENERATE_STOP_RATE = 0.5  # above this, most trades exit almost immediately


def plot(results, out_path):
    degenerate = results[results["stop_rate"] >= DEGENERATE_STOP_RATE]
    degenerate_cutoff = degenerate["stop_loss_factor"].max() if len(degenerate) else None

    practical = results[results["stop_rate"] < DEGENERATE_STOP_RATE]
    best = practical.loc[practical["sharpe_ratio"].idxmax()]
    naive_best = results.loc[results["sharpe_ratio"].idxmax()]

    fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)
    fig.suptitle("Stop-loss factor sweep — SPY weekly strangle, 2020-2025")

    panels = [
        ("stop_rate", "Stop-trigger rate", "% of 314 trades exited early"),
        ("sharpe_ratio", "Sharpe ratio (annualized)", "Sharpe ratio"),
        ("total_pnl", "Total P&L ($)", "P&L, USD, all 314 trades"),
    ]
    for ax, (col, title, ylabel) in zip(axes, panels):
        if degenerate_cutoff is not None:
            ax.axvspan(FACTORS.min(), degenerate_cutoff, color=GRID, alpha=0.6, zorder=0)
        ax.plot(results["stop_loss_factor"], results[col], color=ACCENT, linewidth=2, zorder=2)
        ax.axvline(best["stop_loss_factor"], color=PEAK, linewidth=1, linestyle="--", alpha=0.6, zorder=1)
        ax.set_title(title, loc="left", fontsize=10)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.grid(color=GRID, linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    axes[2].yaxis.set_major_formatter(lambda v, _: f"${v:,.0f}")

    axes[0].annotate(
        f"stop-rate ≥ {DEGENERATE_STOP_RATE:.0%}:\nnear-immediate exit,\nnot a meaningful stop",
        xy=(FACTORS.min() + 0.03, 0.08),
        fontsize=8,
        color="#6b7280",
    )
    axes[1].scatter([best["stop_loss_factor"]], [best["sharpe_ratio"]], color=PEAK, zorder=5)
    axes[1].annotate(
        f"best practical Sharpe {best['sharpe_ratio']:.2f}\nat factor {best['stop_loss_factor']:.2f}"
        f"\n(naive global max {naive_best['sharpe_ratio']:.2f} at {naive_best['stop_loss_factor']:.2f}"
        f" is a {naive_best['stop_rate']:.0%} stop-rate degenerate case)",
        xy=(best["stop_loss_factor"], best["sharpe_ratio"]),
        xytext=(10, 10),
        textcoords="offset points",
        fontsize=8,
        color=PEAK,
    )
    axes[-1].set_xlabel("stop_loss_factor  (stop band width, as a multiple of the expected move)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    return best, naive_best


def main():
    raw = data.get_all(START, END)
    weeks_base = strategy.generate_weeks(raw["spy"], raw["vix"], raw["irx"])

    t0 = time.time()
    results = run_sweep(weeks_base, raw["spy"], raw["vix"], raw["irx"])
    elapsed = time.time() - t0
    print(f"swept {len(FACTORS)} factors in {elapsed:.1f}s")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_DIR / "sweep_results.csv", index=False)
    best, naive_best = plot(results, OUT_DIR / "sweep_plot.png")

    print(f"practical best sharpe {best['sharpe_ratio']:.3f} at factor {best['stop_loss_factor']:.2f}")
    print(
        f"naive global max sharpe {naive_best['sharpe_ratio']:.3f} at factor "
        f"{naive_best['stop_loss_factor']:.2f} (stop_rate {naive_best['stop_rate']:.0%}, degenerate)"
    )


if __name__ == "__main__":
    main()
