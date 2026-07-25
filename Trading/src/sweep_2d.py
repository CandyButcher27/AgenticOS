import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

import data
import strategy
import backtest
import metrics
from sweep_stop_loss import START, END

OUT_DIR = Path(__file__).parent.parent / "runs" / "sweep_2d"

SD_MULTIPLIERS = np.round(np.arange(0.5, 2.0001, 0.2), 2)
STOP_FACTORS = np.round(np.arange(0.5, 2.0001, 0.1), 2)
DEGENERATE_STOP_RATE = 0.5


def run_grid(spy, vix, irx):
    rows = []
    for sd in SD_MULTIPLIERS:
        weeks_base = strategy.generate_weeks(spy, vix, irx, sd_multiplier=sd)
        for stop in STOP_FACTORS:
            weeks = strategy.add_stop_bounds(weeks_base, stop_loss_factor=stop)
            trades = backtest.run(weeks, spy, vix, irx)
            m = metrics.compute(trades)
            stop_rate = (trades["exit_reason"] == "stop_loss").mean()
            rows.append({"sd_multiplier": sd, "stop_loss_factor": stop, "stop_rate": stop_rate, **m})
    return pd.DataFrame(rows)


def heatmap(ax, results, value_col, title, cmap="RdBu"):
    pivot = results.pivot(index="sd_multiplier", columns="stop_loss_factor", values=value_col)
    stop_rate_pivot = results.pivot(index="sd_multiplier", columns="stop_loss_factor", values="stop_rate")

    vmax = pivot.abs().max().max()
    norm = TwoSlopeNorm(vcenter=0, vmin=-vmax, vmax=vmax)
    im = ax.imshow(pivot.values, cmap=cmap, norm=norm, aspect="auto", origin="lower")

    degenerate = stop_rate_pivot.values >= DEGENERATE_STOP_RATE
    ys, xs = np.where(degenerate)
    ax.scatter(xs, ys, marker="x", color="black", s=15, alpha=0.4, linewidths=0.8)

    practical = pivot.values.copy()
    practical[degenerate] = np.nan
    if np.isfinite(practical).any():
        flat_idx = np.nanargmax(practical)
        best_y, best_x = np.unravel_index(flat_idx, practical.shape)
        ax.scatter([best_x], [best_y], marker="*", color="black", s=180, zorder=5, edgecolors="white", linewidths=0.8)

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"{c:.1f}" for c in pivot.columns], rotation=90, fontsize=7)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([f"{r:.1f}" for r in pivot.index], fontsize=8)
    ax.set_xlabel("stop_loss_factor")
    ax.set_ylabel("sd_multiplier (strike distance, x expected move)")
    ax.set_title(title, loc="left", fontsize=10)
    return im, pivot


def plot(results, out_path):
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle(
        "2D sweep: strike SD multiplier x stop-loss factor  "
        "(x = stop-rate >= 50%, degenerate;  * = best practical cell)"
    )

    im0, pivot_pnl = heatmap(axes[0], results, "total_pnl", "Total P&L ($)")
    cb0 = fig.colorbar(im0, ax=axes[0])
    cb0.ax.set_ylabel("Total P&L ($)", fontsize=9)

    im1, pivot_sharpe = heatmap(axes[1], results, "sharpe_ratio", "Sharpe ratio (annualized)")
    cb1 = fig.colorbar(im1, ax=axes[1])
    cb1.ax.set_ylabel("Sharpe ratio", fontsize=9)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)


def main():
    raw = data.get_all(START, END)

    t0 = time.time()
    results = run_grid(raw["spy"], raw["vix"], raw["irx"])
    elapsed = time.time() - t0
    print(f"swept {len(SD_MULTIPLIERS)}x{len(STOP_FACTORS)}={len(results)} cells in {elapsed:.1f}s")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_DIR / "grid_results.csv", index=False)
    plot(results, OUT_DIR / "grid_heatmap.png")

    practical = results[results["stop_rate"] < DEGENERATE_STOP_RATE]
    best_pnl = practical.loc[practical["total_pnl"].idxmax()]
    best_sharpe = practical.loc[practical["sharpe_ratio"].idxmax()]
    print(f"best practical P&L: sd={best_pnl['sd_multiplier']:.1f} stop={best_pnl['stop_loss_factor']:.1f} "
          f"-> ${best_pnl['total_pnl']:,.2f}, sharpe={best_pnl['sharpe_ratio']:.2f}")
    print(f"best practical Sharpe: sd={best_sharpe['sd_multiplier']:.1f} stop={best_sharpe['stop_loss_factor']:.1f} "
          f"-> sharpe={best_sharpe['sharpe_ratio']:.2f}, pnl=${best_sharpe['total_pnl']:,.2f}")


if __name__ == "__main__":
    main()
