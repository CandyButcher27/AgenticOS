from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import data
import strategy
import backtest
import metrics
from sweep_stop_loss import START, END, ACCENT, PEAK, GRID
from sweep_stop_loss_by_year import YEARS, run_sweep, best_practical_factor

OUT_DIR = Path(__file__).parent.parent / "runs" / "walk_forward"
K_A = 0.85
TEST_YEARS = range(2021, 2026)  # 2020 has no prior in-sample year for B


def yearly_best_factors(weeks_base, spy, vix, irx):
    best = {}
    for year in YEARS:
        yearly_weeks = weeks_base[weeks_base["entry_date"].dt.year == year]
        results = run_sweep(yearly_weeks, spy, vix, irx)
        row = best_practical_factor(results)
        best[year] = row["stop_loss_factor"] if row is not None else K_A
    return best


def trade_year(weeks_base, spy, vix, irx, year, k):
    yearly_weeks = weeks_base[weeks_base["entry_date"].dt.year == year]
    weeks = strategy.add_stop_bounds(yearly_weeks, stop_loss_factor=k)
    return backtest.run(weeks, spy, vix, irx)


def main():
    raw = data.get_all(START, END)
    weeks_base = strategy.generate_weeks(raw["spy"], raw["vix"], raw["irx"])
    weeks_base["entry_date"] = pd.to_datetime(weeks_base["entry_date"])

    prior_year_best = yearly_best_factors(weeks_base, raw["spy"], raw["vix"], raw["irx"])

    rows = []
    trades_a_all, trades_b_all = [], []
    for year in TEST_YEARS:
        k_b = prior_year_best[year - 1]

        trades_a = trade_year(weeks_base, raw["spy"], raw["vix"], raw["irx"], year, K_A)
        trades_b = trade_year(weeks_base, raw["spy"], raw["vix"], raw["irx"], year, k_b)
        trades_a_all.append(trades_a)
        trades_b_all.append(trades_b)

        m_a = metrics.compute(trades_a)
        m_b = metrics.compute(trades_b)
        rows.append(
            {
                "year": year,
                "k_A": K_A,
                "pnl_A": m_a["total_pnl"],
                "sharpe_A": m_a["sharpe_ratio"],
                "k_B_prev_year": k_b,
                "pnl_B": m_b["total_pnl"],
                "sharpe_B": m_b["sharpe_ratio"],
            }
        )

    yearly = pd.DataFrame(rows).set_index("year")

    combined_a = metrics.compute(pd.concat(trades_a_all, ignore_index=True))
    combined_b = metrics.compute(pd.concat(trades_b_all, ignore_index=True))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    yearly.to_csv(OUT_DIR / "walk_forward_by_year.csv")
    pd.DataFrame([{"approach": "A (k=0.85 fixed)", **combined_a}, {"approach": "B (prior-year k)", **combined_b}]).to_csv(
        OUT_DIR / "walk_forward_combined.csv", index=False
    )

    plot(yearly, OUT_DIR / "walk_forward_plot.png")

    print(yearly.to_string())
    print()
    print("combined 2021-2025:")
    print(f"  A (k=0.85 fixed):  total_pnl={combined_a['total_pnl']:.2f}  sharpe={combined_a['sharpe_ratio']:.3f}")
    print(f"  B (prior-year k):  total_pnl={combined_b['total_pnl']:.2f}  sharpe={combined_b['sharpe_ratio']:.3f}")


def plot(yearly, out_path):
    fig, axes = plt.subplots(2, 1, figsize=(8, 8), sharex=True)
    fig.suptitle("Walk-forward: fixed k=0.85 vs. prior-year-optimal k")

    x = range(len(yearly))
    width = 0.35

    axes[0].bar([i - width / 2 for i in x], yearly["pnl_A"], width, label="A: k=0.85 fixed", color=ACCENT)
    axes[0].bar([i + width / 2 for i in x], yearly["pnl_B"], width, label="B: prior-year k", color=PEAK)
    axes[0].set_title("Total P&L by year", loc="left", fontsize=10)
    axes[0].yaxis.set_major_formatter(lambda v, _: f"${v:,.0f}")
    axes[0].legend(frameon=False, fontsize=9)

    axes[1].bar([i - width / 2 for i in x], yearly["sharpe_A"], width, label="A: k=0.85 fixed", color=ACCENT)
    axes[1].bar([i + width / 2 for i in x], yearly["sharpe_B"], width, label="B: prior-year k", color=PEAK)
    axes[1].set_title("Sharpe ratio by year", loc="left", fontsize=10)

    for ax in axes:
        ax.set_xticks(list(x))
        ax.set_xticklabels(yearly.index)
        ax.grid(color=GRID, linewidth=0.8, axis="y")
        ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)


if __name__ == "__main__":
    main()
