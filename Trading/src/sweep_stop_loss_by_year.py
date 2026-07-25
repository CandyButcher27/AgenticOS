from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import data
import strategy
from sweep_stop_loss import FACTORS, DEGENERATE_STOP_RATE, run_sweep, START, END, ACCENT, PEAK, GRID

OUT_DIR = Path(__file__).parent.parent / "runs" / "sweep_stop_loss_by_year"
YEARS = range(2020, 2026)


def best_practical_factor(results):
    practical = results[results["stop_rate"] < DEGENERATE_STOP_RATE]
    if practical.empty:
        return None
    return practical.loc[practical["total_pnl"].idxmax()]


def plot(per_year_results, summary, out_path):
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True)
    fig.suptitle("Total P&L vs. stop-loss factor, by year")

    for ax, year in zip(axes.flat, YEARS):
        results = per_year_results[year]
        best = summary.loc[year]
        degenerate = results[results["stop_rate"] >= DEGENERATE_STOP_RATE]
        cutoff = degenerate["stop_loss_factor"].max() if len(degenerate) else None
        if cutoff is not None:
            ax.axvspan(FACTORS.min(), cutoff, color=GRID, alpha=0.6, zorder=0)
        ax.plot(results["stop_loss_factor"], results["total_pnl"], color=ACCENT, linewidth=1.8, zorder=2)
        if not pd.isna(best["best_factor"]):
            ax.axvline(best["best_factor"], color=PEAK, linewidth=1, linestyle="--", alpha=0.7)
            ax.scatter([best["best_factor"]], [best["best_pnl"]], color=PEAK, zorder=5, s=25)
        ax.set_title(f"{year}  (best={best['best_factor']})", loc="left", fontsize=10)
        ax.grid(color=GRID, linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.yaxis.set_major_formatter(lambda v, _: f"${v:,.0f}")

    for ax in axes[-1]:
        ax.set_xlabel("stop_loss_factor")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)


def main():
    raw = data.get_all(START, END)
    weeks_base = strategy.generate_weeks(raw["spy"], raw["vix"], raw["irx"])
    weeks_base["entry_date"] = pd.to_datetime(weeks_base["entry_date"])

    per_year_results = {}
    summary_rows = []
    for year in YEARS:
        yearly_weeks = weeks_base[weeks_base["entry_date"].dt.year == year]
        results = run_sweep(yearly_weeks, raw["spy"], raw["vix"], raw["irx"])
        per_year_results[year] = results

        best = best_practical_factor(results)
        summary_rows.append(
            {
                "year": year,
                "num_trades": len(yearly_weeks),
                "best_factor": best["stop_loss_factor"] if best is not None else float("nan"),
                "best_pnl": best["total_pnl"] if best is not None else float("nan"),
                "best_sharpe": best["sharpe_ratio"] if best is not None else float("nan"),
                "best_stop_rate": best["stop_rate"] if best is not None else float("nan"),
            }
        )

    summary = pd.DataFrame(summary_rows).set_index("year")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for year, results in per_year_results.items():
        results.to_csv(OUT_DIR / f"sweep_{year}.csv", index=False)
    summary.to_csv(OUT_DIR / "best_factor_by_year.csv")
    plot(per_year_results, summary, OUT_DIR / "best_factor_by_year.png")

    print(summary.to_string())


if __name__ == "__main__":
    main()
